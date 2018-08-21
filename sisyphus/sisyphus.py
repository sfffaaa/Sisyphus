#! /usr/bin/env python
# Copyright (C) 2018-2018 cmj<cmj@cmj.tw>. All right reserved.

import time
import logging
from multiprocessing import Process
try:
    from setproctitle import setproctitle as procname # pylint: disable=import-error
except ImportError:
    try:
        from procname import setprocname as procname
    except ImportError:
        procname = lambda x: None


class Sisyphus(object):
    _jobs_ = {}

    def __init__(self, debug=False):
        fmt = '[%(asctime)-.19s] (%(filename)s#%(lineno)04d) - %(message)s'
        fmt = logging.Formatter(fmt)

        syslog = logging.StreamHandler()
        syslog.setFormatter(fmt)

        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.DEBUG if debug else logging.WARNING)

        if not logger.handlers:
            logger.addHandler(syslog)
        logger = logging.LoggerAdapter(logger, {'app_name': self.__class__.__name__})

        for attr in 'critical error warning info debug'.split():
            setattr(self, attr, getattr(logger, attr))

    def __call__(self, frequency=5):
        jobs = {}
        try:
            while True:
                for name in self._jobs_:
                    if name not in jobs or not jobs[name].is_alive():
                        jobs[name] = Process(target=self.worker, args=(name, ))
                        jobs[name].start()
                        self.warning(f'new job `{name}` on PID#{jobs[name].pid}')
                time.sleep(frequency)
        except KeyboardInterrupt:
            for name in self._jobs_:
                if name in jobs and jobs[name].is_alive():
                    _ = jobs[name].kill() if hasattr(jobs[name], 'kill') else jobs[name].terminate()
            self.critical(f'Ctrl-C')

    def worker(self, name):
        procname(f'{name} ({self._jobs_[name]["frequency"]})')
        while True:
            self._jobs_[name]['fn'].__globals__['worker'] = self
            self._jobs_[name]['fn']()
            time.sleep(self._jobs_[name]['frequency'])

    @property
    def jobs(self):
        jobs = [f'- {job} ({item["fn"]})' for job, item in self._jobs_.items()]
        return '\n'.join(jobs)

    @classmethod
    def register(cls, frequency=1):
        def wrapper(func):
            if func.__name__ in cls._jobs_:
                raise KeyError(func.__name__)

            cls._jobs_[func.__name__] = {'fn': func, 'frequency': frequency}

            return func
        return wrapper


if __name__ == '__main__':
    @Sisyphus.register(1)
    def echo():
        print('echo ...')

    sisyphus = Sisyphus()
    sisyphus()
