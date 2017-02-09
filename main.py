#!/usr/bin/env python

import argparse
from processor import Processor
from lib.yaml_config import load_configs, load_config
from multiprocessing import Pool

MAX_PROCESSES = 4


def worker(*args, **kwargs):
    w = Processor(*args, **kwargs)
    return w.run()

if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description="""
        Parse sites and send the data to an email.
        Usage:
            APP_CONFIG=./config/ python main.py
    """)

    args_parser.add_argument('--dry_run', action='store_true', default=True,
                             help='Do not send emails')

    args_parser.add_argument('--show_html', action='store_true', default=False,
                             help='Print generated html')

    args_parser.add_argument('--config', type=str,
                             help='Process only specified config')

    args_parser.add_argument('--workers', type=int, default=MAX_PROCESSES,
                             help='Number of parallel requests')

    args = args_parser.parse_args()

    pool = Pool(processes=args.workers)
    if args.config:
        configs = [load_config(args.config)]
    else:
        configs = load_configs()
    for i in range(len(configs)):
        pool.apply_async(worker, kwds={
                         "config": configs[i],
                         "dry_run": args.dry_run,
                         "show_html": args.show_html})
    pool.close()
    pool.join()
