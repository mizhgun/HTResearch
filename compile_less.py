import time
import os
from subprocess import call
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class CompileLessHandler(FileSystemEventHandler):
    # called on directory or file change
    def on_modified(self, event):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HTResearch\\WebClient\\WebClient\\static')
        if event.src_path[-5:] == '.less':
            path_split = event.src_path.split('\\')
            parent_directory = path_split[-2]
            less_file = path_split[-1]
            css_file = less_file.replace('.less', '.css')
            command_arg = '{0}\less\\{1}\\{2} > {3}\\css\\{4}\\{5}'.format(path, parent_directory, less_file,
                                                                           path, parent_directory, css_file)
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