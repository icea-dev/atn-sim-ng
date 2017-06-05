#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
core_message_builder

CORE message builder

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

revision 0.1  2017/jun  matias
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/06"

# < import >---------------------------------------------------------------------------------------
from core.api import coreapi
from PyQt4 import QtCore

import logging
import os
import subprocess

module_logger = logging.getLogger('main_app.core_message_builder')

# < class CCoreMessageBuilder >--------------------------------------------------------------------
class CCoreMessageBuilder(QtCore.QObject):
    """
    Class responsible for creating the message and sending them to the CORE daemon.
    Uses coresendmsg.
    """


    # ---------------------------------------------------------------------------------------------
    def __init__(self, f_parent=None):
        """
        Constructor

        :param f_parent: the parent object.
        """

        super(CCoreMessageBuilder, self).__init__(f_parent)

        self.logger = logging.getLogger('main_app.core_message_builder.CCoreMessageBuilder')
        self.logger.info("Creating instance of CCoreMessageBuilder")

        self.home = os.environ.get('HOME')
        self.logger.info("HOME = %s" % self.home)


    # ---------------------------------------------------------------------------------------------
    def add_node(self, f_node_number, f_xpos, f_ypos, f_wlan_node_number, f_address_ip4, f_address_ip6):
        """
        Uses coresendmsg to add the node, create the link with the ADS-B cloud, and run the emane.

        :param f_node_number:
        :param f_xpos:
        :param f_ypos:
        :param f_wlan_node_number:
        :param f_address_ip4
        :param f_address_ip6
        :return:
        """

        l_node_name = "n" + str(f_node_number)

        self.logger.debug("Node name [%s] Postion (%s,%s)" % (l_node_name, f_xpos, f_ypos))

        l_arg_number = "number=" + str(f_node_number)
        l_arg_xpos = "xpos=" + str(int(f_xpos))
        l_arg_ypos = "ypos=" + str(int(f_ypos))
        l_arg_icon = "icon=" + self.home + "/atn-sim/configs/core/icons/aircraft.png"
        l_arg_node_name = "name=" + l_node_name

        self.logger.debug("Arguments [%s %s %s %s %s]" % (l_arg_number, l_arg_xpos, l_arg_ypos, l_arg_icon, l_arg_node_name))

        core_daemon = subprocess.Popen(['coresendmsg', 'node', 'flags=add', l_arg_number, 'type=0',
                                          l_arg_xpos, l_arg_ypos, 'model=aircraft', l_arg_icon,
                                          l_arg_node_name], stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)

        self.logger.debug(core_daemon.communicate())

        l_ip4_split = f_address_ip4.split('/')
        l_ip6_split = f_address_ip6.split('/')

        l_ip4 = l_ip4_split[0].split('.')
        l_ip6 = l_ip6_split[0].split(':')
        self.logger.debug("IPv6 split(:) %s" % l_ip6)

        l_arg_n1number = "n1number=" + str(f_wlan_node_number)
        l_arg_n2number = "n2number=" + str(f_node_number)
        l_arg_ip4 = "if2ip4="+l_ip4[0]+"."+l_ip4[1]+"."+l_ip4[2]+"."+str(f_node_number)
        l_arg_ip4mask = "if2ip4mask=" + l_ip4_split[1]
        l_arg_ip6 = "if2ip6="+l_ip6[0]+"::"+str(f_node_number)
        l_arg_ip6mask = "if2ip6mask=" + l_ip6_split[1]

        self.logger.debug("Arguments [%s %s %s %s %s %s]" % (l_arg_n1number, l_arg_n2number, l_arg_ip4, l_arg_ip4mask, l_arg_ip6, l_arg_ip6mask))

        core_daemon = subprocess.Popen(['coresendmsg', 'link', 'flags=add', l_arg_n1number,
                                        l_arg_n2number, l_arg_ip4, l_arg_ip4mask, l_arg_ip6,
                                        l_arg_ip6mask], stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)

        self.logger.debug(core_daemon.communicate())


# < the end >--------------------------------------------------------------------------------------