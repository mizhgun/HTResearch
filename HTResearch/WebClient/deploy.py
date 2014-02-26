# This file is example of deploy.py
#
# Path to this file is configured in web.config:
#      <application name="django.project.x86" >
#        <environmentVariables>
#          <add name="DEPLOY_FILE" value="deploy.py" />
#          <add name="DEPLOY_LOG"  value="log\deploy.log" />
#        </environmentVariables>
#      </application>
#
# The file is executed once on the first request after every restart of IIS application.
# The file output is redirected to log file described in DEPLOG_LOG environment variable.
#

import sys
import os
import os.path


VIRTUALENV_EXE = os.path.join(os.path.dirname(sys.executable), 'scripts\\virtualenv.exe')
VIRTUALENV_NAME = 'venv'
DJANGO_PROJECT_NAME = 'project'
PROJECT_DIR = os.path.dirname(__file__)


def run(command, exit_on_error=True):
    print('\nRunning command: ' + command)
    status = os.system(command)
    if status != 0:
        sys.exit(status)


def django_manage(command):
    run(DJANGO_PROJECT_NAME + '\\manage.py ' + command)


def main():
    os.chdir(PROJECT_DIR)

    # update APPDATA env for pip
    #os.environ['APPDATA'] = os.path.join(PROJECT_DIR, PYTHON_MODULES_DIR)

    # create virtual environment
    if not os.path.exists(VIRTUALENV_NAME):
        run(VIRTUALENV_EXE + ' ' + VIRTUALENV_NAME)

    # install requirements to local user
    run('pip install --requirement=requirements.txt')

    # run manage.py syncdb --noinput
    django_manage('syncdb --noinput')

    # run manage.py migrate
    #django_manage('migrate')

    # collect static
    #django_manage('collectstatic --noinput')

    # that's all
    print "Bye!"


if __name__ == '__main__':
    main()
