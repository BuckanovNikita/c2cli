"""c2cli - Computer Vision Format Converter."""

import argparse
import sys
from pathlib import Path

from .converter import Converter
from .models import Dataset
from .formats import (
    COCOReader, COCOWriter,
    YOLOReader, YOLOWriter,
    PascalVOCReader, PascalVOCWriter
)

__version__ = "0.1.0"

__all__ = [
    "Converter",
    "Dataset",
    "COCOReader", "COCOWriter",
    "YOLOReader", "YOLOWriter",
    "PascalVOCReader", "PascalVOCWriter",
]


def main() -> None:
    """CLI entry point for c2cli."""
    parser = argparse.ArgumentParser(
        description="Convert between computer vision annotation formats (COCO, YOLO, Pascal VOC)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert COCO to YOLO
  c2cli coco yolo --input annotations.json --output labels/ --classes classes.txt

  # Convert YOLO to Pascal VOC
  c2cli yolo voc --input labels/ --output voc_annotations/ \\
    --images images/ --classes classes.txt

  # Convert Pascal VOC to COCO
  c2cli voc coco --input voc_annotations/ --output annotations.json
        """
    )

    parser.add_argument('source', choices=['coco', 'yolo', 'voc'],
                       help='Source annotation format')
    parser.add_argument('target', choices=['coco', 'yolo', 'voc'],
                       help='Target annotation format')
    parser.add_argument('-i', '--input', required=True,
                       help='Input path (file for COCO, directory for YOLO/VOC)')
    parser.add_argument('-o', '--output', required=True,
                       help='Output path (file for COCO, directory for YOLO/VOC)')

    # YOLO-specific arguments
    parser.add_argument('--images', help='Images directory (required for YOLO as source)')
    parser.add_argument('--classes', help='Classes file path (required for YOLO)')
    parser.add_argument('--image-ext', default='.jpg',
                       help='Image file extension for YOLO (default: .jpg)')

    parser.add_argument('-v', '--version', action='version',
                       version=f'c2cli {__version__}')

    args = parser.parse_args()

    # Validate format-specific requirements
    if args.source == 'yolo' and (not args.images or not args.classes):
        parser.error("YOLO source format requires --images and --classes arguments")

    if args.target == 'yolo' and not args.classes:
        # Default classes file location
        args.classes = str(Path(args.output).parent / 'classes.txt')

    # Prepare kwargs
    kwargs = {}
    if args.images:
        kwargs['images_dir'] = args.images
    if args.classes:
        kwargs['classes_file'] = args.classes
        kwargs['output_classes_file'] = args.classes
    if args.image_ext:
        kwargs['image_ext'] = args.image_ext

    try:
        converter = Converter()
        print(f"Converting {args.source.upper()} -> {args.target.upper()}...")
        print(f"Input: {args.input}")
        print(f"Output: {args.output}")

        dataset = converter.convert(
            source_format=args.source,
            target_format=args.target,
            source_path=args.input,
            target_path=args.output,
            **kwargs
        )

        print(f"\nConversion completed successfully!")
        print(f"Images: {len(dataset.images)}")
        print(f"Categories: {len(dataset.categories)}")
        total_annotations = sum(len(img.annotations) for img in dataset.images)
        print(f"Total annotations: {total_annotations}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
