from Queue import Queue, Empty
from threading import Thread
from Adafruit_PCA9685 import PCA9685
from sys import stderr
from math import ceil, fabs

class LightingWorker(Thread):
    def __init__(self, queue):
        super(LightingWorker, self).__init__()
        self.queue = queue
        self.pwm = PCA9685()
        self.pwm.set_pwm_freq(600)

        self.current = {}
        self.wanted = {}
        self.rates = {}

    def run(self):
        print("Worker thread running")
        while True:
            self.loop()

    def loop(self):
        delay = 1

        for channel in sorted(self.wanted):
            current_level = self.current.get(channel, 0)
            wanted_level = self.wanted.get(channel)
            rate = self.rates.get(channel, 1)

            if wanted_level < current_level:
                rate *= -1

            rate /= 20.0

            if wanted_level == current_level:
                self.wanted.pop(channel)
                self.rates.pop(channel)
                next
            elif fabs(wanted_level - current_level) <= fabs(rate):
                current_level = wanted_level
            else:
                current_level = current_level + rate
                delay = .05

            self.scale(channel, current_level)
            self.current[channel] = current_level
            stderr.write("%s=%.2f " % (channel, current_level))

        stderr.write("        \r")

        try:
            message = self.queue.get(True, delay)
        except Empty:
            pass
        else:
            channel = message.get('channel')
            level = message.get('level')
            rate = message.get('rate')

            self.wanted[channel] = level
            self.rates[channel] = rate

            self.queue.task_done()

    def scale(self, channel, level):
        scaled = int(ceil(pow(2, level / 100.0 * 12) - 1))
        self.pwm.set_pwm(channel, 0, scaled)


queue = Queue()
worker = LightingWorker(queue)
worker.setDaemon(True)
worker.start()

def set(channel, level, rate):
    queue.put({
        "channel": channel,
        "level": level,
        "rate": rate
    })
