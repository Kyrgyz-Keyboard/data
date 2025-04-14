from typing import Any

from multiprocessing.synchronize import Event as EventType
from multiprocessing.queues import Queue as QueueType
from multiprocessing import Process, Event

from contextlib import contextmanager, suppress, chdir
from queue import Empty as EmptyQueueException
import sys
import os


def mkpath(*paths: str) -> str:
    return os.path.normpath(os.path.join(*paths))


class PathMagic:
    def __init__(self, source_file_path: str):
        self.source_file_directory = os.path.dirname(os.path.abspath(source_file_path))
        # sys.path.remove(self.source_file_directory)

    def __call__(self, *paths: str) -> str:
        return mkpath(self.source_file_directory, *paths)

    @contextmanager
    def import_from(self, import_from_path: str):
        sys.path.append(mkpath(self.source_file_directory, import_from_path))
        try:
            yield
        finally:
            with suppress(ValueError):
                sys.path.remove(mkpath(self.source_file_directory, import_from_path))

    @contextmanager
    def chdir(self, *paths: str):
        with chdir(mkpath(self.source_file_directory, *paths)):
            yield


def write_file(path: str, data: str | bytes, append: bool = False, binary: bool = False):
    path = mkpath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(
        path,
        ('a' if append else 'w') + ('b' if binary else ''),
        encoding=(None if binary else 'utf-8')
    ) as file:
        file.write(data)


def print_async(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


class FileWriter:
    _queue: QueueType[tuple[tuple[Any], dict[str, Any]]]
    _stop_event: EventType
    _process: Process

    @classmethod
    def init(cls, queue):
        cls._queue = queue
        cls._stop_event = Event()

        cls._process = Process(
            target=cls._writer_worker,
            args=(cls._queue, cls._stop_event)
        )
        cls._process.start()

    @classmethod
    def bind_worker(cls, queue):
        cls._queue = queue

    @classmethod
    def _writer_worker(cls, queue, stop_event):
        while not stop_event.is_set() or not queue.empty():
            try:
                args, kwargs = queue.get(timeout=0.5)
            except EmptyQueueException:
                continue
            print_async('[FileWriter] Writing to', args[0])
            write_file(*args, **kwargs)
            print_async('[FileWriter] Finished writing to', args[0])

    @classmethod
    def write_file(cls, *args, **kwargs):
        print_async(f'[FileWriter] New task: write to {args[0]}. Tasks in queue: {cls._queue.qsize() + 1}')
        cls._queue.put((args, kwargs))

    @classmethod
    def stop(cls):
        print_async('[FileWriter] Termination requested, waiting for all writes to finish...')
        cls._stop_event.set()
        cls._process.join()
        print_async('[FileWriter] Stopped')


# def _test_worker(i):
#     from time import sleep
#     FileWriter.write_file(mkpath(f'../results/test/test_{i}.txt'), f'Worker {i}\n')
#     sleep(3)


# if __name__ == '__main__':
#     from multiprocessing import Manager, Pool
#     from time import sleep

#     manager = Manager()
#     queue = manager.Queue()

#     FileWriter.init(queue)

#     with Pool(initializer=FileWriter.bind_worker, initargs=(queue,)) as pool:
#         pool.map(_test_worker, range(10))
#         # pool.map_async(_test_worker, range(10))
#         sleep(1)
#         # FileWriter.stop()

#     FileWriter.stop()
