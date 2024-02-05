import os
import cv2

"""
There are multiple instances where one will have to convert ther video


? FIRST INSTANCE
        process1 = (
            ffmpeg
            .input(video_path)
            .output('pipe:', format='rawvideo', pix_fmt='gray')
            #.output('pipe:', format='rawvideo', pix_fmt='yuv420p')
            .run_async(pipe_stdout=True, quiet=True)
        )
        frame = 0
        while True:
            # Using pix_fmt='gray' we should get a single channel of 8 bits per pixel
            in_bytes = process1.stdout.read(width * height)
            if in_bytes:
                frame += 1
            else:
                process1.wait()
                break
        total_frames = frame
    return width, height, total_frames

? Second Instance
process1 = (
            ffmpeg
            .input(self.path)
            .trim(start_frame=1, end_frame=400)
            .filter('scale', self.scale*self.width, -1)
            .filter('crop', out_w=in_width, out_h=in_height, x=self.crop_x, y=self.crop_y)
        )
        if self.normalize:
            process1 = process1.filter('normalize', independence=1.0)
            process1 = (
                process1
                .output('pipe:', format='rawvideo', pix_fmt=pix_fmt)
                .run_async(pipe_stdout=True, quiet=True)
            )
            in_bytes = process1.stdout.read(in_width * in_height * self.channels)
"""


def processVideo(IN_PATH, OUT_PATH):
    """
    There are multiple steops this function
    1. Read in the video file
        - scaling to
    2. Apply a scale effect
    3. Crop the video file
    """
