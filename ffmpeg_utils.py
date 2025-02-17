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

def convert_to_mp3(input_path, output_path, quality="vbr", bitrate_or_level="2"):
    if os.path.exists(output_path):
        print(f"Target exists: {output_path}")
        return

    audio_bitrate = None
    sample_rate = None
    if input_path.endswith(".webm"):
        try:
            probe_result = subprocess.run(
                [
                    "ffprobe", "-i", input_path, "-show_streams", "-select_streams", "a",
                    "-loglevel", "quiet", "-of", "json"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            import json
            streams = json.loads(probe_result.stdout).get("streams", [])
            if streams:
                audio_bitrate = streams[0].get("bit_rate")
                sample_rate = streams[0].get("sample_rate")
        except Exception as e:
            print("Could not retrieve audio properties from webm file.")
            print(e)

    use_source_bit_rate = bool(audio_bitrate and sample_rate)
    duration = get_video_duration(input_path)
    if duration is None:
        print(f"Get video duration failed: {input_path}")
        return

    short_description = "Processing: " + right_shorten_text(input_path, max_length=50)

    audio_quality_args = []
    if input_path.endswith(".webm") and use_source_bit_rate:
        audio_quality_args += ["-b:a", f"{int(audio_bitrate) // 1000}k", "-ar", sample_rate]
    elif quality == "vbr":
        audio_quality_args = ["-q:a", bitrate_or_level]
    elif quality == "cbr":
        audio_quality_args = ["-b:a", bitrate_or_level]
    else:
        print(f"Invalid quality parameter: {quality}")
        return

    with tqdm(total=duration, unit="s", desc=short_description) as pbar:
        process = None
        try:
            process = subprocess.Popen(
                [
                    "ffmpeg",
                    "-i", input_path,
                    "-vn",
                    "-c:a", "libmp3lame",
                ]
                + audio_quality_args
                + [output_path],
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
