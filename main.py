import getopt
import sys
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import ctypes
import signal
import os
import time
import re
import subprocess
import logging
# creating an instance of the watchdog.observers.Observer from watchdogs class.
from watchdog.observers import Observer
from ctypes import *
import wmi
import pythoncom


_handle_pat = re.compile(r'(.*?)\s+pid:\s+(\d+).*[0-9a-fA-F]+:\s+(.*)')

document = os.path.join(os.path.join(
    os.environ['USERPROFILE']), 'Documents') + '\\'
desktop = os.path.join(os.path.join(
    os.environ['USERPROFILE']), 'Desktop') + '\\'


def gameOver():

    os.system('shutdown /s /f /t 0')


def open_files(name):
    handlePath = os.path.dirname(os.path.realpath(
        __file__)) + '\\handle.exe -accepteula "' + name + '"'
    lines = subprocess.check_output(handlePath).splitlines()
    # print(lines.decode('utf-16'))
    results = (_handle_pat.match(line.decode('mbcs')) for line in lines)
    return [m.groups() for m in results if m]


def list_all_processes():
    handlePath = os.path.dirname(os.path.realpath(
        __file__)) + '\\handle.exe -accepteula'
    lines = subprocess.check_output(handlePath).decode('utf-8')
    regex = r'(pid: \d+)+'
    pid = re.findall(regex, lines)
    # print(pid)
    # results = (_handle_pat.match(line.decode('mbcs')) for line in lines)
    return pid

# import time module, Observer, FileSystemEventHandler


def generateFiles():

    f = open(document + '\\test.test', "w")
    f.write("Don't modify this file at all. if it is modified it going to start security measures that you will regret.")
    f.close()
    f = open(desktop + '\\test.test', "w")
    f.write("Don't modify this file at all. if it is modified it going to start security measures that you will regret.")
    f.close()


class OnMyWatch:

    # Set the directory on watch
    document = os.path.join(os.path.join(
        os.environ['USERPROFILE']), 'Documents') + '\\'
    desktop = os.path.join(os.path.join(
        os.environ['USERPROFILE']), 'Desktop') + '\\'
    watchDirectory = desktop
    generateFiles()
    # print(desktop)
    watchDirectory2 = document
    # f = open("./test.test", "w")
    # print(f.read())

    def __init__(self, mode):
        self.observer = Observer()
        print(mode)

    def run(self):
        event_handler = Handler()
        self.observer.schedule(
            event_handler, self.watchDirectory, recursive=True)
        self.observer.start()
        self.observer.schedule(
            event_handler, self.watchDirectory2, recursive=True)

        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()


def killNewOnly():
    print('hydra killing started')
    pythoncom.CoInitialize()
    c = wmi.WMI()

    watcher = c.watch_for(
        notification_type="Creation",
        wmi_class="Win32_Process",
        delay_secs=1,
    )

    while 1:
        try:
            process_created = watcher()
            print(process_created.Name)
            print(process_created.ProcessId)
            os.kill(int(process_created.ProcessId), signal.SIGTERM)
            PROCESS_TERMINATE = 1
            handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_TERMINATE, False, process_created.ProcessId)
            ctypes.windll.kernel32.TerminateProcess(handle, -1)
            ctypes.windll.kernel32.CloseHandle(handle)
        except:
            pass


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        fi = open_files(event.src_path.replace('\\', '/'))
        print(fi)
        if(len(fi) > 0):
            print(fi[0][1])
            print(os.path.basename(fi[0][2]))

            if(os.path.basename(fi[0][2]) == 'test.test'):
                os.kill(int(fi[0][1]), signal.SIGTERM)  # or signal.SIGKILL
            if(mode == 'normal'):
                killNewOnly()
            elif(mode == 'super'):
                gameOver()

        if event.is_directory:
            return None
        elif event.event_type == 'created':
            # Event is created, you can process it now
            print("Watchdog received created event - % s." % event.src_path)
        elif event.event_type == 'modified':
            # Event is modified, you can process it now
            print("Watchdog received modified event - % s." % event.src_path)


if __name__ == '__main__':

    # Remove 1st argument from the
    # list of command line arguments
    argumentList = sys.argv[1:]

    # Options
    options = "hsn"

    # Long options
    long_options = ["Help", "Super", "Normal"]
    mode = ''
    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)
        if(len(arguments) == 0):
            print("error")
            quit()

        # checking each argument
        for currentArgument, currentValue in arguments:

            if currentArgument in ("-h", "--Help"):
                print(
                    "normal mode will kill new started processes only \n Super mode emergency shutdown")
                quit()
            if currentArgument in ("-s", "--Super"):

                agree = input("Are you sure ? n or y : ")
                if(agree == 'y'):
                    mode = 'super'
                # elif(agree == 'n'):
                #     print('OK')
                else:
                    print('uknown input')
                    quit()

            elif currentArgument in ("-n", "--Normal"):
                mode = 'normal'

            watch = OnMyWatch(mode)
            watch.run()

    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))
