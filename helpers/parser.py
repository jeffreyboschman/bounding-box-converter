import argparse

def parse_arguements():
    
    parser = argparse.ArgumentParser(description = """Many functions relating to the different dataset formats.""")
    subparser = parser.add_subparsers(dest='operation')
    convert_parser = subparser.add_parser('convert', help='For converting bbox annotations between different formats.')

    convert_parser.add_argument('--categories', nargs='+', type=str, default=['cat','dog', 'zebra', 'giraffe'], help='The categories we are interested in. Just separate them with a space.')

    convert_parser.add_argument('--input_annotation_format', type=str, choices=['coco_json', 'oidv6_csv', 'yolo_textfiles'], default='coco_json',
        help='The style of the annotations that we want to convert into a different style. (yolo_textfiles not implemented yet). Default: coco_json')

    convert_parser.add_argument('--input_annotations', type=str, default = './data/coco_example.json',
        help='The path to the input annotations. When input_annotation_format is coco_json or oidv6_csv, this is a file. When input_annotation_format is yolo_textfiles, this is a folder (not implemented yet). Default: ./examples/coco_example.json')

    convert_parser.add_argument('--output_annotation_format', type=str, choices=['coco_json', 'oidv6_csv', 'yolo_textfiles'], default='yolo_textfiles',
        help='The style of the annotations that we want to convert the original annotations into. (coco_json and oidv6_csv not implemented yet). Default: yolo_textfiles')

    convert_parser.add_argument('--output_annotations', type=str, default='./data/yolo_textfiles_examples/',
        help='The path to the output annotations. When output_annotation_format is coco_json or oidv6_csv, this is a file (not implemented yet). When output_annotation_format is yolo_textfiles, this is a folder. Default: ./examples/yolo_textfiles_examples/')

    convert_parser.add_argument('--test_split_percentage', type=int, default=0,
        help='The percentage of images to randomly split into a test set.')

    args = parser.parse_args()

    return args
    
