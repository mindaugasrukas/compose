from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from .. import __version__
import datetime
from docker import version as docker_py_version
import os
import platform
import subprocess
import ssl
from .docker_client import docker_client


def yesno(prompt, default=None):
    """
    Prompt the user for a yes or no.

    Can optionally specify a default value, which will only be
    used if they enter a blank line.

    Unrecognised input (anything other than "y", "n", "yes",
    "no" or "") will return None.
    """
    answer = raw_input(prompt).strip().lower()

    if answer == "y" or answer == "yes":
        return True
    elif answer == "n" or answer == "no":
        return False
    elif answer == "":
        return default
    else:
        return None


# http://stackoverflow.com/a/5164027
def prettydate(d):
    diff = datetime.datetime.utcnow() - d
    s = diff.seconds
    if diff.days > 7 or diff.days < 0:
        return d.strftime('%d %b %y')
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{0} days ago'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{0} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{0} minutes ago'.format(s / 60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{0} hours ago'.format(s / 3600)


def mkdir(path, permissions=0o700):
    if not os.path.exists(path):
        os.mkdir(path)

    os.chmod(path, permissions)

    return path


def find_candidates_in_parent_dirs(filenames, path):
    """
    Given a directory path to start, looks for filenames in the
    directory, and then each parent directory successively,
    until found.

    Returns tuple (candidates, path).
    """
    candidates = [filename for filename in filenames
                  if os.path.exists(os.path.join(path, filename))]

    if len(candidates) == 0:
        parent_dir = os.path.join(path, '..')
        if os.path.abspath(parent_dir) != os.path.abspath(path):
            return find_candidates_in_parent_dirs(filenames, parent_dir)

    return (candidates, path)


def split_buffer(reader, separator):
    """
    Given a generator which yields strings and a separator string,
    joins all input, splits on the separator and yields each chunk.

    Unlike string.split(), each chunk includes the trailing
    separator, except for the last one if none was found on the end
    of the input.
    """
    buffered = str('')
    separator = str(separator)

    for data in reader:
        buffered += data
        while True:
            index = buffered.find(separator)
            if index == -1:
                break
            yield buffered[:index + 1]
            buffered = buffered[index + 1:]

    if len(buffered) > 0:
        yield buffered


def call_silently(*args, **kwargs):
    """
    Like subprocess.call(), but redirects stdout and stderr to /dev/null.
    """
    with open(os.devnull, 'w') as shutup:
        return subprocess.call(*args, stdout=shutup, stderr=shutup, **kwargs)


def is_mac():
    return platform.system() == 'Darwin'


def is_ubuntu():
    return platform.system() == 'Linux' and platform.linux_distribution()[0] == 'Ubuntu'


def get_version_info(scope):
    versioninfo = 'docker-compose version: %s' % __version__
    client = docker_client()
    if scope == 'compose':
        return versioninfo
    elif scope == 'full':
        return versioninfo + '\n' \
            + "docker-py version: %s\n" % docker_py_version \
            + "Client API version: %s\n" % client.version \
            + "%s version: %s\n" % (platform.python_implementation(), platform.python_version()) \
            + "OpenSSL version: %s" % ssl.OPENSSL_VERSION
    else:
        raise RuntimeError('passed unallowed value to `cli.utils.get_version_info`')
