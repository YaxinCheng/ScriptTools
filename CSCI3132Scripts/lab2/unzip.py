#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
import os, sys, subprocess

if len(sys.argv) < 2:
    print("Use with a directory path")
    sys.exit(2)
for name in filter(lambda name: ' - ' in name, os.listdir(sys.argv[1])):
    components = name.split(' - ')
    uploader = components[1]
    name_components = uploader.split(' ')
    first, last = name_components[0], ' '.join(name_components[1:])
    os.rename(name, last + ' ' + first + '.zip')

print("Rename finished")
errors = []

if len(sys.argv) > 2 and sys.argv[2] == '-u':
    for name in filter(lambda name: name.endswith('.zip'), os.listdir(sys.argv[1])):
        try:
            subprocess.check_output(['unzip', name, '-d', name.replace('.zip', '')])
        except subprocess.CalledProcessError:
            errors.append(name)
    print('Finished unzip')
    print('Failed to unzip', len(errors))
    print(errors)
    
    for name in filter(lambda name: ' ' in name and not name.endswith('.zip'), os.listdir(sys.argv[1])):
        with open('schema', 'r') as schema:
            markingSchema = schema.readlines()
        with open(os.path.join(name, 'score.txt'), 'w') as score:
            score.write(''.join(markingSchema))
