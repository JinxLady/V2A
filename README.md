# Video to MP3 Converter
A Python-based command-line tool to extract audio from video files and convert it to MP3 format. The tool supports batch processing, multithreading for faster execution, and real-time progress tracking.
## Features
- Extract audio from video files and convert it to high-quality MP3 format.
- Support for batch conversion of multiple video files in a folder.
- Multithreaded processing for faster performance.
- Handles various video formats such as MP4, MKV, AVI, MOV, and WEBM.
- Displays a progress bar for each video being processed.

## Requirements
Before running the tool, ensure the following dependencies are installed.
### Dependencies:
1. Python 3.7 or higher
2. Required Python libraries:
    - `tqdm`
3. **FFmpeg Tool**:
    - FFmpeg must be installed on your system and added to the system's PATH.

To install the Python dependencies, run:
``` bash
pip install -r requirements.txt
```
To install FFmpeg:
- **Ubuntu/Debian**:
``` bash
    sudo apt update
    sudo apt install ffmpeg
```
- **MacOS** (with Homebrew):
``` bash
    brew install ffmpeg
```
## Installation
1. Clone this repository:
``` bash
    git clone <repository_link>
    cd <repository_folder>
```
1. Install the Python dependencies:
``` bash
    pip install -r requirements.txt
```
1. Ensure FFmpeg is installed and accessible from the command line. To verify:
``` bash
    ffmpeg -version
```
## Usage
Run the script from the command line. The tool supports both single video file conversion and batch processing of all files in a folder.
### Basic Syntax:
``` bash
python main.py <input_path> [-o OUTPUT_FOLDER] [-t THREADS]
```
### Arguments:
- `input`: The path to a video file or folder containing video files.
- `-o, --output`: (Optional) Path to the output folder. If not provided, the output will be saved in the same location as the input.
- `-t, --threads`: (Optional) Number of threads to use for processing. The default is `4`.

### Examples
#### Convert a single video file
``` bash
python main.py ./videos/video1.mp4 -o ./output
```
- Converts `video1.mp4` to MP3 and saves it in the `./output` folder.

#### Batch convert all videos in a folder
``` bash
python main.py ./videos -o ./output
```
- Converts all videos in the `./videos` folder to MP3 and saves the outputs in the `./output` folder.

#### Use 8 threads for faster processing
``` bash
python main.py ./videos -o ./output -t 8
```
- Converts all videos in the `./videos` folder using 8 threads for better performance.

## Supported Video Formats
The following video formats are supported:
- MP4
- MKV
- AVI
- MOV
- WEBM

## Error Handling and Interruptions
- If the script is interrupted (e.g., with `Ctrl+C`), it will:
    - Cancel any ongoing tasks.
    - Clean up partially created MP3 files to avoid clutter.

- If a specific video fails to convert, the error will be logged, and the script will continue processing other files.