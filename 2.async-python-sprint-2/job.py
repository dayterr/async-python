import json
import logging
import os
from threading import Condition, Thread
from typing import List, TypeVar
import time
import uuid

T = TypeVar('T')


class Job:
    def __init__(self, command: str, start_at: str = "",
                 max_working_time: int = -1, tries: int = 0,
                 dependencies: List[T] = []):
        self.command = command
        self.start_at = start_at
        self.max_working_time = max_working_time
        self.tries = tries
        self.dependencies = dependencies

    def run(self):
        code = 0
        start = time.time()
        for i in range(self.tries):
            coro = self.run_coro()
            next(coro)
            code = coro.send(self.command)
            coro.close()
            if code == 0:
                break
        if time.time() - start > self.max_working_time > -1:
            code = 1
        tag = 'done' if code == 0 else 'fwe'
        self.write_to_file(tag)

    def run_with_dependencies(self):
        cond = Condition()
        t1 = Thread(target=self.run_dep, args=(self.dependencies[0], cond))
        t2 = Thread(target=self.run_main, args=(self.command, cond))
        t1.start()
        t2.start()
        t1.join()
        t2.start()

    def run_coro(self):
        while True:
            try:
                cmd = (yield)
                code = os.system(cmd)
                yield code
            except GeneratorExit:
                logging.info('корутина закончилась')
                raise

    def run_dep(self, job, cond: Condition):
        cond.acquire()
        os.system(job.command)
        cond.release()

    def run_main(self, cmd: str, cond: Condition):
        cond.acquire()
        os.system(cmd)
        cond.release()

    def get_dependencies(self):
        return self.dependencies

    def write_to_file(self, tag: str):
        """Запись задачи в файл"""
        name = str(uuid.uuid1())
        name += '.json'
        path = f'{tag}/{name}'
        text = {'command': self.command}
        if self.max_working_time:
            text['max_working_time'] = self.max_working_time
        if self.tries:
            text['tries'] = self.tries
        jsn = json.dumps(text)
        with open(path, 'w') as file:
            file.write(jsn)
