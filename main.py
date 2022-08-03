import ctypes
import signal
import os
import time
import re
import subprocess
import logging
from watchdog.observers import Observer  #creating an instance of the watchdog.observers.Observer from watchdogs class.
from ctypes import *
import wmi
import pythoncom



_handle_pat = re.compile(r'(.*?)\s+pid:\s+(\d+).*[0-9a-fA-F]+:\s+(.*)')

def open_files(name):
    """return a list of (process_name, pid, filename) tuples for
       open files matching the given name."""
    lines = subprocess.check_output('handle.exe -accepteula "%s"' % name).splitlines()
    # print(lines.decode('utf-16'))
    results = (_handle_pat.match(line.decode('mbcs')) for line in lines)
    return [m.groups() for m in results if m]

# import time module, Observer, FileSystemEventHandler
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class OnMyWatch:
    # Set the directory on watch
    watchDirectory = "./"
    # f = open("./test.test", "w")
    # print(f.read())
    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive = True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()


def killThemAll():
    print('hydra killing started')
    pythoncom.CoInitialize()
    c = wmi.WMI ()

    watcher = c.watch_for (
    notification_type="Creation",
    wmi_class="Win32_Process",
    delay_secs=2,
    )

    while 1:
        process_created = watcher()
        print(process_created.Name)
        print(process_created.ProcessId)
        PROCESS_TERMINATE = 1
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, process_created.ProcessId)
        ctypes.windll.kernel32.TerminateProcess(handle, -1)
        ctypes.windll.kernel32.CloseHandle(handle)

class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        fi = open_files(event.src_path.replace('\\','/'))
        print(len(fi))
        if(len(fi) > 0):
            print(fi[0][1])
            os.kill(int(fi[0][1]), signal.SIGTERM) #or signal.SIGKILL 
            killThemAll()
        
        # print(event.src_path.replace('/','\\'))
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            # Event is created, you can process it now
            print("Watchdog received created event - % s." % event.src_path)
        elif event.event_type == 'modified':
            # Event is modified, you can process it now
            print("Watchdog received modified event - % s." % event.src_path)
            

if __name__ == '__main__':
    watch = OnMyWatch()
    watch.run()
