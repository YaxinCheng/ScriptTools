from threading import Thread, Lock
from queue import Queue
import os, requests, re, time, sys

class fileControl:
    fileDir = '/Volumes/Seagate Backup Plus Drive/Down/Hee/'
    fileName = fileDir + '{}.jpg'

    def __init__(self):
        fileNames = os.listdir(fileControl.fileDir)
        if fileNames[0] == '.DS_Store': self.baseNum = len(fileNames) - 1
        else: self.baseNum = len(fileNames)

class DLThread(Thread):
    lock = Lock()
    control = fileControl()
    queue = Queue()
    runningCount = -1

    def __init__(self):
        Thread.__init__(self, daemon=True)

    def _process(self, url):
        print('Begin downloading:\n{}\n\n'.format(url))
        source = requests.get(url).text
        imgPattern = re.compile('http:\/\/.*?mo.*?\.jpg')
        imgs = imgPattern.findall(source)
        base = self.control.baseNum
        DLThread.lock.acquire()
        self.control.baseNum += len(imgs)
        DLThread.lock.release()
        for index, imgURL in enumerate(imgs):
            with open(self.control.fileName.format(base + index), 'wb') as img:
                img.write(requests.get(imgURL).content)
        return len(imgs)

    def run(self):
        url = self.queue.get()
        last = None
        while url != last:
            DLThread.lock.acquire()
            if self.runningCount == -1: self.runningCount == 0
            self.runningCount += 1
            DLThread.lock.release()
            last = url
            count = self._process(url)
            DLThread.lock.acquire()
            self.runningCount -= 1
            DLThread.lock.release()
            print('{} images downloaded. {} URLs in the queue'.format(count, self.queue.qsize()))
            url = self.queue.get()

threads = [DLThread() for _ in range(5)]
for thread in threads: thread.start()

last = os.popen('pbpaste', 'r').read()
urlPattern = re.compile('http:\/\/.*?')
while True:
    try:
        text = os.popen('pbpaste', 'r').read()
        if not text or text == last or not urlPattern.match(text):
            time.sleep(1)
            continue
        last = text
        DLThread.queue.put(text)
    except KeyboardInterrupt:
        break
