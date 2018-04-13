from threading import Thread, Lock
from queue import Queue, Empty
import os, requests, re, time

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
    runningCount = 0
    countDownTime = None

    def __init__(self):
        Thread.__init__(self, daemon=True)

    def _process(self, url):
        print('Begin downloading:\n{}'.format(url))
        source = requests.get(url).text
        imgPattern = re.compile('http:\/\/.*?mo.*?\.jpg')
        imgs = imgPattern.findall(source)
        base = self.control.baseNum
        DLThread.lock.acquire()
        self.control.baseNum += len(imgs)
        DLThread.lock.release()
        print('\rDownloading... 0/{}'.format(len(imgs)), end='\r')
        for index, imgURL in enumerate(imgs):
            with open(self.control.fileName.format(base + index), 'wb') as img:
                img.write(requests.get(imgURL).content)
            print('\rDownloading... {}/{}'.format(index+1, len(imgs)),end='\r')
        return len(imgs)

    def run(self):
        url = self.queue.get()
        last = None
        while url != last:
            DLThread.lock.acquire()
            self.runningCount += 1
            DLThread.lock.release()
            last = url
            count = self._process(url)
            DLThread.lock.acquire()
            self.runningCount -= 1
            DLThread.lock.release()
            print('{} images downloaded. {} threads are downloading. {} URLs in the queue'.format(count, self.runningCount, self.queue.qsize()))
            while(True):
                if self.runningCount == 0 and self.queue.empty():
                    if self.countDownTime is None:
                        print('No process is running, system will exit after 10 second...')
                        self.countDownTime = time.time()
                    elif time.time() - self.countDownTime >= 10:
                        print('No process is running, system exit')
                        os._exit(0)
                try:
                    url = self.queue.get_nowait()
                    if url != last: break
                except Empty:
                    time.sleep(1)
                    continue

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
