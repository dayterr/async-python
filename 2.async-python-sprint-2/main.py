from scheduler import Scheduler

if __name__ == '__main__':
    scheduler = Scheduler()
    job = scheduler.new('touch t.txt')
    scheduler.run(job)
