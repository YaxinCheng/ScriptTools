import sys
import os
import argparse

mainParser = argparse.ArgumentParser(description='Manage app for Flask project')
subparser = mainParser.add_subparsers()

startproject = subparser.add_parser('startproject', help='Build flask proejct with preset templates')
startproject.add_argument('projectName', nargs='?', metavar='Project Name', help='Project Name')
startapp = subparser.add_parser('startapp', help='Build app for Flask project with templates')
startapp.add_argument('appName', metavar='App Name', help='App Name')
runserver = subparser.add_parser('runserver', help='Run server on the local machine')
runserver.add_argument('IP', nargs='?', help='ip address')
commit = subparser.add_parser('commit', help='Commit all files and push them to the remote repo')
commit.add_argument('message', metavar='message', help='Version info of the commit')
args = mainParser.parse_args() 

if 'projectName' in args:
    with open('main.py', 'w') as main: main.write('''from flask import Flask\nimport settings\n\napp = Flask(__name__)\n\nfor ia in settings.installedApps:\n    app.register_blueprint(ia)\nhost = '127.0.0.1' if settings.DEBUG else '0.0.0.0'\nif __name__ == '__main__':\n    app.run(host=host, port=8000, debug=settings.DEBUG, threaded=True)''')
    with open('db.py', 'w') as db: db.write('import os\n#Configure your db here')
    with open('settings.py', 'w') as settings: settings.write('import os\nDEBUG = True\n# Set up your db uri here\ninstalledApps = []')
elif 'appName' in args:
    curPath = os.path.dirname(os.path.realpath(__file__))
    appName = args.appName
    appPath = curPath + '/' + appName
    os.makedirs(appPath)
    os.makedirs(appPath + '/templates')
    with open(appPath + '/__init__.py', 'w') as init: init.write('') 
    with open(appPath + '/models.py', 'w') as models: models.write('')
    with open(appPath + '/forms.py', 'w') as forms: forms.write('')
    with open(appPath + '/views.py', 'w') as views: 
        views.write('from flask import request, render_template, abort, Blueprint, redirect, url_for\nfrom jinja2 import TemplateNotFound\n')
        views.write("from {app}.models import *\nfrom {app}.forms import *\n\n{app} = Blueprint('{app}', __name__, template_folder = 'templates')\n\n".format(app=appName))
        views.write("# Add your router functions below")
    with open(curPath + '/settings.py', 'a') as settings: settings.write('from {app} import views as {app}_views\ninstalledApps.append({app}_views.{app})\n'.format(app=appName))
elif 'IP' in args:
    os.system('python main.py')
elif 'message' in args:
    log = args.message
    os.system('git add .')
    os.system('git commit -m "%s"' % log)
    os.system('git push')
else:
    mainParser.print_help()
