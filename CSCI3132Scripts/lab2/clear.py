#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
import os, sys, subprocess, shutil

if len(sys.argv) < 2:
    print("Use with a directory path")
    sys.exit(2)
for name in filter(lambda name: ' ' in name, os.listdir(sys.argv[1])):
    if os.path.isdir(name):
        shutil.rmtree(name)
