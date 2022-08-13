import argparse

def create_parser():
    
    parser = argparse.ArgumentParser(description = """Many functions relating to the different dataset formats.""")
    subparser = parser.add_subparsers(dest='operation')
    convert_parser = subparser.add_parser('convert', help='For converting bbox annotations between different formats.')


    return parser
    
