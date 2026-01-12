# c2cli - Конвертер форматов компьютерного зрения

Python библиотека и инструмент командной строки для конвертации между различными форматами аннотаций компьютерного зрения для задач детекции объектов.

## Поддерживаемые форматы

- **COCO** (Common Objects in Context) - формат JSON
- **YOLO** (You Only Look Once) - текстовые файлы с нормализованными координатами
- **Pascal VOC** (Visual Object Classes) - формат XML

## Возможности

- Конвертация между любыми поддерживаемыми форматами (COCO ↔ YOLO ↔ Pascal VOC)
- Интерфейс командной строки для быстрой конвертации
- Python API для интеграции в ваши рабочие процессы
- Сохранение метаданных аннотаций (флаги difficult, truncated и т.д.)
- Автоматическое определение размеров изображений

## Установка

```bash
# Установка из исходников
git clone <repository-url>
cd c2cli
pip install -e .
```

## Быстрый старт

### Интерфейс командной строки

```bash
# Конвертация COCO в YOLO
c2cli coco yolo --input annotations.json --output labels/ --classes classes.txt

# Конвертация YOLO в Pascal VOC
c2cli yolo voc --input labels/ --output voc_annotations/ \
  --images images/ --classes classes.txt

# Конвертация Pascal VOC в COCO
c2cli voc coco --input voc_annotations/ --output annotations.json
```

### Python API

```python
from c2cli import Converter

# Инициализация конвертера
converter = Converter()

# Конвертация COCO в YOLO
converter.convert(
    source_format='coco',
    target_format='yolo',
    source_path='annotations.json',
    target_path='labels/',
    output_classes_file='classes.txt'
)

# Конвертация YOLO в Pascal VOC
converter.convert(
    source_format='yolo',
    target_format='voc',
    source_path='labels/',
    target_path='voc_annotations/',
    images_dir='images/',
    classes_file='classes.txt'
)

# Конвертация Pascal VOC в COCO
converter.convert(
    source_format='voc',
    target_format='coco',
    source_path='voc_annotations/',
    target_path='annotations.json'
)
```

## Детали форматов

### Формат COCO
- Один JSON файл, содержащий все аннотации
- Структура: `{"images": [...], "annotations": [...], "categories": [...]}`
- Ограничивающие рамки в формате `[x, y, width, height]` (абсолютные координаты)

### Формат YOLO
- Один текстовый файл на изображение (с тем же именем, что и файл изображения)
- Каждая строка: `<class_id> <x_center> <y_center> <width> <height>` (нормализовано 0-1)
- Отдельный файл `classes.txt` с названиями классов (по одному на строку)

### Формат Pascal VOC
- Один XML файл на изображение
- Содержит метаданные изображения и ограничивающие рамки объектов
- Ограничивающие рамки в формате `[xmin, ymin, xmax, ymax]` (абсолютные координаты)
- Поддерживает флаги `difficult` и `truncated`

## Структура проекта

```
c2cli/
├── src/c2cli/
│   ├── __init__.py          # Точка входа CLI и экспорты
│   ├── models.py            # Общие модели данных (Dataset, Image, Annotation, BBox)
│   ├── converter.py         # Основной движок конвертации
│   └── formats/             # Читатели и писатели для конкретных форматов
│       ├── __init__.py
│       ├── coco.py          # Читатель/писатель COCO
│       ├── yolo.py          # Читатель/писатель YOLO
│       └── pascal_voc.py    # Читатель/писатель Pascal VOC
├── pyproject.toml
└── README.md
```

## Расширенное использование

### Чтение и запись конкретных форматов

```python
from c2cli.formats import COCOReader, YOLOWriter

# Чтение аннотаций COCO
dataset = COCOReader.read('annotations.json')

# Просмотр датасета
print(f"Изображений: {len(dataset.images)}")
print(f"Категорий: {len(dataset.categories)}")
for image in dataset.images:
    print(f"{image.file_name}: {len(image.annotations)} объектов")

# Запись в формат YOLO
YOLOWriter.write(
    dataset,
    output_labels_dir='labels/',
    output_classes_file='classes.txt'
)
```

### Работа с моделью данных

```python
from c2cli.models import Dataset, Image, Annotation, Category, BBox

# Программное создание датасета
dataset = Dataset()

# Добавление категорий
dataset.add_category(Category(id=0, name='person'))
dataset.add_category(Category(id=1, name='car'))

# Создание изображения с аннотациями
image = Image(file_name='image001.jpg', width=1920, height=1080)

# Добавление ограничивающих рамок
bbox1 = BBox(100, 200, 300, 400)  # xmin, ymin, xmax, ymax
annotation1 = Annotation(
    bbox=bbox1,
    category_id=0,
    category_name='person'
)
image.add_annotation(annotation1)

dataset.add_image(image)

# Запись в любой формат
from c2cli.formats import COCOWriter
COCOWriter.write(dataset, 'output.json')
```

## Справка по CLI

```
использование: c2cli [-h] [-i INPUT] [-o OUTPUT] [--images IMAGES] [--classes CLASSES]
                     [--image-ext IMAGE_EXT] [-v]
                     {coco,yolo,voc} {coco,yolo,voc}

Конвертация между форматами аннотаций компьютерного зрения (COCO, YOLO, Pascal VOC)

позиционные аргументы:
  {coco,yolo,voc}       Исходный формат аннотаций
  {coco,yolo,voc}       Целевой формат аннотаций

опции:
  -h, --help            Показать справку и выйти
  -i, --input INPUT     Путь к входным данным (файл для COCO, директория для YOLO/VOC)
  -o, --output OUTPUT   Путь к выходным данным (файл для COCO, директория для YOLO/VOC)
  --images IMAGES       Директория с изображениями (требуется для YOLO в качестве источника)
  --classes CLASSES     Путь к файлу с классами (требуется для YOLO)
  --image-ext IMAGE_EXT
                        Расширение файлов изображений для YOLO (по умолчанию: .jpg)
  -v, --version         Показать версию программы и выйти
```

## Разработка

### Запуск тестов

```bash
# TODO: Добавить тесты
pytest tests/
```

### Участие в разработке

Вклад приветствуется! Пожалуйста, не стесняйтесь отправлять Pull Request.

## План развития

- [x] Поддержка формата COCO
- [x] Поддержка формата YOLO
- [x] Поддержка формата Pascal VOC
- [ ] Добавить полный набор тестов
- [ ] Поддержка масок сегментации
- [ ] Поддержка дополнительных форматов (Labelme, CreateML и др.)
- [ ] Валидация и проверка форматов
- [ ] Утилиты для копирования/организации изображений

## Лицензия

MIT License

## Благодарности

- Формат датасета COCO: https://cocodataset.org/
- Формат YOLO: https://github.com/ultralytics/yolov5
- Датасет Pascal VOC: http://host.robots.ox.ac.uk/pascal/VOC/
