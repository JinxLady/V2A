import os
import sys
import signal
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import ffmpeg_utils

executor = None
ongoing_tasks = []
bitrate_or_level_map = {
    "vbr" : {"high" : "0", "mid" : "2", "low" : "5"},
    "cbr" : {"high" : "320k", "mid" : "192k", "low" : "128k"}
}

def handle_interrupt(signal, frame):
    if executor is not None:
        try:
            executor.shutdown(wait=False, cancel_futures=True)
        except Exception as e:
            print(f"Stop task(s) failed: {e}")

    for output_file in ongoing_tasks:
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except Exception as e:
                print(f"Clean cache failed: {output_file}: {e}")

    sys.exit(1)


def safe_convert(input_file, output_file, quality="vbr", bitrate_or_level="high"):
    ongoing_tasks.append(output_file)
    try:
        ffmpeg_utils.convert_to_mp3(input_file, output_file, quality=quality, bitrate_or_level=bitrate_or_level_map[quality][bitrate_or_level])
    except Exception as e:
        print(f"Task failed: {input_file}: {e}")
        if os.path.exists(output_file):
            os.remove(output_file)
        raise
    finally:
        ongoing_tasks.remove(output_file)



def process_folder_multithreaded(input_folder, output_folder=None, max_workers=4):
    global executor
    if not os.path.exists(input_folder):
        print(f"Folder not found: {input_folder}")
        return

    if output_folder is None:
        output_folder = input_folder

    os.makedirs(output_folder, exist_ok=True)

    tasks = []

    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith((".mp4", ".mkv", ".avi", ".mov", ".webm")):
                input_file = os.path.join(root, file)
                output_file = os.path.join(output_folder, os.path.splitext(file)[0] + ".mp3")

                if os.path.exists(output_file):
                    print(f"Target exists: {output_file}")
                    continue

                tasks.append((input_file, output_file))

    executor = ThreadPoolExecutor(max_workers=max_workers)
    future_to_task = {
        executor.submit(safe_convert, input_file, output_file): (input_file, output_file)
        for input_file, output_file in tasks
    }

    try:
        for future in as_completed(future_to_task):
            input_file, output_file = future_to_task[future]
            try:
                future.result()
            except Exception as e:
                print(f"Task failed: {input_file}: {e}")
    except Exception:
        executor.shutdown(wait=False, cancel_futures=True)
        raise


def main():
    signal.signal(signal.SIGINT, handle_interrupt)

    parser = argparse.ArgumentParser(
        description="Extract audio from video files and convert them to MP3 with configurable quality settings."
    )
    parser.add_argument("input", help="Path to the input file or folder")
    parser.add_argument("-o", "--output", help="Path to the output folder (optional)", default=None)
    parser.add_argument("-t", "--threads", type=int, help="Number of threads to use (default is 4)", default=4)
    parser.add_argument("--quality", help="Audio quality mode ('vbr' or 'cbr')", default="vbr")
    parser.add_argument("--level", help="high, mid, low", default="high")

    args = parser.parse_args()

    if args.quality not in bitrate_or_level_map:
        raise ValueError(
            f"Invalid quality '{args.quality}' specified. Allowed values are: {', '.join(bitrate_or_level_map.keys())}."
        )

    if args.level not in bitrate_or_level_map[args.quality]:
        allowed_levels = ", ".join(bitrate_or_level_map[args.quality])
        raise ValueError(
            f"Invalid level '{args.level}' for quality '{args.quality}'. "
            f"Allowed values are: {allowed_levels}."
        )


    if os.path.isfile(args.input):
        input_file = args.input
        output_folder = args.output if args.output else os.path.dirname(input_file)
        output_file = os.path.join(output_folder, os.path.splitext(os.path.basename(input_file))[0] + ".mp3")

        os.makedirs(output_folder, exist_ok=True)

        if os.path.exists(output_file):
            print(f"Target exists: {output_file}")
        else:
            safe_convert(input_file, output_file)
    elif os.path.isdir(args.input):
        process_folder_multithreaded(args.input, args.output, max_workers=args.threads)
    else:
        print(f"Path invalid: {args.input}")


if __name__ == "__main__":
    main()
