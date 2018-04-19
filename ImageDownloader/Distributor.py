#!/usr/local/bin/python
import os, sys, re, time
from threading import Lock
from Threads import SeekerThread, DLThread, ClipboardThread
from queue import Queue

maxThread = 10
#downloadPath = '/Volumes/Seagate Backup Plus Drive/Down/Hee/'
downloadPath = '/Users/cheng/Downloads/images/'
downloadedCount = 0
taskSize = 0

def downProg():
    global downloadedCount, taskSize
    downloadedCount += 1
    print('\rDownloaded: {}/{}...'.format(downloadedCount, taskSize),
            end='\r')

def clipboardProg(url):
    print('\r\033[KURL added', end='\r')

def seekerProg(num):
    global taskSize
    taskSize += num

nameIndex = -1
def getFileName():
    global nameIndex
    if nameIndex == -1:
        fileNames = os.listdir(downloadPath)
        nameIndex = len(fileNames)
        if fileNames and fileNames[0] == '.DS_Store': nameIndex -= 1
    else:
        nameIndex += 1
    return str(nameIndex) + '.jpg'

countDown = None
def autoClose():
    global countDown, downloadedCount
    if downloadedCount > 0 and DLThread.runningCount == 0:
        if countDown is None:
            print('\nNo action detected, system will exit after 10s',
                    end='\r')
            countDown = time.time()
        elif time.time() - countDown >= 10:
            print('\r\033[KSystem exit')
            sys.exit(0)
        time.sleep(1)
    else: countDown = None

if __name__ == '__main__':
    rawURLs, imgURLs = Queue(), Queue()# URLs from clipboard; URLs extracted
    taskQueue = Queue()# formatted tasks (url, download path with file name)

    clipboard = ClipboardThread(rawURLs,
            lambda c: re.match('https?:\/\/.*?', c), clipboardProg)
    seeker = SeekerThread(rawURLs, imgURLs,
            lambda c: re.findall('http:\/\/.*?mo.*?\.jpg', c), seekerProg)
    clipboard.start()
    seeker.start()
    dlthreads = None
    print('System is on, please copy URLs...')
    while True:
        try:
            autoClose()
            for _ in range(imgURLs.qsize()):
                taskQueue.put((imgURLs.get(), downloadPath + getFileName()))

            if dlthreads is None:
                dlthreads = [DLThread(taskQueue, downProg) for _ in
                        range(max(maxThread, taskQueue.qsize()))]
                for thread in dlthreads: thread.start()
            elif len(dlthreads) < maxThread and taskQueue.qsize() >= maxThread:
                prev = len(dlthreads)
                dlthreads.extend([DLThread(taskQueue, downProg)
                    for _ in range(maxThread - prev)])
                for thread in dlthreads[prev:]: thread.start()
        except KeyboardInterrupt:
            break
