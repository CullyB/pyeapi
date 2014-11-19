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

api = None

def _parse_get(interface, flowcontrol):
    """Returns an interface as a set of key/value pairs

    Example:
        {
            "description": <string>
            "shutdown": [true, false],
            "flowcontrol_send": [on, off, desired],
            "flowcontrol_receive": [on, off, desired]
        }

    Args:
        interface (dict): set of attributes returned from eAPI command
                          "show interface <name>"
        flowcontrol (dict): set of attributes return from eAPI command
                            "show interface <name> flowcontrol"

    Returns:
        dict: A dict object containing the interface key/value pairs
    """
    response = dict()
    response['description'] = interface['description']
    response['shutdown'] = interface['interfaceStatus'] == 'disabled'
    response['flowcontrol_send'] = flowcontrol['txAdminState']
    response['flowcontrol_receive'] = flowcontrol['rxAdminState']
    return response

def get(name):
    """Returns a single interface attributes dict as a set of key/value pairs

    The interface attributes are parsed with _parse_get function

    Example
        {
            "Ethernet1": {...}
        }

    Args:
        name (str): the name of the interface to retieve from
                    the running-config

    Returns:
        dict: a dict object that represents the single interface
    """
    result = api.enable(['show interfaces %s' % name,
                         'show interfaces %s flowcontrol' % name])
    return { name: _parse_get(result[0]['interfaces'][name],
                              result[1]['interfaceFlowControls'][name]) }

def getall():
    """Returns all interfaces in a dict object.

    The interface attributes are parsed with _parse_get function

    Example:
        {
            "Ethernet1": {...},
            "Ethernet2": {...}
        }

    Returns:
        dict: a dict object containing all interfaces and attributes
    """
    result = api.enable(['show interfaces', 'show interfaces flowcontrol'])
    response = dict()
    for name in result[0]['interfaces'].keys():
        response[name] = _parse_get(result[0]['interfaces'][name],
                                    result[1]['interfaceFlowControls'][name])
    return response

def create(id):
    """Creates a new interface in EOS

    Args:
        id (str): The interface identifier.  It must be a full interface
                  name (ie Ethernet, not Et)

    Returns:
        bool: True if the create operation succeeds otherwise False
    """
    if id[0:2].upper() in ['ET', 'MA']:
        return False
    return api.config('interface %s' % id) == [{}]

def delete(id):
    """Deletes an interface from the running configuration

    Args:
        id (str): The interface identifier.  It must be a full interface
                  name (ie Ethernet, not Et)

    Returns:
        bool: True if the delete operation succeeds otherwise False
    """
    if id[0:2].upper() in ['ET', 'MA']:
        return False
    return api.config('no interface %s' % id) == [{}]

def default(id):
    """Defaults an interface in the running configuration

    Args:
        id (str): The interface identifier.  It must be a full interface
                  name (ie Ethernet, not Et)

    Returns:
        bool: True if the default operation succeeds otherwise False
    """
    return api.config('default interface %s' % id) == [{}]

def set_description(id, value=None, default=False):
    """Configures the interface description

    Args:
        id (str): The interface identifier.  It must be a full interface
                  name (ie Ethernet, not Et)
        value (str): The value to set the description to.
        default (bool): Specifies to default the interface description

    Returns:
        bool: True if the delete operation succeeds otherwise False
    """
    commands = ['interface %s' % id]
    if default:
        commands.append('default description')
    elif value is not None:
        commands.append('description %s' % value)
    else:
        commands.append('no description')
    return api.config(commands) == [{}, {}]

def set_shutdown(id, value=None, default=False):
    """Configures the interface shutdown state

    Args:
        id (str): The interface identifier.  It must be a full interface
                  name (ie Ethernet, not Et)
        value (bool): True if the interface should be in shutdown state
                      otherwise False
        default (bool): Specifies to default the interface description

    Returns:
        bool: True if the delete operation succeeds otherwise False
    """
    commands = ['interface %s' % id]
    if default:
        commands.append('default shutdown')
    elif value:
        commands.append('shutdown')
    else:
        commands.append('no shutdown')
    return api.config(commands) == [{}, {}]

def set_flowcontrol(id, direction, value=None, default=False):
    """Configures the interface flowcontrol value

    Args:
        id (str): The interface identifier.  It must be a full interface
                  name (ie Ethernet, not Et)
        direction (str): one of either 'send' or 'receive'
        value (bool): True if the interface should be in shutdown state
                      otherwise False
        default (bool): Specifies to default the interface description

    Returns:
        bool: True if the delete operation succeeds otherwise False
    """
    if direction not in ['send', 'receive']:
        return False
    commands = ['interface %s' % id]
    if default:
        commands.append('default flowcontrol %s' % direction)
    elif value:
        commands.append('flowcontrol %s %s' % (direction, value))
    else:
        commands.append('no flowcontrol %s' % direction)
    return api.config(commands) == [{}, {}]
