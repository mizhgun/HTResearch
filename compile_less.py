# compile_less.py
# Compiles LESS files (given in the config) to CSS files if:
#   1. A LESS file is changed
#   2. The LESS file's parent directory inside the LESS directory is a key in the config
#   3. The value of the config key is the correct filepath to the file that is to be compiled
#
# Assumptions: The LESS file changed is in the directory HTResearch\WebClient\WebClient\static\less

import time
import os
from subprocess import call
from HTResearch.Utilities.config import get_section_values
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class CompileLessHandler(FileSystemEventHandler):
    # Called on directory or file change
    def on_modified(self, event):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HTResearch\\WebClient\\WebClient\\static')

        # Get all the section values in a dictionary
        files_to_compile = get_section_values("LESS")
        if event.src_path[-5:] == '.less':
            # Get the path of the changed file and keep checking parent directories until the LESS directory,
            # if any of those parent directories are in the config, recompile
            src_path = event.src_path.split('\\')
            src_path.reverse()
            for directory in src_path[1:]:
                if directory in files_to_compile:
                    for key, value in files_to_compile.iteritems():
                        files = value.split(',')
                        for f in files:
                            command_arg = '{0}\\less\\{1}\\{2}.less > {0}\\css\\{1}\\{2}.css'.format(path, key,
                                                                                                     f.strip())
                            call('lessc ' + command_arg, shell=True)
                elif directory == 'less':
                    break

if __name__ == "__main__":
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HTResearch\\WebClient\\WebClient\\static\\less')
    event_handler = CompileLessHandler()
    observer = Observer()

    # Schedules watching a path
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()