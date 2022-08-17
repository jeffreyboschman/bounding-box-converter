import os
import json

from collections import defaultdict
import helpers.helpers as helpers

class AnnotationConverter():
    """
    Convert bbox annotations between different formats. 
    
    First converts to all_annotations_dict with format {image_filename: [{category, orig_category_id, new_category_id, x_min, x_max, y_min, y_max},],},
    where each element of the list corresponds to a different bbox

    Attributes
    ----------
    
    categories: list of str
        The specific categories/classes we want to utilize

    intput_annotation_format: str
        The style of the annotations that we want to convert into a different style. Options: coco_json, yolo_textfiles, oidv6_csv, all_files. (yolo_textfiles not implemented yet). Default: coco_json.

    input_annotations: str
        The path to the input annotations. When input_annotation_format is coco_json or oidv6_csv, this is a file. When input_annotation_format is yolo_textfiles, this is a folder (not implemented yet). Default: ./examples/coco_example.json

    output_annotation_format: str
        The style of the annotations that we want to convert the original annotations into. Options: coco_json, yolo_textfiles, oidv6_csv. Default: yolo_textfiles

    output_annotations: str
        The path to the output annotations. When output_annotation_format is coco_json or oidv6_csv, this is a file (not implemented yet). When output_annotation_format is yolo_textfiles, this is a folder. Default: ./examples/yolo_textfiles_examples/

    output_symlink_dir: str
        The path to where you want symlinks of images to be. Only when you do input_annotation_format `all_files`

    count_bboxes_only:
        A boolean option to only count the number of bboxes for each category (i.e., do not write any output annotation files, and do not symlink images when input_annotation_format is `all_files`). Default: False


    """
    
    def __init__(self, config):
        self.categories = config['categories']
        self.categories = [helpers.standardize_string(item) for item in self.categories]
        self.categories = list(set(self.categories))
        self.categories.sort()
        
        self.input_annotation_format = config['input_annotation_format']
        self.input_annotations = config['input_annotations']
        self.output_annotation_format = config['output_annotation_format']
        self.output_annotations = config['output_annotations']
        
        self.category_count_dict = dict()
        self.all_annotations_dict = defaultdict(list)

    def convert_coco_json_to_dict(self, annotation_file, categories_of_interest):
        """Extracts bbox information from json files in the coco format (also used by LILABC datasets) and puts in a default dict

        """
        current_category_count_dict = dict()
        categories_of_interest = set(categories_of_interest)

        print(f'Using annotation file: {annotation_file}')
        root_dir = os.path.dirname(annotation_file)
        with open(annotation_file, 'r') as f:
            data = json.load(f)
        
        # The coco format json file has three sections of interest: categories, annotations, and images
        categories = data['categories']
        for cat in categories:
            cat['name'] = helpers.standardize_string(cat['name'])
        category_id_to_name_dict = {cat['id']:cat['name'] for cat in categories}
        annotations = data['annotations']     
        images = dict()
        for img in data['images']:
            images[img['id']] = img

        # Iterate over all annotations and add relevant ones to the default dict
        for annotation in annotations:
            category_id = annotation['category_id']
            category = category_id_to_name_dict[category_id]
            if category in categories_of_interest:
                current_category_count_dict[category] = current_category_count_dict.get(category, 0) + 1
                self.category_count_dict[category] = self.category_count_dict.get(category, 0) + 1
                bbox = annotation['bbox']
                x_min, y_min, bbox_width, bbox_height = bbox[0], bbox[1], bbox[2], bbox[3]
                image_id = annotation['image_id']
                img_data = images[image_id]
                img_width = img_data['width']
                img_height = img_data['height']
                image_filename = img_data['file_name']
                image_filepath = os.path.join(root_dir, 'images', image_filename)
                x_max = (x_min + bbox_width) / img_width
                y_max = (y_min + bbox_height) / img_height
                x_min = x_min / img_width
                y_min = y_min / img_height
                bbox_dict = {'category': category, 'orig_category_id': category_id,
                                        'x_min': float(x_min), 'y_min': float(y_min), 'x_max': float(x_max), 'y_max': float(y_max), 'image_filepath': image_filepath}
                self.all_annotations_dict[image_filename].append(bbox_dict)
        sorted_ccc_dict = dict(sorted(current_category_count_dict.items()))
        print(sorted_ccc_dict)

    def run(self):
        print(f"\nThe list of categories used (in the order of index class labels) is:\n{self.categories}\n")
        if self.input_annotation_format == 'coco_json':
            self.convert_coco_json_to_dict(self.input_annotations, self.categories)
