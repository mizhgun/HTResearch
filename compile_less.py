import time
import os
from subprocess import call
from HTResearch.Utilities.config import get_config_value
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class CompileLessHandler(FileSystemEventHandler):
    # called on directory or file change
    def on_modified(self, event):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HTResearch\\WebClient\\WebClient\\static')
        if event.src_path[-5:] == '.less':
            parent_directory = (event.src_path.split('\\'))[-2]
            # Could be a list of files to compile or a single
            files_to_compile = (get_config_value("LESS", parent_directory)).split(',')
            for f in files_to_compile:
                command_arg = '{0}\\less\\{1}\\{2}.less > {0}\\css\\{1}\\{2}.css'.format(path, parent_directory,
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