"""Common data models for computer vision annotations."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class BBox:
    """Bounding box representation (x_min, y_min, x_max, y_max)."""
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    def to_xywh(self) -> tuple[float, float, float, float]:
        """Convert to (x, y, width, height) format."""
        return (
            self.x_min,
            self.y_min,
            self.x_max - self.x_min,
            self.y_max - self.y_min
        )

    def to_yolo(self, img_width: int, img_height: int) -> tuple[float, float, float, float]:
        """Convert to YOLO format (x_center, y_center, width, height) normalized."""
        width = self.x_max - self.x_min
        height = self.y_max - self.y_min
        x_center = self.x_min + width / 2
        y_center = self.y_min + height / 2

        return (
            x_center / img_width,
            y_center / img_height,
            width / img_width,
            height / img_height
        )

    @classmethod
    def from_xywh(cls, x: float, y: float, w: float, h: float) -> "BBox":
        """Create from (x, y, width, height) format."""
        return cls(x, y, x + w, y + h)

    @classmethod
    def from_yolo(cls, x_center: float, y_center: float, width: float, height: float,
                  img_width: int, img_height: int) -> "BBox":
        """Create from YOLO format (normalized x_center, y_center, width, height)."""
        w = width * img_width
        h = height * img_height
        x = (x_center * img_width) - w / 2
        y = (y_center * img_height) - h / 2
        return cls(x, y, x + w, y + h)


@dataclass
class Annotation:
    """Single object annotation."""
    bbox: BBox
    category_id: int
    category_name: str
    difficult: bool = False
    truncated: bool = False
    area: Optional[float] = None
    iscrowd: int = 0

    def __post_init__(self):
        """Calculate area if not provided."""
        if self.area is None:
            x, y, w, h = self.bbox.to_xywh()
            self.area = w * h


@dataclass
class Image:
    """Image with annotations."""
    file_name: str
    width: int
    height: int
    annotations: List[Annotation] = field(default_factory=list)
    image_id: Optional[int] = None

    def add_annotation(self, annotation: Annotation) -> None:
        """Add an annotation to the image."""
        self.annotations.append(annotation)


@dataclass
class Category:
    """Category/class definition."""
    id: int
    name: str
    supercategory: Optional[str] = None


@dataclass
class Dataset:
    """Complete dataset with images and categories."""
    images: List[Image] = field(default_factory=list)
    categories: List[Category] = field(default_factory=list)
    info: Dict[str, Any] = field(default_factory=dict)

    def add_image(self, image: Image) -> None:
        """Add an image to the dataset."""
        self.images.append(image)

    def add_category(self, category: Category) -> None:
        """Add a category to the dataset."""
        self.categories.append(category)

    def get_category_by_id(self, cat_id: int) -> Optional[Category]:
        """Get category by ID."""
        for cat in self.categories:
            if cat.id == cat_id:
                return cat
        return None

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get category by name."""
        for cat in self.categories:
            if cat.name == name:
                return cat
        return None
