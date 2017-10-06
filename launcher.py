import argparse
import traceback

from monitor.processor import Processor
from monitor.common.log import log
from monitor.config.loader import ConfigLoader
from monitor.notifier.sender import EMail

if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description="""
        Parse sites and send the data to an email.
        Usage:
            python launcher.py
    """)

    args_parser.add_argument('--dry_run', action='store_true', default=False,
                             help='Do not send emails')

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
        "dry_run": args.dry_run
    }

    for config in configs:
        log("Running %s" % config.name)
        try:
            Processor(config, params).execute()
        except:
            message = 'Failed for config %s:\n%s' % (config.name, traceback.format_exc())
            EMail(config.smtp).send(message.replace("\n", "<br>"))
            log(message)
