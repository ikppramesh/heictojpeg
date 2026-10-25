import os
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageOps
import pillow_heif

pillow_heif.register_heif_opener()

HEIC_EXTENSIONS = ('.heic', '.heif')


def find_jobs(input_folder, output_folder):
    """Return a list of (input_path, output_path) pairs.

    Subfolder structure is preserved. Output names that would collide within
    the same run (e.g. a.heic and a.HEIC) get a numeric suffix.
    """
    jobs = []
    claimed = set()
    for root, _, files in os.walk(input_folder):
        rel_path = os.path.relpath(root, input_folder)
        output_dir = os.path.normpath(os.path.join(output_folder, rel_path))
        for file in sorted(files):
            if not file.lower().endswith(HEIC_EXTENSIONS):
                continue
            stem = os.path.splitext(file)[0]
            output_path = os.path.join(output_dir, stem + '.jpg')
            counter = 1
            while output_path.lower() in claimed:
                output_path = os.path.join(output_dir, f"{stem}_{counter}.jpg")
                counter += 1
            claimed.add(output_path.lower())
            jobs.append((os.path.join(root, file), output_path))
    return jobs


def convert_file(input_path, output_path, quality=90, overwrite=False):
    """Convert one file. Returns 'converted' or 'skipped'; raises on failure."""
    if os.path.exists(output_path) and not overwrite:
        return 'skipped'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with Image.open(input_path) as image:
        exif = image.info.get("exif")
        # Bake the orientation into the pixels so the rotation is not lost
        image = ImageOps.exif_transpose(image)
        if image.mode != "RGB":
            image = image.convert("RGB")
        save_kwargs = {"format": "JPEG", "quality": quality}
        if exif:
            save_kwargs["exif"] = exif
        image.save(output_path, **save_kwargs)
    return 'converted'


def _run_job(job, quality, overwrite):
    input_path, output_path = job
    try:
        status = convert_file(input_path, output_path, quality, overwrite)
    except Exception as e:
        print(f"Failed to convert {input_path}: {e}")
        return 'failed'
    if status == 'skipped':
        print(f"Skipped (exists): {output_path}")
    else:
        print(f"Converted: {input_path} -> {output_path}")
    return status


def convert_heic_to_jpeg(input_folder, output_folder, quality=90, overwrite=False, workers=1):
    """Convert all HEIC images; returns a dict of converted/skipped/failed counts."""
    jobs = find_jobs(input_folder, output_folder)
    counts = {'converted': 0, 'skipped': 0, 'failed': 0}
    if workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = pool.map(lambda j: _run_job(j, quality, overwrite), jobs)
            for status in results:
                counts[status] += 1
    else:
        for job in jobs:
            counts[_run_job(job, quality, overwrite)] += 1
    return counts


def main():
    parser = argparse.ArgumentParser(description="Convert all HEIC images in a folder (recursively) to JPEG.")
    parser.add_argument('input_folder', help='Path to the input folder containing HEIC images')
    parser.add_argument('output_folder', help='Path to the output folder for JPEG images')
    parser.add_argument('--quality', type=int, default=90, choices=range(1, 101),
                        metavar='1-100', help='JPEG quality (default: 90)')
    parser.add_argument('--overwrite', action='store_true',
                        help='Overwrite existing JPEG files (default: skip them)')
    parser.add_argument('--workers', type=int, default=1,
                        help='Number of parallel conversions (default: 1)')
    args = parser.parse_args()

    if not os.path.isdir(args.input_folder):
        print(f"Input folder does not exist: {args.input_folder}")
        sys.exit(1)
    os.makedirs(args.output_folder, exist_ok=True)
    counts = convert_heic_to_jpeg(args.input_folder, args.output_folder,
                                  quality=args.quality, overwrite=args.overwrite,
                                  workers=max(1, args.workers))
    print(f"Done: {counts['converted']} converted, {counts['skipped']} skipped, {counts['failed']} failed")
    if counts['failed']:
        sys.exit(1)


if __name__ == "__main__":
    main()
