#
# Copyright (c) 2014, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import os
import sys
import imp
import pprint
import syslog
import collections

def import_module(name, path=None):
    parts = name.split('.')
    module_name = ''

    for index, part in enumerate(parts):
        module_name = part if index == 0 else '%s.%s' % (module_name, part)
        path = [path] if path is not None else path

        try:
            fhandle, path, descr = imp.find_module(part, path)
            if module_name in sys.modules:
                # since imp.load_module works like reload, need to be sure not
                # to reload a previously loaded module
                debug('returing module {} from cache'.format(module_name))
                mod = sys.modules[module_name]
            else:
                debug('loading new module {}'.format(module_name))
                mod = imp.load_module(module_name, fhandle, path, descr)
        finally:
            # lets be sure to clean up after ourselves
            if fhandle:
                fhandle.close()

    return mod

def load_module(name):
    try:
        mod = None
        if name in sys.modules:
            debug('returning {} from cache'.format(name))
        mod = sys.modules[name]
    except KeyError:
        debug('importing module {}'.format(name))
        mod = import_module(name)
    finally:
        if not mod:
            raise ImportError('unable to import module %s' % name)
        return mod

class ProxyCall(object):

    def __init__(self, proxy, method):
        self.proxy = proxy
        self.method = method

    def __call__(self, *args, **kwargs):
        return self.proxy(self.method, *args, **kwargs)


def parseconfig(config):
    cfg = dict()
    for element in config.strip().split('\n'):
        if element[0] != ' ':
            key = element
            cfg[key] = []
        elif element[0] == '!':
            continue
        else:
            cfg[key].append(element.strip())
    return cfg

def islocalconnection():
    return os.path.exists('/etc/Eos-release')

def pp(text):
    pprint.pprint(text)

def debug(text):
    if islocalconnection():
        syslog.openlog('pyeapi')
        syslog.syslog(syslog.LOG_NOTICE, str(text))

def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data
