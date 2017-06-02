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
