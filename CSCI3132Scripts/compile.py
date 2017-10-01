import os, sys, subprocess

if len(sys.argv) < 2:
    print("Use with a directory path")
    sys.exit(2)
errors = []
for name in filter(lambda name: name.endswith('.cpp'), os.listdir(sys.argv[1])):
    try:
        subprocess.check_output(['g++', name, '-o', name.replace('.cpp', '.out'), '-std=c++11'])
    except subprocess.CalledProcessError:
        errors.append(name)
print("Finished compile")
print("Failed to compile,", len(errors))
print(errors)
