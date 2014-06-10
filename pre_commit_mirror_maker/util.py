from __future__ import unicode_literals

import subprocess


def from_utf8(s):
    if type(s) is bytes:
        return s.decode('utf-8')
    else:
        return s


def get_output(*cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    assert not proc.returncode, (proc.returncode, stdout, stderr)
    return from_utf8(stdout)
