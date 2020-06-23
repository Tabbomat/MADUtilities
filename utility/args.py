import configargparse


def parse_args():
    parser = configargparse.ArgParser(default_config_files=['config.ini'])
    parser.add_argument('--madmin_url', required=True, type=str)
    return parser.parse_args()
