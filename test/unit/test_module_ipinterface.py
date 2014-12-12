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
import sys
import os
import unittest
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))

from mock import Mock

from testlib import get_fixture, function, random_int
from testlib import EapiConfigUnitTest

import pyeapi.modules.ipinterfaces

class TestModuleIpinterfaces(EapiConfigUnitTest):

    INTERFACES = ['Ethernet1', 'Ethernet1/1', 'Vlan1234', 'Management1',
                  'Port-Channel1']

    def __init__(self, *args, **kwargs):
        super(TestModuleIpinterfaces, self).__init__(*args, **kwargs)
        self.instance = pyeapi.modules.ipinterfaces.instance(None)

    def test_getall(self):
        fixture = get_fixture('ipinterfaces.json')
        self.eapi.enable.return_value = json.load(open(fixture))
        result = self.instance.getall()
        self.eapi.enable.assert_called_with('show ip interfaces')
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 3)

    def test_instance_functions(self):
        for intf in self.INTERFACES:
            for name in ['create', 'delete']:
                if name == 'create':
                    cmds = ['interface %s' % intf, 'no switchport']
                elif name == 'delete':
                    cmds = ['interface %s' % intf, 'no ip address',
                            'switchport']
                func = function(name, intf)
                self.eapi_positive_config_test(func, cmds)

    def test_set_address_with_value(self):
        for intf in self.INTERFACES:
            value = '1.2.3.4/5'
            cmds = ['interface %s' % intf, 'ip address 1.2.3.4/5']
            func = function('set_address', intf, value)
            self.eapi_positive_config_test(func, cmds)

    def test_set_address_with_no_value(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'no ip address']
            func = function('set_address', intf)
            self.eapi_positive_config_test(func, cmds)

    def test_set_address_with_default(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'default ip address']
            func = function('set_address', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

    def test_set_mtu_with_values(self):
        for intf in self.INTERFACES:
            value = random_int(68, 9214)
            cmds = ['interface %s' % intf, 'mtu %s' % value]
            func = function('set_mtu', intf, value)
            self.eapi_positive_config_test(func, cmds)

    def test_set_mtu_with_no_value(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'no mtu']
            func = function('set_mtu', intf)
            self.eapi_positive_config_test(func, cmds)

    def test_set_mtu_default(self):
        for intf in self.INTERFACES:
            cmds = ['interface %s' % intf, 'default mtu']
            func = function('set_mtu', intf, default=True)
            self.eapi_positive_config_test(func, cmds)

if __name__ == '__main__':
    unittest.main()


