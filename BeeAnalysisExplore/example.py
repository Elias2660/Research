#! /usr/bin/python3

"""
Utility functions and classes for video processing
"""

import cv2
import math
import random
import torch


def vidSamplingCommonCrop(
    height, width, out_height, out_width, scale, x_offset, y_offset
):
    """
    Return the common cropping parameters used in dataprep and annotations.

    Arguments:
        height     (int): Height of the video
        width      (int): Width of the video
        out_height (int): Height of the output patch
        out_width  (int): Width of the output patch
        scale    (float): Scale applied to the original video
        x_offset   (int): x offset of the crop (after scaling)
        y_offset   (int): y offset of the crop (after scaling)
    Returns:
        out_width, out_height, crop_x, crop_y
    """

    if out_width is None:
        out_width = math.floor(width * scale)
    if out_height is None:
        out_height = math.floor(height * scale)

    crop_x = math.floor((width * scale - out_width) / 2 + x_offset)
    crop_y = math.floor((height * scale - out_height) / 2 + y_offset)

    return out_width, out_height, crop_x, crop_y


def getVideoInfo(video_path):
    """
    Get the width, height, and the total number of frames in a video using OpenCV.

    Arguments:
        video_path (str): The path to the video file.
    Returns:
        int: Width
        int: Height
        int: The total number of frames.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Error opening video file {}".format(video_path))

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    cap.release()  # It's important to release the video capture object

    return width, height, total_frames


class VideoSampler:

    def __init__(
        self,
        video_path,
        num_samples,
        frames_per_sample,
        frame_interval,
        out_width=None,
        out_height=None,
        crop_noise=0,
        scale=1.0,
        crop_x_offset=0,
        crop_y_offset=0,
        channels=3,
        begin_frame=None,
        end_frame=None,
        bg_subtract="none",
        normalize=True,
    ):
        """
        Samples have no overlaps. For example, a 10 second video at 30fps has 300 samples of 1
        frame, 150 samples of 2 frames with a frame interval of 0, or 100 samples of 2 frames with a
        frame interval of 1.
        Arguments:
            video_path  (str): Path to the video.
            num_samples (int): Number of samples yielded from VideoSampler's iterator.
            frames_per_sample (int):  Number of frames in each sample.
            frame_interval    (int): Number of frames to skip between each sampled frame.
            out_width     (int): Width of output images, or the original width if None.
            out_height    (int): Height of output images, or the original height if None.
            crop_noise    (int): Noise to add to the crop location (in both x and y dimensions)
            scale       (float): Scale factor of each dimension
            crop_x_offset (int): x offset of crop, in pixels, from the original image
            crop_y_offset (int): y offset of crop, in pixels, from the original image
            channels      (int): Numbers of channels (3 for RGB or 1 luminance/Y/grayscale/whatever)
            begin_frame   (int): First frame to possibly sample.
            end_frame     (int): Final frame to possibly sample.
            bg_subtract   (str): Type of background subtraction to use (mog2 or knn), or none.
            normalize    (bool): True to normalize image channels (done independently)
        """
        self.path = video_path
        self.num_samples = num_samples
        self.frames_per_sample = frames_per_sample
        self.frame_interval = frame_interval
        self.channels = channels
        self.scale = scale
        self.normalize = normalize

        # Background subtraction will require openCV if requested.
        self.bg_subtractor = None
        if "none" != bg_subtract:
            from cv2 import (
                createBackgroundSubtractorMOG2,
                createBackgroundSubtractorKNN,
            )

            if "mog2" == bg_subtract:
                self.bg_subtractor = createBackgroundSubtractorMOG2()
            elif "knn" == bg_subtract:
                self.bg_subtractor = createBackgroundSubtractorKNN()

        print(f"Processing {video_path}")
        # Probe the video to find out some metainformation

        self.width, self.height, self.total_frames = getVideoInfo(video_path)

        if out_width is None or out_height is None:
            self.crop_noise = 0
        else:
            self.crop_noise = crop_noise

        self.out_width, self.out_height, self.crop_x, self.crop_y = (
            vidSamplingCommonCrop(
                self.height,
                self.width,
                out_height,
                out_width,
                self.scale,
                crop_x_offset,
                crop_y_offset,
            )
        )

        if begin_frame is None:
            self.begin_frame = 1
        else:
            self.begin_frame = int(begin_frame)

        if end_frame is None:
            self.end_frame = self.total_frames
        else:
            # Don't attempt to sample more frames than there exist.
            self.end_frame = min(int(end_frame), self.total_frames)
        # Don't attempt to make more samples that the number of frames that will be sampled.
        # Remember that the frames in frame_interval aren't used but are still skipped along with
        # each sample.
        self.sample_span = (
            self.frames_per_sample + (self.frames_per_sample - 1) * self.frame_interval
        )
        self.available_samples = (
            self.end_frame - (self.sample_span - 1) - self.begin_frame
        ) // self.sample_span
        self.num_samples = min(self.available_samples, self.num_samples)
        print(f"Video begin and end frames are {self.begin_frame} and {self.end_frame}")
        print(
            f"Video has {self.available_samples} available samples of size {self.sample_span} and {self.num_samples} will be sampled"
        )

    def setSeed(self, seed):
        """Set the seed used for sample generation in the iterator."""
        self.seed = seed

    def __iter__(self):
        """An iterator that yields frames using OpenCV for video processing."""
        # Open the video file
        cap = cv2.VideoCapture(self.path)
        if not cap.isOpened():
            raise IOError("Could not open video file.")

        # Determine frames to sample
        target_samples = [
            (self.begin_frame - 1) + x * self.sample_span
            for x in sorted(
                random.sample(
                    population=range(self.available_samples), k=self.num_samples
                )
            )
        ]

        frame_count = 0
        for target_sample in target_samples:
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_sample)
            partial_sample = []
            sample_frames = []
            while len(partial_sample) < self.frames_per_sample:
                ret, frame = cap.read()
                if not ret:
                    break  # End of video or error

                frame_count += 1

                # Apply background subtraction if needed
                if self.bg_subtractor is not None:
                    fgmask = self.bg_subtractor.apply(frame)
                    frame = cv2.bitwise_and(frame, frame, mask=fgmask)

                # Convert frame to the desired format (RGB or grayscale)
                if self.channels == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                else:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Scale, Crop, and Normalize the frame if necessary
                if self.scale != 1.0:
                    frame = cv2.resize(
                        frame,
                        None,
                        fx=self.scale,
                        fy=self.scale,
                        interpolation=cv2.INTER_AREA,
                    )

                # Add noise to crop location if needed
                crop_x = random.randint(0, max(0, frame.shape[1] - self.out_width))
                crop_y = random.randint(0, max(0, frame.shape[0] - self.out_height))
                frame = frame[
                    crop_y : crop_y + self.out_height, crop_x : crop_x + self.out_width
                ]

                if self.normalize:
                    frame = cv2.normalize(
                        frame,
                        None,
                        alpha=0,
                        beta=1,
                        norm_type=cv2.NORM_MINMAX,
                        dtype=cv2.CV_32F,
                    )

                # Convert to PyTorch tensor
                frame_tensor = (
                    torch.from_numpy(frame).permute(2, 0, 1).float()
                    if self.channels == 3
                    else torch.from_numpy(frame).unsqueeze(0).float()
                )
                partial_sample.append(frame_tensor)
                sample_frames.append(frame_count)

                # Skip frames if necessary
                for _ in range(self.frame_interval):
                    ret = cap.grab()
                    if not ret:
                        break

            if partial_sample:
                if len(partial_sample) == 1:
                    yield partial_sample[0], self.path, tuple(sample_frames)
                else:
                    yield torch.cat(partial_sample, dim=0), self.path, tuple(
                        sample_frames
                    )

        cap.release()
