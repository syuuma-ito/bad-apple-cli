import argparse
import os
import shutil
import time

import cv2

ASCII_CHARS = r" .-:=+*%@#"
CLEAR_CMD = "cls" if os.name == "nt" else "clear"
window_height = shutil.get_terminal_size().lines
window_width = shutil.get_terminal_size().columns

video_path = "./video/Bad_Apple.mp4"


def clear_screen():
    os.system(CLEAR_CMD)


def frame_to_ascii(frame, width, height, CHARS):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized_frame = cv2.resize(gray, (width, height))
    return "\n".join(
        "".join(CHARS[int(pixel) * len(CHARS) // 256] for pixel in row)
        for row in resized_frame
    )


def calc_sleep(start, frame_idx, fps):
    target = frame_idx / fps
    return target - (time.time() - start)


def play_video_in_ascii(args):
    global window_height, window_width

    if args.chars:
        CHARS = args.chars[::-1] if args.invert else args.chars
    else:
        CHARS = ASCII_CHARS[::-1] if args.invert else ASCII_CHARS

    clear_screen()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"Could not open video {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    start = time.time()

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            idx = cap.get(cv2.CAP_PROP_POS_FRAMES)
            to_sleep = calc_sleep(start, idx, fps)
            if to_sleep > 0:
                time.sleep(to_sleep)

            window_height_ = shutil.get_terminal_size().lines
            window_width_ = shutil.get_terminal_size().columns
            if window_width_ != window_width:
                window_width = window_width_
                clear_screen()
            if window_height_ != window_height:
                window_height = window_height_
                clear_screen()

            ratio = 2.8
            height = window_height
            width = int(height * ratio)

            if width > window_width:
                width = window_width
                height = int(width / ratio)

            ascii_frame = frame_to_ascii(frame, width, height, CHARS)
            print("\033[H" + ascii_frame, end="", flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--invert",
        "-i",
        help="黒と白を反転させる",
        action="store_true",
    )
    parser.add_argument(
        "--chars",
        help="使うアスキー文字列を指定する",
        type=str,
        default=None,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    play_video_in_ascii(args)


if __name__ == "__main__":
    main()
