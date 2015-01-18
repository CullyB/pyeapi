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
import re

from collections import Callable, Mapping

from pyeapi.eapilib import CommandError

BLOCK_END_RE = re.compile(r'^[^\s]')


class BaseEntity(object):
    """Base class for all resources to derive from

    This BaseResource class should not be directly instatiated.  It is
    designed to be implemented by all resource classes to provide common
    methods.

    Args:
        node (Node): An instance of Node

    Attributes:
        node (Node): The node instance this resource will perform operations
            against for configuration
        config (Config): Returns an instance of Config with the nodes
            current running configuration
        error (CommandError): Holds the latest CommandError exception
            instance if raised

    """
    def __init__(self, node, autorefresh=False):
        self.node = node
        self.autorefresh = autorefresh
        self.properties = dict()

    @property
    def config(self):
        return self.node.running_config

    @property
    def error(self):
        return self.node.connection.error

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        elif name in self.__dict__['properties']:
            return self.__dict__['properties'][name]
        else:
            super(BaseEntity, self).__getattr__(name)

    def add_property(self, name, cls):
        self.properties[name] = cls(self.node)

    def get_block(self, parent):
        match = re.search(r'^%s$' % parent, self.config, re.M)
        if not match:
            return None
        block_start, line_end = match.regs[0]

        match = re.search(r'^[^\s]', self.config[line_end:], re.M)
        if not match:
            return None
        _, block_end = match.regs[0]

        block_end = line_end + block_end

        return self.config[block_start:block_end]

    def configure(self, commands):
        """Sends the commands list to the node in config mode

        This method performs configuration the node using the array of
        commands specified.   This method wraps the configuration commands
        in a try/except block and stores any exceptions in the error
        property.

        Args:
            commands (list): A list of commands to be sent to the node in
                config mode

        Returns:
            True if the commands are executed without exception otherwise
                False is returned
        """
        try:
            self.node.config(commands)
            return True
        except CommandError:
            return False


class Entity(BaseEntity, Callable):

    def __call__(self):
        return self.get()

    def get(self):
        raise NotImplementedError


class EntityCollection(BaseEntity, Mapping):

    def __call__(self):
        return self.getall()

    def __getitem__(self, value):
        return self.get(value)

    def __len__(self):
        return len(self.getall())

    def __iter__(self):
        return iter(self.getall())

    def getall(self):
        raise NotImplementedError

    def get(self, name, default=None):
        raise NotImplementedError


