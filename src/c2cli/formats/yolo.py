"""YOLO format reader and writer."""

from pathlib import Path
from typing import Union, Optional

from ..models import Dataset, Image, Annotation, Category, BBox


class YOLOReader:
    """Read YOLO format annotations."""

    @staticmethod
    def read(
        labels_dir: Union[str, Path],
        images_dir: Union[str, Path],
        classes_file: Union[str, Path],
        image_ext: str = ".jpg"
    ) -> Dataset:
        """
        Read YOLO format annotations.

        YOLO format:
        - One .txt file per image with same name as image
        - Each line: <class_id> <x_center> <y_center> <width> <height> (normalized 0-1)
        - classes.txt file with one class name per line (line index = class_id)

        Args:
            labels_dir: Directory containing .txt label files
            images_dir: Directory containing image files
            classes_file: Path to classes.txt file
            image_ext: Image file extension (default: .jpg)

        Returns:
            Dataset object
        """
        labels_dir = Path(labels_dir)
        images_dir = Path(images_dir)
        classes_file = Path(classes_file)

        dataset = Dataset()

        # Read classes
        with open(classes_file, 'r') as f:
            class_names = [line.strip() for line in f if line.strip()]

        for idx, name in enumerate(class_names):
            category = Category(id=idx, name=name)
            dataset.add_category(category)

        # Read label files
        for label_file in sorted(labels_dir.glob("*.txt")):
            # Find corresponding image
            image_name = label_file.stem + image_ext
            image_path = images_dir / image_name

            if not image_path.exists():
                # Try other common extensions
                for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
                    test_path = images_dir / (label_file.stem + ext)
                    if test_path.exists():
                        image_path = test_path
                        image_name = test_path.name
                        break
                else:
                    continue

            # Get image dimensions (in real implementation, you'd read the actual image)
            # For now, we'll need to store this info or read from a metadata file
            # As a workaround, we'll try to get it from a companion metadata or use PIL
            try:
                from PIL import Image as PILImage
                with PILImage.open(image_path) as img:
                    width, height = img.size
            except ImportError:
                # If PIL not available, skip or use default
                print(f"Warning: PIL not available. Cannot determine image size for {image_name}")
                continue

            image = Image(
                file_name=image_name,
                width=width,
                height=height
            )

            # Read annotations
            with open(label_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split()
                    if len(parts) != 5:
                        continue

                    class_id = int(parts[0])
                    x_center, y_center, w, h = map(float, parts[1:5])

                    # Convert from YOLO format to absolute coordinates
                    bbox = BBox.from_yolo(x_center, y_center, w, h, width, height)

                    annotation = Annotation(
                        bbox=bbox,
                        category_id=class_id,
                        category_name=class_names[class_id] if class_id < len(class_names) else 'unknown'
                    )
                    image.add_annotation(annotation)

            dataset.add_image(image)

        return dataset


class YOLOWriter:
    """Write YOLO format annotations."""

    @staticmethod
    def write(
        dataset: Dataset,
        output_labels_dir: Union[str, Path],
        output_classes_file: Union[str, Path]
    ) -> None:
        """
        Write dataset to YOLO format.

        Args:
            dataset: Dataset object
            output_labels_dir: Directory to write .txt label files
            output_classes_file: Path to write classes.txt file
        """
        output_labels_dir = Path(output_labels_dir)
        output_classes_file = Path(output_classes_file)

        output_labels_dir.mkdir(parents=True, exist_ok=True)
        output_classes_file.parent.mkdir(parents=True, exist_ok=True)

        # Write classes file
        sorted_categories = sorted(dataset.categories, key=lambda c: c.id)
        with open(output_classes_file, 'w') as f:
            for category in sorted_categories:
                f.write(f"{category.name}\n")

        # Write label files
        for image in dataset.images:
            # Create label file with same name as image (but .txt extension)
            label_name = Path(image.file_name).stem + ".txt"
            label_path = output_labels_dir / label_name

            with open(label_path, 'w') as f:
                for annotation in image.annotations:
                    # Convert bbox to YOLO format
                    x_center, y_center, width, height = annotation.bbox.to_yolo(
                        image.width, image.height
                    )

                    # Write: class_id x_center y_center width height
                    f.write(f"{annotation.category_id} {x_center:.6f} {y_center:.6f} "
                           f"{width:.6f} {height:.6f}\n")
