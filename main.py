from helpers.parser import parse_arguements
from helpers.converter import AnnotationConverter


def main():
    args = parse_arguements()
    cfg = vars(args)

    if cfg['operation'] == "convert":
        ac = AnnotationConverter(cfg)
        ac.run()


if __name__ == "__main__":
   main() 
