#!/usr/bin/env python3

import os
import sys
import time
import queue
import signal
import subprocess

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def main():

    proc = subprocess.Popen("ipython",
                            shell=False,
                            stdin=subprocess.PIPE)

    def send_cmd(cmd):

        proc.stdin.write(f"{cmd}\n".encode("utf8"))
        proc.stdin.flush()

    send_cmd("%load_ext autoreload")
    send_cmd("%autoreload 2")

    sp = sys.argv[1].split(".")
    module_name = ".".join(sp[:-1])
    func_name = sp[-1]

    send_cmd("import os")
    send_cmd("import traceback")
    send_cmd(f"import {module_name}")
    send_cmd("def loop_func():")
    send_cmd("    try:")
    send_cmd(f"        {module_name}.{func_name}()")
    send_cmd("        os._exit(0)")
    send_cmd("    except:")
    send_cmd("        print('\\n' + traceback.format_exc(), end='')")
    send_cmd("")
    send_cmd("loop_func()")

    update_queue = queue.Queue()

    class EventHandler(FileSystemEventHandler):

        def on_modified(self, event):

            if event.is_directory:
                return

            if event.src_path.endswith(".py"):
                update_queue.put(True)

    watch_dir = os.path.dirname(os.path.abspath(os.getcwd()))

    observer = Observer()
    observer.schedule(EventHandler(), watch_dir, recursive=True)
    observer.start()

    wait_time = 0.2
    debounce_time = 0.5

    last_request = None

    try:
        while proc.poll() is None:
            try:
                update_queue.get(timeout=0.5)
                last_request = time.time()
            except queue.Empty:
                pass

            if last_request is None:
                continue

            now = time.time()
            if now - last_request > debounce_time:
                proc.send_signal(signal.SIGINT)
                time.sleep(wait_time)
                send_cmd("loop_func()")
                last_request = None
    except BrokenPipeError:
        # in this case proc has finished
        pass
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
