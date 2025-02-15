import os
import subprocess
import re
from tqdm import tqdm
import sys


def right_shorten_text(text, max_length, ellipsis="..."):
    if len(text) <= max_length:
        return text
    ellipsis_length = len(ellipsis)
    tail_length = max_length - ellipsis_length
    return f"{ellipsis}{text[-tail_length:]}"


def parse_progress(text):
    progress = re.search(r"time=(\d+:\d+:\d+\.\d+)", text)
    if progress:
        time_str = progress.group(1)
        h, m, s = map(float, time_str.split(":"))
        return h * 3600 + m * 60 + s
    return None


def get_video_duration(input_path):
    try:
        result = subprocess.run(
            ["ffprobe", "-i", input_path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Get video duration failed: {input_path}")
        print(e)
        return None


def convert_to_mp3_with_gpu(input_path, output_path):
    if os.path.exists(output_path):
        print(f"Target exists: {output_path}")
        return

    duration = get_video_duration(input_path)
    if duration is None:
        print(f"Get video duration failed: {input_path}")
        return

    short_description = "Processing: " + right_shorten_text(input_path, max_length=50)

    with tqdm(total=duration, unit="s", desc=short_description) as pbar:
        process = None
        try:
            process = subprocess.Popen(
                [
                    "ffmpeg",
                    "-i", input_path,
                    "-vn",
                    "-c:a", "libmp3lame",
                    "-b:a", "320k",
                    output_path
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            while True:
                output = process.stderr.readline()
                if output == "" and process.poll() is not None:
                    break
                sys.stdout.flush()
                progress = parse_progress(output)
                if progress:
                    pbar.n = progress
                    pbar.refresh()

            process.wait()

            if process.returncode == 0:
                print(f"Completed: {input_path} -> {output_path}")
            else:
                print(f"Failed: {input_path}")
                print(process.stderr.read())
        except Exception as e:
            print(f"Error: {input_path} : {e}")
        finally:
            pbar.close()
