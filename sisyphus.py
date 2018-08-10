#! /usr/bin/env python
#! using: utf-8
# Copyright (C) 2018-2018 cmj<cmj@cmj.tw>. All right reserved.

import time
import logging
import functools
import setproctitle
from multiprocessing import Process

class Sisyphus(object):
	_jobs_ = {}

	def __init__(cls, debug=False):
		fmt = '[%(asctime)-.19s] (%(filename)s#%(lineno)04d) - %(message)s'
		fmt = logging.Formatter(fmt)

		syslog = logging.StreamHandler()
		syslog.setFormatter(fmt)

		logger = logging.getLogger(cls.__class__.__name__)
		logger.setLevel(logging.DEBUG if debug else logging.WARNING)

		if not logger.handlers: logger.addHandler(syslog)
		logger = logging.LoggerAdapter(logger, {'app_name': cls.__class__.__name__})

		for attr in 'critical error warning info debug'.split():
			setattr(cls, attr, getattr(logger, attr))

	def __call__(cls, frequency=5):
		jobs = {}
		try:
			while True:
				for name in cls._jobs_:
					if name not in jobs or not jobs[name].is_alive():
						jobs[name] = Process(target=cls.worker, args=(name, ))
						jobs[name].start()
						cls.warning(f'new job `{name}` on PID#{jobs[name].pid}')
				time.sleep(frequency)
		except KeyboardInterrupt as e:
			for name in cls._jobs_:
				if name in jobs and jobs[name].is_alive():
					jobs[name].kill() if hasattr(jobs[name], 'kill') else jobs[name].terminate()
			cls.critical(f'Ctrl-C')

	def worker(cls, name):
		setproctitle.setproctitle(f'{name} ({cls._jobs_[name]["frequency"]})')
		while True:
			cls._jobs_[name]['fn'].__globals__['worker'] = cls
			cls._jobs_[name]['fn']()
			time.sleep(cls._jobs_[name]['frequency'])

	@property
	def jobs(cls):
		jobs = [f'- {job} ({item["fn"]})' for job, item in cls._jobs_.items()]
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
