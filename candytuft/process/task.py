import logging

from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from abc import abstractmethod
from queue import Queue, Empty
from time import sleep

logger = logging.getLogger("candytuft.process.task")


class Task:
	@abstractmethod
	def __call__(self, *args, **kwargs):
		pass

	@property
	@abstractmethod
	def name(self) -> str:
		pass

class TaskQueue:
	def __init__(self, concurrency_level=5):
		self._concurrency_level = concurrency_level
		self._in_progress_count = 0

		self._thread = Thread(name="queue_monitor", target=self._run)
		self._thread.daemon = True

		self._executor = ThreadPoolExecutor(concurrency_level, "queue_worker")
		self._tasks = Queue()

		self._thread.start()

	def add(self, task: Task):
		self._tasks.put_nowait(task)

	def _run(self):
		def _on_execute(task: Task):
			logger.debug("Executing task '%s'", task.name)
			try:
				task()
				logger.debug("Task '%s' successfully completed", task.name)
			except:
				logger.exception("Unexpected exception while executing task '%s' - it is suppressed", task.name)

		# noinspection PyUnusedLocal
		def _on_task_done(future):
			self._in_progress_count -= 1
			self._tasks.task_done()

		while True:
			try:
				if self._in_progress_count == self._concurrency_level:
					sleep(1)
					continue

				task = self._tasks.get(timeout=1)
				self._in_progress_count += 1
				self._executor.submit(lambda: _on_execute(task)).add_done_callback(_on_task_done)
			except Empty:
				pass
