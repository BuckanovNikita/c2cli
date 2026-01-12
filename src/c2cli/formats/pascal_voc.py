"""Pascal VOC format reader and writer."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union, Set

from ..models import Dataset, Image, Annotation, Category, BBox


class PascalVOCReader:
    """Read Pascal VOC format annotations."""

    @staticmethod
    def read(annotations_dir: Union[str, Path]) -> Dataset:
        """
        Read Pascal VOC format XML annotations.

        Pascal VOC format:
        - One XML file per image
        - Contains image info and bounding boxes with class labels

        Args:
            annotations_dir: Directory containing .xml annotation files

        Returns:
            Dataset object
        """
        annotations_dir = Path(annotations_dir)
        dataset = Dataset()

        # Collect all unique categories
        categories_set: Set[str] = set()
        xml_files = list(annotations_dir.glob("*.xml"))

        # First pass: collect all category names
        for xml_file in xml_files:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for obj in root.findall("object"):
                name_elem = obj.find("name")
                if name_elem is not None and name_elem.text is not None:
                    categories_set.add(name_elem.text)

        # Create categories with IDs
        category_map = {}
        for idx, name in enumerate(sorted(categories_set)):
            category = Category(id=idx, name=name)
            dataset.add_category(category)
            category_map[name] = idx

        # Second pass: read images and annotations
        for xml_file in xml_files:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Read image info
            filename_elem = root.find("filename")
            if filename_elem is None or filename_elem.text is None:
                continue
            filename = filename_elem.text

            size = root.find("size")
            if size is None:
                continue

            width_elem = size.find("width")
            height_elem = size.find("height")
            if (
                width_elem is None
                or width_elem.text is None
                or height_elem is None
                or height_elem.text is None
            ):
                continue

            width = int(width_elem.text)
            height = int(height_elem.text)

            image = Image(file_name=filename, width=width, height=height)

            # Read objects/annotations
            for obj in root.findall("object"):
                name_elem = obj.find("name")
                if name_elem is None or name_elem.text is None:
                    continue
                name = name_elem.text

                difficult_elem = obj.find("difficult")
                difficult = (
                    int(difficult_elem.text)
                    if difficult_elem is not None and difficult_elem.text is not None
                    else 0
                )

                truncated_elem = obj.find("truncated")
                truncated = (
                    int(truncated_elem.text)
                    if truncated_elem is not None and truncated_elem.text is not None
                    else 0
                )

                bndbox = obj.find("bndbox")
                if bndbox is None:
                    continue

                xmin_elem = bndbox.find("xmin")
                ymin_elem = bndbox.find("ymin")
                xmax_elem = bndbox.find("xmax")
                ymax_elem = bndbox.find("ymax")

                if (
                    xmin_elem is None
                    or xmin_elem.text is None
                    or ymin_elem is None
                    or ymin_elem.text is None
                    or xmax_elem is None
                    or xmax_elem.text is None
                    or ymax_elem is None
                    or ymax_elem.text is None
                ):
                    continue

                xmin = float(xmin_elem.text)
                ymin = float(ymin_elem.text)
                xmax = float(xmax_elem.text)
                ymax = float(ymax_elem.text)

                bbox = BBox(xmin, ymin, xmax, ymax)

                annotation = Annotation(
                    bbox=bbox,
                    category_id=category_map[name],
                    category_name=name,
                    difficult=bool(difficult),
                    truncated=bool(truncated),
                )
                image.add_annotation(annotation)

            dataset.add_image(image)

        return dataset


class PascalVOCWriter:
    """Write Pascal VOC format annotations."""

    @staticmethod
    def write(dataset: Dataset, output_dir: Union[str, Path]) -> None:
        """
        Write dataset to Pascal VOC format XML files.

        Args:
            dataset: Dataset object
            output_dir: Directory to write .xml annotation files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for image in dataset.images:
            # Create XML structure
            annotation = ET.Element("annotation")

            # Folder
            folder = ET.SubElement(annotation, "folder")
            folder.text = "images"

            # Filename
            filename = ET.SubElement(annotation, "filename")
            filename.text = image.file_name

            # Path (optional)
            path = ET.SubElement(annotation, "path")
            path.text = image.file_name

            # Source
            source = ET.SubElement(annotation, "source")
            database = ET.SubElement(source, "database")
            database.text = "Unknown"

            # Size
            size = ET.SubElement(annotation, "size")
            width = ET.SubElement(size, "width")
            width.text = str(image.width)
            height = ET.SubElement(size, "height")
            height.text = str(image.height)
            depth = ET.SubElement(size, "depth")
            depth.text = "3"

            # Segmented
            segmented = ET.SubElement(annotation, "segmented")
            segmented.text = "0"

            # Objects
            for ann in image.annotations:
                obj = ET.SubElement(annotation, "object")

                name = ET.SubElement(obj, "name")
                name.text = ann.category_name

                pose = ET.SubElement(obj, "pose")
                pose.text = "Unspecified"

                truncated = ET.SubElement(obj, "truncated")
                truncated.text = "1" if ann.truncated else "0"

                difficult = ET.SubElement(obj, "difficult")
                difficult.text = "1" if ann.difficult else "0"

                bndbox = ET.SubElement(obj, "bndbox")
                xmin = ET.SubElement(bndbox, "xmin")
                xmin.text = str(int(ann.bbox.x_min))
                ymin = ET.SubElement(bndbox, "ymin")
                ymin.text = str(int(ann.bbox.y_min))
                xmax = ET.SubElement(bndbox, "xmax")
                xmax.text = str(int(ann.bbox.x_max))
                ymax = ET.SubElement(bndbox, "ymax")
                ymax.text = str(int(ann.bbox.y_max))

            # Write to file
            xml_filename = Path(image.file_name).stem + ".xml"
            xml_path = output_dir / xml_filename

            tree = ET.ElementTree(annotation)
            ET.indent(tree, space="  ")
            tree.write(xml_path, encoding="utf-8", xml_declaration=True)
