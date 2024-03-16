from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import time
import shutil
import os

if len(sys.argv) < 4:
    print("USAGE: %s source_path target_path log_file" % sys.argv[0])
    exit(1)

source_path = sys.argv[1]
target_path = sys.argv[2]
log_file = sys.argv[3]


def log_record(file_path):
    with open(log_file, "a") as f:
        f.write(file_path + "\n")


def is_synced(file_path):
    try:
        with open(log_file, "r") as f:
            return file_path in f.read().splitlines()
    except FileNotFoundError:
        return False


def deal_file(file_path):
    print("deal %s" % file_path)
    target_file_path = file_path.replace(source_path, target_path)
    flag = "%s#%s" % (file_path, target_file_path)
    if not is_synced(flag):
        target_dir_path = os.path.dirname(target_file_path)
        os.makedirs(target_dir_path, exist_ok=True)
        print("%s sending to %s" % (file_path, target_file_path))
        shutil.copy2(file_path, target_file_path)
        log_record(flag)
    else:
        print("%s sent" % file_path)


class MyHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        try:
            if event.event_type == 'created' or event.event_type == 'moved':
                if event.event_type == 'created':
                    file_path = event.src_path
                else:
                    file_path = event.dest_path
                deal_file(file_path)

        except Exception as e:
            print(e)


folder_path = source_path
event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, folder_path, recursive=True)
observer.start()

print("=================sync start=================")
print("**************CTRL+C to stop!***************")

for root, dirs, files in os.walk(source_path):
    for file in files:
        file_path = os.path.join(root, file)
        deal_file(file_path)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
print("=================sync   end=================")
observer.join()
