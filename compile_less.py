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
        parent_dir = (event.src_path.split('\\'))[-2]

        if event.src_path[-5:] == '.less' and parent_dir in files_to_compile:
            for key, value in files_to_compile.iteritems():
                files = value.split(',')
                for f in files:
                    command_arg = '{0}\\less\\{1}\\{2}.less > {0}\\css\\{1}\\{2}.css'.format(path, key,
                                                                                             f.strip())
                    call('lessc ' + command_arg, shell=True)

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