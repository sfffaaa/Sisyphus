#! /usr/bin/env python
# Copyright (C) 2017-2018 cmj<cmj@cmj.tw>. All right reserved.

import argparse
from contextlib import contextmanager
import importlib
import sys
import os
import zmq

from sisyphus.sisyphus import Sisyphus

class CommandLine(Sisyphus):

    def run(self, argv=None):
        argv = argv if argv else sys.argv[1:]
        argv = argv.split() if isinstance(argv, str) else argv

        parser = argparse.ArgumentParser()

        _a = parser.add_argument
        _a('-f', action='store_true', default=False, help='Run as background before execution')
        _a('-c', '--config', default='', type=str, help='Specifies the configuration')
        _a('-s', '--server', action='store_true', default=False, help='Run as server mode')
        _a('-v', '--verbose', action='store_true', default=False, help='Show verbose message')

        # client sub-command
        _sub = parser.add_subparsers(help='CLI commands')

        _sub_task = _sub.add_parser('run', help='Run single task without server')
        _sub_task.add_argument('--count', type=int, default=-1, help='Counter of executions')
        _sub_task.add_argument('--frequency', type=int, default=1, help='Update frequency')
        _sub_task.add_argument('-F', '--entry-point', type=str, default='run', help='Entry function')
        _sub_task.add_argument('filepath', help='Module path')
        _sub_task.set_defaults(func=self.run_single_task)


        args = parser.parse_args(argv)
        super().__init__(args.verbose)

        if args.config: self.load_config(args.config)

        if args.f or args.server:
            if not args.server:
                parser.error('-f only be set when -s/--server enable')
            self.server()
        elif hasattr(args, 'func'):
            self.info(f'Run sub-command `{args.func.__name__}` ...')
            args.func(args)
        else:
            parser.print_help()

    def server(self):
        ''' Run as server-mode '''
        ctx = zmq.Context()
        sk = ctx.sock(zmq.SUB) # pylint: disable=E1101
        sk.bind(self.config['SISYPHUS_RPC'])

        while True:
            cmd = sk.recv() # pylint: disable=unused-variable
            # TODO - Receive command and dispatch to Sisyphus

    @contextmanager
    def add_env_path(self, path=None):
        path = path or f'{os.getcwd()}'
        self.info(f'Template add env PATH: {path}')
        env_path = sys.path[:]

        sys.path.insert(0, path)
        yield sys.path

        sys.path = env_path

    def run_single_task(self, args):
        if not args.filepath.endswith('.py'):
            raise KeyError(f'not the valid python file name {args.filepath}')

        if args.filepath.startswith('/'):
            cwd = os.path.dirname(args.filepath)
            path = os.path.basename(args.filepath)[:-3]
        else:
            cwd = None
            path = '.'.join(args.filepath[:-3].split('/'))

        with self.add_env_path(cwd):
            task = importlib.import_module(f'{path}')

            if not hasattr(task, args.entry_point):
                attrs = ', '.join(dir(task))
                msg = f'entry function `{args.entry_point}` not found in {args.filepath} - {attrs}'
                raise KeyError(msg)
            self.register(args.frequency, args.count)(getattr(task, args.entry_point))
            self()

cli = CommandLine()
