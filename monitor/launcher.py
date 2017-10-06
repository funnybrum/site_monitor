#!/usr/bin/env python

import argparse

from processor import Processor
from common.log import log
from config.loader import ConfigLoader

if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description="""
        Parse sites and send the data to an email.
        Usage:
            python launcher.py
    """)

    args_parser.add_argument('--dry_run', action='store_true', default=False,
                             help='Do not send emails')

    args_parser.add_argument('--show_html', action='store_true', default=False,
                             help='Print generated html')

    args_parser.add_argument('--config', type=str,
                             help='Process only specified config')

    args = args_parser.parse_args()

    configs = ConfigLoader.load_all_configs()

    # Filter out disabled configs.
    configs = [config for config in configs if config.enabled]

    # If --config is specified - pick only that config
    if args.config:
        one_config = [config for config in configs if config.name == args.config]
        if not one_config:
            log('Invalid --config value, no config named %s was found. Available configs are %s' % (
                args.config,
                [config.name for config in configs]
            ))
        configs = one_config

    params = {
        "dry_run": args.dry_run,
        "show_html": args.show_html
    }

    for config in configs:
        log("Running %s" % config.name)
        # try:
        Processor(config, params).execute()
        # except Exception as e:
        #     log('Failed for config %s: %s' % (config.name, e))
