import argparse
from asyncio.log import logger
import json
import subprocess

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Executes a hub component.'
    )
    parser.add_argument('-b',
                        '--build-spec',
                        type=str,
                        nargs=1,
                        help='Build Spec',
                        required=True)

    args = parser.parse_args()
    build_spec = json.loads(args.build_spec[0])
    print(build_spec)
