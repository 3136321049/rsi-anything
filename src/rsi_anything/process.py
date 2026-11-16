"""Clean up the child processes a background command started when it times out or is cancelled."""
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
        # On POSIX the separate process group holds the wrapper and its children, so cleanup works even if the parent exits first.
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
