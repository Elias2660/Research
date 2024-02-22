import cv2
import numpy as np
import os
from cv2 import (bitwise_and)

class VideoSampler:

    def __init__(self, video_path, num_samples, frames_per_sample, frame_interval,
            out_width=None, out_height=None, crop_noise=0, scale=1.0, crop_x_offset=0,
             crop_y_offset=0, channels=3, begin_frame=None, end_frame=None,
             bg_subtract='none', normalize=True):
        self.path = video_path
        self.num_samples = num_samples
        self.frames_per_sample = frames_per_sample
        self.frame_interval = frame_interval
        self.channels = channels
        self.scale = scale
        self.normalize = normalize

        # Background subtraction will require openCV if requested.
        self.bg_subtractor = None
        if ('none' != bg_subtract):
            from cv2 import (createBackgroundSubtractorMOG2,
                             createBackgroundSubtractorKNN)
            if 'mog2' == bg_subtract:
                self.bg_subtractor = createBackgroundSubtractorMOG2()
            elif 'knn' == bg_subtract:
                self.bg_subtractor = createBackgroundSubtractorKNN()

        print(f"Processing {video_path}")
        # Probe the video to find out some metainformation

        self.width, self.height, self.total_frames = getVideoInfo(video_path)

        if out_width is None or out_height is None:
            self.crop_noise = 0
        else:
            self.crop_noise = crop_noise

        self.out_width, self.out_height, self.crop_x, self.crop_y = vidSamplingCommonCrop(
            self.height, self.width, out_height, out_width, self.scale, crop_x_offset, crop_y_offset)

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
        self.sample_span = self.frames_per_sample + (self.frames_per_sample - 1) * self.frame_interval
        self.available_samples = (self.end_frame - (self.sample_span - 1) - self.begin_frame)//self.sample_span
        self.num_samples = min(self.available_samples, self.num_samples)
        print(f"Video begin and end frames are {self.begin_frame} and {self.end_frame}")
        print(f"Video has {self.available_samples} available samples of size {self.sample_span} and {self.num_samples} will be sampled")


def __iter__(self):    
    target_samples = [(self.begin_frame - 1) + x * self.sample_span for x in sorted(random.sample(
    population=range(self.available_samples), k=self.num_samples))]
    
    
    if 3 == self.channels:
        pix_fmt='rgb24'
    else:
        pix_fmt='gray'
    in_width = self.out_width + 2 * self.crop_noise
    in_height = self.out_height + 2 * self.crop_noise
    
    
    cap = cv2.VideoCapture(self.path)
    count = 0
    while cap.isOpened():
        
        ret, frame = cap.read()
        count += 1
        
        if (self.bg_subtractor is not None):
            if count < 400:
                frame = cv2.resize(frame, (self.width * self.scale, self.height))
                frame = frame[self.crop_y : self.crop_y + in_height, self.crop_x : self.crop_x + in_width]
                count += 1
            

            
            
        
        if not ret:
            break
        
            
    