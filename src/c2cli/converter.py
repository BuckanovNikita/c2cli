"""Conversion engine for converting between different formats."""

from pathlib import Path
from typing import Union, Literal

from .models import Dataset
from .formats import (
    COCOReader,
    COCOWriter,
    YOLOReader,
    YOLOWriter,
    PascalVOCReader,
    PascalVOCWriter,
)

FormatType = Literal["coco", "yolo", "voc"]


class Converter:
    """Main converter class for converting between annotation formats."""

    def __init__(self):
        self.readers = {
            "coco": COCOReader,
            "yolo": YOLOReader,
            "voc": PascalVOCReader,
        }
        self.writers = {
            "coco": COCOWriter,
            "yolo": YOLOWriter,
            "voc": PascalVOCWriter,
        }

    def convert(
        self,
        source_format: FormatType,
        target_format: FormatType,
        source_path: Union[str, Path],
        target_path: Union[str, Path],
        **kwargs,
    ) -> Dataset:
        """
        Convert annotations from one format to another.

        Args:
            source_format: Source format ('coco', 'yolo', 'voc')
            target_format: Target format ('coco', 'yolo', 'voc')
            source_path: Path to source annotations
            target_path: Path to write converted annotations
            **kwargs: Additional format-specific parameters

        Returns:
            Dataset object

        Examples:
            # COCO to YOLO
            converter.convert(
                'coco', 'yolo',
                'annotations.json',
                'labels_dir',
                output_classes_file='classes.txt'
            )

            # YOLO to VOC
            converter.convert(
                'yolo', 'voc',
                labels_dir='labels',
                target_path='voc_annotations',
                images_dir='images',
                classes_file='classes.txt'
            )

            # VOC to COCO
            converter.convert(
                'voc', 'coco',
                'voc_annotations',
                'coco_annotations.json'
            )
        """
        # Read source format
        dataset = self.read(source_format, source_path, **kwargs)

        # Write target format
        self.write(target_format, dataset, target_path, **kwargs)

        return dataset

    def read(
        self, format_type: FormatType, source_path: Union[str, Path], **kwargs
    ) -> Dataset:
        """
        Read annotations from a specific format.

        Args:
            format_type: Format type ('coco', 'yolo', 'voc')
            source_path: Path to source annotations
            **kwargs: Format-specific parameters

        Returns:
            Dataset object
        """
        if format_type not in self.readers:
            raise ValueError(
                f"Unsupported format: {format_type}. "
                f"Supported formats: {list(self.readers.keys())}"
            )

        reader_class = self.readers[format_type]

        if format_type == "coco":
            return reader_class.read(source_path)

        elif format_type == "yolo":
            images_dir = kwargs.get("images_dir")
            classes_file = kwargs.get("classes_file")
            image_ext = kwargs.get("image_ext", ".jpg")

            if not images_dir or not classes_file:
                raise ValueError(
                    "YOLO format requires 'images_dir' and 'classes_file' parameters"
                )

            return reader_class.read(
                labels_dir=source_path,
                images_dir=images_dir,
                classes_file=classes_file,
                image_ext=image_ext,
            )

        elif format_type == "voc":
            return reader_class.read(source_path)

        raise ValueError(f"Format {format_type} not implemented")

    def write(
        self,
        format_type: FormatType,
        dataset: Dataset,
        target_path: Union[str, Path],
        **kwargs,
    ) -> None:
        """
        Write dataset to a specific format.

        Args:
            format_type: Format type ('coco', 'yolo', 'voc')
            dataset: Dataset object to write
            target_path: Path to write annotations
            **kwargs: Format-specific parameters
        """
        if format_type not in self.writers:
            raise ValueError(
                f"Unsupported format: {format_type}. "
                f"Supported formats: {list(self.writers.keys())}"
            )

        writer_class = self.writers[format_type]

        if format_type == "coco":
            writer_class.write(dataset, target_path)

        elif format_type == "yolo":
            output_classes_file = kwargs.get("output_classes_file")
            if not output_classes_file:
                # Default to classes.txt in same directory as labels
                output_classes_file = Path(target_path).parent / "classes.txt"

            writer_class.write(
                dataset,
                output_labels_dir=target_path,
                output_classes_file=output_classes_file,
            )

        elif format_type == "voc":
            writer_class.write(dataset, target_path)

        else:
            raise ValueError(f"Format {format_type} not implemented")
