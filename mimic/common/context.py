#
# Mimic - Deploy web applications as users
#

import argparse
import configparser
import logging

class MimicContext:
    def __init__(self, args={}) -> None:
        self.args = args
        self.config = self.load_config()
        self.logger = logging.getLogger("mimic")

    def load_config(self) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config.read(self.args.config)
        return config
