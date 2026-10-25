# iPhone HEIC to JPEG Converter

This tool recursively converts all iPhone HEIC images in a folder (and its subfolders) to JPEG format, saving them in a specified output folder while preserving the directory structure. EXIF metadata is kept and orientation is applied.

## Requirements
- Python 3.x
- pillow
- pillow-heif

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python heic_to_jpeg.py <input_folder> <output_folder> [--quality 1-100] [--overwrite] [--workers N]
```

- `<input_folder>`: Path to the folder containing HEIC images (can include subfolders)
- `<output_folder>`: Path to the folder where JPEG images will be saved
- `--quality`: JPEG quality (default: 90)
- `--overwrite`: Overwrite existing JPEG files (default: existing files are skipped)
- `--workers`: Number of parallel conversions (default: 1)

Files whose output names would collide (e.g. `a.heic` and `a.HEIC`) are saved as `a.jpg` and `a_1.jpg`. A summary is printed at the end, and the exit code is 1 if any file failed.

Example:
```bash
python heic_to_jpeg.py /path/to/heic_images /path/to/jpeg_output --quality 85 --workers 4
```

## Web app (Vercel)

`index.html` is an upload page and `api/convert.py` is a Python serverless function that converts the uploaded image to JPG (HEIC, PNG, WebP, etc.) and returns it for download.

Deploy: import this repository in Vercel (no build settings needed), or run `vercel` from the project folder. Locally, `vercel dev` serves the page and the API.

Vercel limits request bodies to 4.5 MB, so uploads are capped at about 4 MB.

## Tests
```bash
pip install -r requirements-dev.txt
pytest
```
