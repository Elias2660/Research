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


def runThroughVideo(IN_PATH, OUT_PATH):
    """
    This will be the simple function to make sure everything could work here
    """
    cap = cv2.VideoCapture(IN_PATH)
    count = 0
    while True:
        ret, frame = cap.read()
        count += 1
        print(f"Converting Frame {count}", end="\r")
        if not ret:
            break
        ## This is where everything shoule happen
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


# runThroughVideo("./output.mp4", "./output.mp4")


def turn_to_raw_grayscale(file_in, out_file, codec='avc1'):
    """
    to replace
            process1 = (
            ffmpeg
            .input(video_path)
            .output('pipe:', format='rawvideo', pix_fmt='gray')
            #.output('pipe:', format='rawvideo', pix_fmt='yuv420p')
            .run_async(pipe_stdout=True, quiet=True)
        )
    """
    count = 0
    cap = cv2.VideoCapture(file_in)
    height, width = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    video_writer = cv2.VideoWriter(out_file, fourcc, fps, (width, height))
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        print(f"Converting Frame {count}", end="\r")
        count += 1
        video_writer.write(frame)
    print();
    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()

turn_to_raw_grayscale(os.path.join("converted.mp4"),os.path.join("troll.mp4"))