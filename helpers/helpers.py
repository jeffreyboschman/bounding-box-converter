import os
import json
import pathlib


def ensure_directory_exists(dir_path):
    """Creates directory (and the path leading up to it) if it does not exist. If it already exists, then does nothing."""
    if not os.path.exists(dir_path):
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)


def standardize_string(text):
    """Standardizes texts to be lowercase and use underscores instead of spaces."""
    text = text.strip()
    text = text.lower()
    text = text.replace(" ", "_")
    return text


def clean_list(lst):
    """"Standardizes each item, ensures there are no duplicates, and sorts a list"""
    lst = [standardize_string(item) for item in lst]
    lst = list(set(lst))
    lst.sort()
    return lst


def get_coco_json_data(json_file):
    """Opens json file that contains annotations in the COCO format,
    returns dictionaries for the three sections of interest: categories, annotations, and images
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
        
    # The coco format json file has three sections of interest: categories, annotations, and images
    categories = data['categories']
    for cat in categories:
        cat['name'] = standardize_string(cat['name'])
    category_id_to_name_dict = {cat['id']:cat['name'] for cat in categories}
    annotations = data['annotations']     
    images = dict()
    for img in data['images']:
        images[img['id']] = img
    
    return categories, annotations, images

def get_standard_bbox_coords_from_coco_bbox(annotation_dict, image_dicts):
    """Gets bbox dict from COCO data

    Attributes
    ----------

    annotation_dict: dict
        A dictionary (from a COCO json annotation file) that contains information about a specific annotation (i.e., a bbox). 
        It contains at least the following keys and values: {'image_id': image_id, category_id: 'category_id', bbox: [x_min, y_min, bbox_width, bbox_height]}.
        As per the COCO format, the bbox values are in pixels.
    
    image_dicts: dict of dicts
        A dictionary (from a COCO json annotation file) that contains information about all the images. 
        The key of the main dict is image_ids.
        The subdicionary has at least the following keys and values: {'width': width, 'height': height, 'filename', image filename}

    Returns
    --------

    x_min, y_min, x_max, y_max: float
        Four values corresponding to the four corners of a bbox. 
        The bbox values are standardized between 0 and 1 based on the image height and width. 
    """

    bbox = annotation_dict['bbox']
    x_min, y_min, bbox_width, bbox_height = bbox[0], bbox[1], bbox[2], bbox[3]
    image_id = annotation_dict['image_id']
    image_data = image_dicts[image_id]
    image_width = image_data['width']
    image_height = image_data['height']
    x_max = (x_min + bbox_width) / image_width
    y_max = (y_min + bbox_height) / image_height
    x_min = x_min / image_width
    y_min = y_min / image_height
    
    return x_min, y_min, x_max, y_max