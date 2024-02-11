import os

from App import get_app_run

import argparse

from Model.classes import Game


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000, help='set port,default=5000')
    parser.add_argument('-s', '--server', type=str, default='127.0.0.1', help='set host,default=127.0.0.1')
    parser.add_argument('-r', '--route', type=str, default='', help="set path,default=''")
    parser.add_argument('-d', '--debug', action='store_true', help='if debug')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    app = get_app_run(args.route)
    if args.debug:
        app.run(host=args.server, port=args.port, debug=True)
    else:
        app.run(host=args.server, port=args.port)
