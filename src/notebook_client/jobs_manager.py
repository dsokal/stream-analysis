import subprocess
import psutil
import signal


class JobsManager(object):
    def __init__(self):
        self.jobs = set()

    def start_job(self, msg):
        filename = msg["filename"]
        process = subprocess.Popen(["./run-job.sh", filename])
        self.jobs.add(process.pid)
        return {"status": "started", "pid": process.pid}

    def check_status(self, msg):
        pid = msg["pid"]
        if pid in self.jobs:
            return {"status": "running"}
        else:
            return {"status": "not found"}

    def stop_job(self, msg):
        pid = msg["pid"]
        if pid in self.jobs:
            self.kill_child_processes(pid)
            self.jobs.remove(pid)
            return {"status": "stopped"}
        else:
            return {"error": "job not found"}

    def kill_child_processes(self, parent_pid, sig=signal.SIGINT):
        try:
            parent = psutil.Process(parent_pid)
        except psutil.NoSuchProcess:
            return
        children = parent.children()
        for process in children:
            process.send_signal(sig)
