import os
import csv
#import yaml
import random
from tqdm import tqdm
from pathlib import Path

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
        self.test_split_percentage = config['test_split_percentage']
        
        self.category_count_dict = dict()
        self.all_annotations_dict = defaultdict(list)


    def convert_coco_json_to_dict(self, annotation_file):
        """Extracts bbox information from json files in the coco format (also used by LILABC datasets) and puts in self.all_annotations_dict
        """
        print(f'Using annotation file: {annotation_file}')
        root_dir = os.path.dirname(annotation_file)
        categories, annotations, images = helpers.get_coco_json_data(annotation_file)

        category_id_to_name_dict = {cat['id']:cat['name'] for cat in categories}
        categories_of_interest = set(self.categories)
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
        """Extracts bbox information from csv files in the Open Images Dataset V6 format and puts in self.all_annotations_dict
        """        
        print(f'Using annotation file: {annotation_file}')
        root_dir = os.path.dirname(annotation_file)
        
        categories_of_interest = set(self.categories)
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


    def write_yolo_textfiles(self, output_dir, annotations_dict):
        """Creates annotation textfiles in the format required by: https://github.com/ultralytics/yolov5/wiki/Train-Custom-Data
        """
        print(f"Writing annotation textfiles in {output_dir}")
        helpers.ensure_directory_exists(output_dir)
        ## Create the individual textfiles for each image
        for image_filename in tqdm(annotations_dict):
            image_filename_stem = Path(image_filename).stem    
            suffix = '.txt'
            output_filepath = os.path.join(output_dir, image_filename_stem + suffix)
            with open(output_filepath, 'w') as f:
                for bbox in annotations_dict[image_filename]:
                    category = bbox['category']
                    category_int = self.categories.index(category)
                    x_min, x_max = bbox['x_min'], bbox['x_max']
                    y_min, y_max = bbox['y_min'], bbox['y_max']
                    x_center = (x_min + x_max) / 2
                    y_center = (y_min + y_max) / 2
                    bbox_width = x_max - x_min
                    bbox_height = y_max - y_min
                    data = [category_int, x_center, y_center, bbox_width, bbox_height]
                    line = ' '.join(map(str,data)) + "\n"
                    f.write(line)
        
        # ## Create the dataset.yaml file
        # yaml_dict = {}
        # yaml_dict['path'] = 'rootdir  # Please change'
        # yaml_dict['train'] = 'images/train'
        # yaml_dict['val'] = 'images/val'
        # yaml_dict['test'] = 'images/test'

        # nc = len(self.categories)
        # yaml_dict['nc'] = nc
        # yaml_dict['names'] = self.categories
        
        # output_yaml = os.path.join(output_dir, 'dataset.yaml')
        # with open(output_yaml, 'w') as yaml_f:
        #     data1 = yaml.dump(yaml_dict, yaml_f, default_flow_style=None)

    def split_dictionary_train_test(self, test_size):
        """Randomly splits an annotations_dict into separate dictionaries for training and testing.)
        """
        annotations_list = [(key, value) for key, value in self.all_annotations_dict.items()]
        num = len(annotations_list)
        random.shuffle(annotations_list)
        
        train_annotations_list = annotations_list[int((num+1)*test_size):]
        test_annotations_list = annotations_list[:int((num+1)*test_size)]
        train_annotations_dict = dict(train_annotations_list)
        test_annotations_dict = dict(test_annotations_list)
        return train_annotations_dict, test_annotations_dict

    def run(self):
        print(f"\nThe list of categories used (in the order of index class labels) is:\n{self.categories}\n")
        if self.input_annotation_format == 'coco_json':
            self.convert_coco_json_to_dict(self.input_annotations)
        elif self.input_annotation_format == 'oid_csv':
            self.convert_oid_csv_to_dict(self.input_annotations)

        if self.output_annotation_format == 'yolo_textfiles':
            if self.test_split_percentage > 0:
                train_annotations_dict, test_annotations_dict = self.split_dictionary_train_test(self.test_split_percentage)
                self.write_yolo_textfiles(os.path.join(self.output_annotations, 'train'), train_annotations_dict)
                self.write_yolo_textfiles(os.path.join(self.output_annotations, 'val'), test_annotations_dict)
            else:
                self.write_yolo_textfiles(self.output_annotations, self.all_annotations_dict)