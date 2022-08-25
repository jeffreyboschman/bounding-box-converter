import sys
#sys.path.insert(0, '..')
import unittest
from helpers.converter import AnnotationConverter


class TestConvert(unittest.TestCase):

    def test_coco_json_to_dict(self):
        config = {'categories': ['zebra', 'giraffe'], \
                    'input_annotation_format': 'coco_json', \
                    'input_annotations': './data/coco_ex.json', \
                    'output_annotation_format': 0, \
                    'output_annotations': 0}
        ac = AnnotationConverter(config)
        ac.convert_coco_json_to_dict(ac.input_annotations, ac.categories)
        all_annotations_dict = ac.all_annotations_dict
        result = all_annotations_dict['000000236730.jpg'][0]['category']
        self.assertEqual(result, 'zebra')
        
        config = {'categories': ['dog'], \
                    'input_annotation_format': 'coco_json', \
                    'input_annotations': './data/coco_ex.json', \
                    'output_annotation_format': 0, \
                    'output_annotations': 0}
        ac = AnnotationConverter(config)
        ac.convert_coco_json_to_dict(ac.input_annotations, ac.categories)
        all_annotations_dict = ac.all_annotations_dict  # Should be an empty defaultdict, which evaluates to False. 
        self.assertFalse(all_annotations_dict)


if __name__ == "__main__":
    unittest.main()