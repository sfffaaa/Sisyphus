#! /usr/bin/env python
# Copyright (C) 2017-2018 cmj<cmj@cmj.tw>. All right reserved.

__VERSION__ = '0.0.1'

import argparse
import sys
from os.path import expanduser
import zmq

from sisyphus.sisyphus import Sisyphus

class CommandLine(object):

    def run(self, argv=None):
        argv = argv if argv else sys.argv[1:]
        argv = argv.split() if isinstance(argv, str) else argv

        parser = argparse.ArgumentParser()

        _a = parser.add_argument

        _a('-f', action='store_true', default=False, help='Run as background before execution')
        _a('-c', '--config', default='', type=str, help='Specifies the configuration')
        _a('-s', '--server', action='store_true', default=False, help='Run as server mode')
        _a('commands', nargs='*', help='CLI commands')

        args = parser.parse_args(argv)
        self.load_config(argv)
        if args.f or args.server:
            if not args.server:
                parser.error('-f only be set when -s/--server enable')
            self.server()
        else:
            if not args.commands:
                parser.error('CLI mode need commands')
            self.client(*args.commands)

    def load_config(self, argv): # pylint: disable=unused-argument
        self.config = {      # NOTE - default configuration
            'SISYPHUS_RPC': f'ipc://{expanduser("~")}/.sisyphus.sock',
        }

    def server(self):
        ''' Run as server-mode '''
        ctx = zmq.Context()
        sk = ctx.sock(zmq.SUB) # pylint: disable=E1101
        sk.bind(self.config['SISYPHUS_RPC'])

        while True:
            cmd = sk.recv() # pylint: disable=unused-variable
            # TODO - Receive command and dispatch to Sisyphus

    def client(self, cmd, *args): # pylint: disable=unused-argument
        ''' Run as client-mode '''
        ctx = zmq.Context()
        sk = ctx.sock(zmq.PUB) # pylint: disable=E1101
        sk.connect(self.config['SISYPHUS_RPC'])

        # TODO - Send the comamnd and sub-command if need

cli = CommandLine()
