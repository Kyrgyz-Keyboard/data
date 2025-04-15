from typing import no_type_check

from multiprocessing import Process, Event, Value, Lock, Queue
from contextlib import contextmanager, suppress, chdir
from concurrent.futures import ThreadPoolExecutor
from queue import Empty as EmptyQueueException
from time import sleep
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


def empty_file(path: str):
    path = mkpath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, 'w', encoding='utf-8') as file:
        file.write('')


def print_async(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


class FileWriter:
    _queue: Queue          # type: ignore
    _stop_event: Event     # type: ignore
    _process: Process
    _data_size: Value      # type: ignore
    _wait_lock: Lock       # type: ignore
    _pending_tasks: Value  # type: ignore
    _max_size: int = 1_000_000_000  # 1 GB
    _num_threads: int = 10

    @classmethod
    def init(cls):
        cls._queue = Queue()
        cls._stop_event = Event()
        cls._data_size = Value('i', 0)
        cls._wait_lock = Lock()
        cls._pending_tasks = Value('i', 0)

        cls._process = Process(
            target=cls._writer_worker,
            args=(cls._queue, cls._stop_event, cls._data_size),
        )
        cls._process.start()

        return (cls._queue, cls._data_size, cls._wait_lock, cls._pending_tasks)

    @classmethod
    def bind_worker(cls, queue, total_size, wait_lock, pending_tasks):
        cls._queue = queue
        cls._data_size = total_size
        cls._wait_lock = wait_lock
        cls._pending_tasks = pending_tasks

    @classmethod
    def _writer_worker(cls, queue, stop_event, total_size):
        active_writes_lock = Lock()
        active_writes_to: set[str] = set()

        def _write_task(args, kwargs, total_size):
            path, data, *args = args

            while True:
                with active_writes_lock:
                    need_wait = path in active_writes_to
                if not need_wait:
                    break
                sleep(1)

            with active_writes_lock:
                active_writes_to.add(path)

            # print_async('[FileWriter] Writing to', path)
            try:
                write_file(path, data, *args, **kwargs)
            except Exception as e:
                print_async(f'[FileWriter] Error writing to {path}: {e}')
            finally:
                active_writes_to.remove(path)
                with total_size.get_lock():
                    total_size.value -= len(data)
            # print_async('[FileWriter] Finished writing to', path)

        with ThreadPoolExecutor(max_workers=cls._num_threads) as executor:
            while not queue.empty() or not stop_event.is_set():
                try:
                    args, kwargs = queue.get(timeout=0.5)
                except EmptyQueueException:
                    continue
                # print_async('[FileWriter] Starting task:', args, kwargs)
                executor.submit(_write_task, args, kwargs, total_size)

    @classmethod
    @no_type_check
    def write_file(cls, path: str, data: str | bytes, *args, **kwargs):
        with cls._pending_tasks.get_lock():
            cls._pending_tasks.value += 1

        data_size = len(data)
        with cls._wait_lock:
            while cls._data_size.value and cls._data_size.value + data_size > cls._max_size:
                print_async(
                    '[FileWriter] Data queue too large, waiting... '
                    f'({cls._data_size.value} + {data_size} > {cls._max_size}, '
                    f'{cls._queue.qsize()} tasks in queue, {cls._pending_tasks.value} pending)'
                )
                sleep(1)

            with cls._data_size.get_lock():
                cls._data_size.value += data_size

        cls._queue.put(((path, data, *args), kwargs))

        # print_async(
        #     f'[FileWriter] New task: write to {path}. Tasks in queue: {cls._queue.qsize()}. '
        #     f'Total size of text: {cls._data_size.value} characters'
        # )

        with cls._pending_tasks.get_lock():
            cls._pending_tasks.value -= 1

    @classmethod
    @no_type_check
    def stop(cls):
        print_async('[FileWriter] Termination requested, waiting for all writes to finish...')
        while cls._pending_tasks.value:
            print_async(cls._pending_tasks.value)
            sleep(1)
        cls._stop_event.set()
        cls._process.join()
        assert cls._data_size.value == 0, (
            f'[FileWriter] Not all writes have finished. '
            f'Total size: {cls._data_size.value} characters'
        )
        print_async('[FileWriter] Stopped')


# def _test_worker(i):
#     FileWriter.write_file(mkpath(f'../results/test/test_{i}.txt'), f'Worker {i}\n')
#     # sleep(3)


# FileWriter._max_size = 40

# if __name__ == '__main__':
#     from multiprocessing import Pool

#     bind_args = FileWriter.init()

#     with Pool(processes=4, initializer=FileWriter.bind_worker, initargs=bind_args) as pool:
#         pool.map(_test_worker, range(10))
#         # pool.map_async(_test_worker, range(10))
#         # FileWriter.stop()

#     # sleep(1)

#     FileWriter.stop()
