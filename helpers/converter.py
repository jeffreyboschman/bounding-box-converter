import os
import csv
from tqdm import tqdm

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
        self.categories = helpers.clean_list(self.categories)
        
        self.input_annotation_format = config['input_annotation_format']
        self.input_annotations = config['input_annotations']
        self.output_annotation_format = config['output_annotation_format']
        self.output_annotations = config['output_annotations']
        
        self.category_count_dict = dict()
        self.all_annotations_dict = defaultdict(list)


    def convert_coco_json_to_dict(self, annotation_file, categories_of_interest):
        """Extracts bbox information from json files in the coco format (also used by LILABC datasets) and puts in a default dict
        """
        print(f'Using annotation file: {annotation_file}')
        root_dir = os.path.dirname(annotation_file)
        categories, annotations, images = helpers.get_coco_json_data(annotation_file)

        category_id_to_name_dict = {cat['id']:cat['name'] for cat in categories}
        categories_of_interest = set(categories_of_interest)
        current_category_count_dict = dict()

        # Iterate over all annotations and add relevant ones to the default dict
        for annotation in tqdm(annotations):
            category_id = annotation['category_id']
            category = category_id_to_name_dict[category_id]
            if category in categories_of_interest:
                current_category_count_dict[category] = current_category_count_dict.get(category, 0) + 1
                self.category_count_dict[category] = self.category_count_dict.get(category, 0) + 1  # In case we want to count the total
                
                image_id = annotation['image_id']
                image_filename = images[image_id]['file_name']
                image_filepath = os.path.join(root_dir, 'images', image_filename)
                
                x_min, y_min, x_max, y_max = helpers.get_standard_bbox_coords_from_coco_bbox(annotation, images)

                bbox_dict = {'category': category, 'orig_category_id': category_id, 'image_filepath': image_filepath,
                                        'x_min': float(x_min), 'y_min': float(y_min), 'x_max': float(x_max), 'y_max': float(y_max)}
                self.all_annotations_dict[image_filename].append(bbox_dict)
        sorted_ccc_dict = dict(sorted(current_category_count_dict.items()))
        print(sorted_ccc_dict)


    def convert_oid_csv_to_dict(self, annotation_file, categories_of_interest):
        """Extracts bbox information from csv files in the Open Images Dataset V6 format and puts in a default dict
        """        
        print(f'Using annotation file: {annotation_file}')
        root_dir = os.path.dirname(annotation_file)
        
        categories_of_interest = set(categories_of_interest)
        category_id_to_name_dict = helpers.get_oid_category_id_to_name_dict(categories_of_interest)
        current_category_count_dict = dict()

        with open(annotation_file, 'r') as annotation_f:
            csv_reader = csv.reader(annotation_f)
            # Iterate over all annotations and add relevant ones to the default dict
            for annotation in tqdm(csv_reader):
                image_id, __, category_id, __, x_min, x_max, y_min, y_max, *tail = annotation
                category = category_id_to_name_dict[category_id]
                if category in categories_of_interest:
                    current_category_count_dict[category] = current_category_count_dict.get(category, 0) + 1
                    self.category_count_dict[category] = self.category_count_dict.get(category, 0) + 1

                    image_filename = str(image_id) + '.jpg'
                    image_filepath = os.path.join(root_dir, 'images', image_filename)

                    bbox_dict = {'category': category, 'orig_category_id': category_id,
                                        'x_min': float(x_min), 'y_min': float(y_min), 'x_max': float(x_max), 'y_max': float(y_max), 'image_filepath': image_filepath}
                    self.all_annotations_dict[image_filename].append(bbox_dict)
        sorted_ccc_dict = dict(sorted(current_category_count_dict.items()))
        print(sorted_ccc_dict)


    def run(self):
        print(f"\nThe list of categories used (in the order of index class labels) is:\n{self.categories}\n")
        if self.input_annotation_format == 'coco_json':
            self.convert_coco_json_to_dict(self.input_annotations, self.categories)
        elif self.input_annotation_format == 'oid_csv':
            self.convert_oid_csv_to_dict(self.input_annotations, self.categories)