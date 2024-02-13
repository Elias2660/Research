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


def turn_to_raw_grayscale(file_in, out_file, codec):
    """
    to replace
            process1 = (
            ffmpeg
            .input(video_path)
            .output('pipe:', format='rawvideo', pix_fmt='gray')
            #.output('pipe:', format='rawvideo', pix_fmt='yuv420p')
            .run_async(pipe_stdout=True, quiet=True)



        )
        ! need to convert this shit so that it reads to the in_bytes
    """
    count = 0
    cap = cv2.VideoCapture(file_in)
    height, width = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(
        cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    )
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*codec)
    video_writer = cv2.VideoWriter(out_file, fourcc, fps, (width, height))
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        print(f"Converting Frame {count}", end="\r")
        count += 1
        gray = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
        video_writer.write(gray)
    print()
    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()


turn_to_raw_grayscale(
    os.path.join("converted.mp4"), os.path.join("last_test.avi"), codec="yuv4"
)


def filter_trip_scale(
    in_path,
    out_path,
    width,
    height,
    in_width,
    in_height,
    out_w,
    out_h,
    crop_x,
    crop_y,
    x,
    y,
    scale,
    normalize,
    start_frame=1,
    end_frame=400,
    codec="yuv4",
):
    """
     Designed to replace the following:

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
    cap = cv2.videoCauture(in_path)
    out = cv2.VideoWriter(
        out_path,
        cv2.VideoWriter_fourcc(*codec),
        cap.get(cv2.CAP_PROP_FPS),
        (out_w, out_h),
    )
    count = 0

    while cap.isOpened():
        frame, ret = cap.read()
        if not ret:
            break
        if count < 400:
            frame = cv2.resize(frame, (width * scale, height))
            frame = frame[crop_y : crop_y + in_height, crop_x : crop_x + in_width]
            count += 1

            if normalize:
                frame = cv2.normalize(
                    frame,
                    None,
                    alpha=0,
                    beta=1,
                    norm_type=cv2.NORM_MINMAX,
                    dtype=cv2.CV_32F,
                )

            out.write(frame)

        else:
            break
    cap.release()
    out.release()
    
    
# given the fact that we're writing to a video file, we don't use 