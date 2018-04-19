from threading import Thread, Lock
import time, requests, os
from queue import Queue

class DLThread(Thread):
    runningCount = 0
    lock = Lock()

    def __init__(self, inputQueue, callback):
        '''
        inputQueue: a queue where the thread accepts downloading content: (URL, savePath)
        callback: a function to notify the distributer of completion
        '''
        Thread.__init__(self, daemon=True)

        self.inQueue = inputQueue
        self.callback = callback

    def run(self):
        while True:
            task = self.inQueue.get()
            if task is not None: url, path = task
            else: self.inputQueue.task_done(); break
            DLThread.lock.acquire()
            DLThread.runningCount += 1
            DLThread.lock.release()

            with open(path, 'wb') as imgFile:
                imgFile.write(requests.get(url).content)
            self.callback()

            DLThread.lock.acquire()
            DLThread.runningCount -= 1
            DLThread.lock.release()

class SeekerThread(Thread):
    def __init__(self, inputQueue, outputQueue, imgExtract, callback=None):
        '''
        inputQueue: contains the url where we need to find images
        outputQueue: put extracted image URLs to the queue
        imgExtract: a function takes in a string of source and returns image URLs
        '''
        Thread.__init__(self, daemon=True)
        self.inQueue = inputQueue
        self.outQueue = outputQueue
        self.imgExtract = imgExtract
        self.callback = callback

    def run(self):
        while True:
            url = self.inQueue.get()
            if url is None: break
            source = requests.get(url).text
            images = self.imgExtract(source)
            for image in images: self.outQueue.put(image)
            if self.callback: self.callback(len(images))

class ClipboardThread(Thread):
    def __init__(self, outputQueue, match, callback=None):
        '''
        outputQueue: a queue stores the copied content from clipboard
        match: a match function to choose the content with wanted format
        callback: a callback function
        '''
        Thread.__init__(self, daemon=True)
        self.visited = set()
        self.match = match
        self.outQueue = outputQueue
        self.callback = callback

    def run(self):
        while True:
            text = os.popen('pbpaste', 'r').read()
            if not text or text in self.visited or not self.match(text):
                time.sleep(1)
                continue
            self.visited.add(text)
            self.outQueue.put(text)
            if self.callback is not None: self.callback()
