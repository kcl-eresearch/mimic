#
# Mimic - Deploy web applications as users
#

import argparse
import configparser
import logging

class MimicContext:
    def __init__(self) -> None:
        self.args = self.load_args()
        self.config = self.load_config()
        self.logger = logging.getLogger("mimic")
    
    def load_args(self) -> dict:
        args = argparse.ArgumentParser()
        args.add_argument('-c', '--config', default='/etc/mimic/mimic.conf', help='Path to config file')
        (actual_args, _) = args.parse_known_args()
        return actual_args

    def load_config(self) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config.read(self.args.config)
        return config
