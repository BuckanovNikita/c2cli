"""COCO format reader and writer."""

import json
from pathlib import Path
from typing import Union

from ..models import Dataset, Image, Annotation, Category, BBox


class COCOReader:
    """Read COCO format annotations."""

    @staticmethod
    def read(annotation_path: Union[str, Path]) -> Dataset:
        """
        Read COCO format JSON file.

        Args:
            annotation_path: Path to COCO JSON file

        Returns:
            Dataset object
        """
        annotation_path = Path(annotation_path)

        with open(annotation_path, "r") as f:
            coco_data = json.load(f)

        dataset = Dataset()

        # Read info
        if "info" in coco_data:
            dataset.info = coco_data["info"]

        # Read categories
        category_map = {}
        for cat in coco_data.get("categories", []):
            category = Category(
                id=cat["id"], name=cat["name"], supercategory=cat.get("supercategory")
            )
            dataset.add_category(category)
            category_map[cat["id"]] = cat["name"]

        # Read images and create mapping
        image_map = {}
        for img in coco_data.get("images", []):
            image = Image(
                file_name=img["file_name"],
                width=img["width"],
                height=img["height"],
                image_id=img["id"],
            )
            dataset.add_image(image)
            image_map[img["id"]] = image

        # Read annotations and assign to images
        for ann in coco_data.get("annotations", []):
            # COCO bbox is [x, y, width, height]
            x, y, w, h = ann["bbox"]
            bbox = BBox.from_xywh(x, y, w, h)

            annotation = Annotation(
                bbox=bbox,
                category_id=ann["category_id"],
                category_name=category_map.get(ann["category_id"], "unknown"),
                area=ann.get("area"),
                iscrowd=ann.get("iscrowd", 0),
            )

            # Add annotation to corresponding image
            if ann["image_id"] in image_map:
                image_map[ann["image_id"]].add_annotation(annotation)

        return dataset


class COCOWriter:
    """Write COCO format annotations."""

    @staticmethod
    def write(dataset: Dataset, output_path: Union[str, Path]) -> None:
        """
        Write dataset to COCO format JSON file.

        Args:
            dataset: Dataset object
            output_path: Path to output JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        coco_data = {
            "info": dataset.info,
            "licenses": [],
            "categories": [],
            "images": [],
            "annotations": [],
        }

        # Write categories
        for category in dataset.categories:
            cat_dict = {
                "id": category.id,
                "name": category.name,
            }
            if category.supercategory:
                cat_dict["supercategory"] = category.supercategory
            coco_data["categories"].append(cat_dict)

        # Write images and annotations
        annotation_id = 1
        for idx, image in enumerate(dataset.images, start=1):
            # Assign image_id if not set
            if image.image_id is None:
                image.image_id = idx

            img_dict = {
                "id": image.image_id,
                "file_name": image.file_name,
                "width": image.width,
                "height": image.height,
            }
            coco_data["images"].append(img_dict)

            # Write annotations for this image
            for annotation in image.annotations:
                x, y, w, h = annotation.bbox.to_xywh()
                ann_dict = {
                    "id": annotation_id,
                    "image_id": image.image_id,
                    "category_id": annotation.category_id,
                    "bbox": [x, y, w, h],
                    "area": annotation.area,
                    "iscrowd": annotation.iscrowd,
                    "segmentation": [],
                }
                coco_data["annotations"].append(ann_dict)
                annotation_id += 1

        with open(output_path, "w") as f:
            json.dump(coco_data, f, indent=2)
