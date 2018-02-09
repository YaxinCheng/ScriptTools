from threading import Thread, Lock
from queue import Queue
import os, requests, re

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

    def __init__(self, queue):
        Thread.__init__(self, daemon=True)
        self.queue = queue

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
            last = url
            count = self._process(url)
            print('{} images downloaded. {} URLs in the queue'.format(count, self.queue.qsize()))
            url = self.queue.get()

queue = Queue()
threads = [DLThread(queue) for _ in range(5)]
for thread in threads: thread.start()

last = os.popen('pbpaste', 'r').read()
urlPattern = re.compile('http:\/\/.*?')
while True:
    try:
        text = os.popen('pbpaste', 'r').read()
        if not text or text == last or not urlPattern.match(text): continue
        last = text
        queue.put(text)
    except KeyboardInterrupt:
        break
