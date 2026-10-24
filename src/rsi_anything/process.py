"""后台命令超时或被取消时，清理它启动的子进程。"""
from __future__ import annotations

import os
import signal
import subprocess


def run(command, *, timeout, input=None, stdin=None, **kwargs):
    if input is not None:
        stdin = subprocess.PIPE
    process = subprocess.Popen(command, stdin=stdin, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True,
                               start_new_session=os.name == "posix", **kwargs)
    try:
        stdout, stderr = process.communicate(input, timeout=timeout)
    except BaseException:
        # POSIX 的独立进程组包含包装程序及其子进程，父进程先退出也能清理。
        if os.name == "posix":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:
            process.kill()
        process.communicate()
        raise
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
