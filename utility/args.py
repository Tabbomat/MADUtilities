import configargparse


def parse_args() -> dict:
    parser = configargparse.ArgParser(default_config_files=['config.ini'])
    parser.add_argument('--madmin_url', required=True, type=str)
    parser.add_argument('--madmin_user', required=False, default='', type=str)
    parser.add_argument('--madmin_password', required=False, default='', type=str)
    args, unknown = parser.parse_known_args()
    return {'madmin_url': args.madmin_url.rstrip('/'),
            'madmin_user': args.madmin_user.strip(),
            'madmin_password': args.madmin_password.strip()}
