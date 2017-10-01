import os, sys

if len(sys.argv) < 2:
    print("Use with a directory path")
    sys.exit(2)
for name in filter(lambda name: ' - ' in name, os.listdir(sys.argv[1])):
    components = name.split(' - ')
    uploader = components[1]
    name_components = uploader.split(' ')
    first, last = name_components[0], ' '.join(name_components[1:])
    os.rename(name, last + ' ' + first + '.cpp')

print("Rename finished")

