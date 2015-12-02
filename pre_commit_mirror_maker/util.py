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


def split_by_commas(maybe_s):
    """Split a string by commas, but allow escaped commas.
    - If maybe_s is falsey, returns an empty tuple
    - Ignore backslashed commas
    """
    if not maybe_s:
        return ()
    parts = []
    split_by_backslash = maybe_s.split(r'\,')
    for split_by_backslash_part in split_by_backslash:
        splitby_comma = split_by_backslash_part.split(',')
        if parts:
            parts[-1] += ',' + splitby_comma[0]
        else:
            parts.append(splitby_comma[0])
        parts.extend(splitby_comma[1:])
    return tuple(parts)
