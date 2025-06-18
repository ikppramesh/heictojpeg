# iPhone HEIC to JPEG Converter

This tool recursively converts all iPhone HEIC images in a folder (and its subfolders) to JPEG format, saving them in a specified output folder while preserving the directory structure.

## Requirements
- Python 3.x
- pillow
- pyheif

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python heic_to_jpeg.py <input_folder> <output_folder>
```

- `<input_folder>`: Path to the folder containing HEIC images (can include subfolders)
- `<output_folder>`: Path to the folder where JPEG images will be saved

Example:
```bash
python heic_to_jpeg.py /path/to/heic_images /path/to/jpeg_output
``` 