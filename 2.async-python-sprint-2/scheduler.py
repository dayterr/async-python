import json
import logging
import os
from typing import List, TypeVar

from job import Job

T = TypeVar('T')


class Scheduler:
    count_tasks = 0
    dir_names = ['done', 'planned', 'fwe']

    def __init__(self, pool_size: int = 10):
        self.jobs = []
        self.pending = []
        self.pool_size = pool_size
        self.create_dirs()
        self.restart()

    def schedule(self, task):
        pass

    def run(self, job: Job):
        if self.count_tasks < 10:
            if job.dependencies:
                job.run_with_dependencies()
            else:
                job.run()
        else:
            self.pending.append(job)
            job.write_to_file('planned')

    def new(self, command: str, start_at: str = "",
            max_working_time: int = -1, tries: int = 0,
            dependencies: List[T] = []) -> Job:
        """Создает новый экземпляр класса Job и добавляет его в список задач"""
        job = Job(command, start_at, max_working_time, tries, dependencies)
        self.jobs.append(job)
        return job

    def create_dirs(self):
        """Создаёт директории для файлов задач"""
        for name in self.dir_names:
            cmd = f'mkdir {name}'
            code = os.system(cmd)
            if code != 0:
                msg = f'Директория {name} уже создана'
                logging.info(msg)

    def restart(self):
        """Восстанавливает задачи из файлов задач при перезапуске"""
        for filename in os.listdir('planned'):
            with open(os.path.join('planned', filename)) as file:
                data = json.load(file)
                tries = data.get('tries', 0)
                max_working_time = data.get('max_working_time', -1)
                job = Job(data['command'], tries=tries,
                          max_working_time=max_working_time)
                self.jobs.append(job)
