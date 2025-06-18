import os
import sys
import argparse
from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()

def convert_heic_to_jpeg(input_folder, output_folder):
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith('.heic'):
                input_path = os.path.join(root, file)
                # Preserve subfolder structure
                rel_path = os.path.relpath(root, input_folder)
                output_dir = os.path.join(output_folder, rel_path)
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.splitext(file)[0] + '.jpg'
                output_path = os.path.join(output_dir, output_file)
                try:
                    image = Image.open(input_path)
                    image.save(output_path, format="JPEG")
                    print(f"Converted: {input_path} -> {output_path}")
                except Exception as e:
                    print(f"Failed to convert {input_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Convert all HEIC images in a folder (recursively) to JPEG.")
    parser.add_argument('input_folder', help='Path to the input folder containing HEIC images')
    parser.add_argument('output_folder', help='Path to the output folder for JPEG images')
    args = parser.parse_args()

    if not os.path.isdir(args.input_folder):
        print(f"Input folder does not exist: {args.input_folder}")
        sys.exit(1)
    os.makedirs(args.output_folder, exist_ok=True)
    convert_heic_to_jpeg(args.input_folder, args.output_folder)

if __name__ == "__main__":
    main() 