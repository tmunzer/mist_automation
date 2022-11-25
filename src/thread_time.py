import time, sched
from threading import Thread
from libs.logger import Console
console = Console("time trig")


class TimeWorker(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.s = sched.scheduler(time.time, time.sleep)

    def run(self):
        self.s.enter(60, 1, self.do_something, (self.s,))
        self.s.run()

    def do_something(self, sc): 
        print("Doing stuff...")
        # do your stuff
        sc.enter(60, 1, self.do_something, (sc,))