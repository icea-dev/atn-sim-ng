#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
track_generator_mngr

Track generator Manager

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

revision 0.1  2017/may  matias
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/05"

# < import >---------------------------------------------------------------------------------------

# python library
from PyQt4 import QtCore

import ConfigParser
import logging
import os
import socket

module_logger = logging.getLogger('main_app.track_generator_mngr')

# < class CTrackGeneratorMngr >--------------------------------------------------------------------


class CTrackGeneratorMngr(QtCore.QObject):
    """

    """

    D_NET_CNFG = None
    D_NET_PORT = None

    D_MSG_VRS = None
    D_MSG_FRZ = None
    D_MSG_UFZ = None


    # ---------------------------------------------------------------------------------------------
    def __init__(self, f_parent=None, f_mediator=None):
        """
        Constructor

        :param f_parent:
        :param f_mediator:
        """
        super(CTrackGeneratorMngr, self).__init__(f_parent)

        self.logger = logging.getLogger('main_app.track_generator_mngr.CTrackGeneratorMngr')
        self.logger.info("Creating instance of CTrackGeneratorMngr")

        # the mediator
        self.mediator = f_mediator

        # Track Generator processes
        self.ptracks = None
        self.adapter = None
        self.visil = None
        self.pilot = None
        self.db_edit = None

        # Channel Track generator
        self.channel = 4

        # Track generator directories
        self.dir = None
        self.data_dir = None

        # Read configuration files
        self.load_config_file()

        # Read configuration files of the Track Generator
        self.load_track_generator_config_file(os.path.join(self.dir, "tracks.cfg"))

        self.net_tracks_cnfg = self.D_NET_CNFG + "." + str(self.channel)
        self.logger.debug("Multicast address of ptracks cnfg %s" % self.net_tracks_cnfg)

        # Create the socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Make the socket multicast-aware, and set TTL.
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)


    # ---------------------------------------------------------------------------------------------
    def load_config_file(self, config="atn-sim-gui.cfg"):
        """
        Reads a configuration file to load the root directory of the Track generator.

        :param config: configuration file name.
        :return:
        """

        if os.path.exists(config):
            conf = ConfigParser.ConfigParser()
            conf.read(config)
            self.dir = conf.get("Dir", "ptracks")
        else:
            self.dir = os.path.join(os.environ['HOME'], 'ptracks')

        self.data_dir = os.path.join(self.dir, 'data')

        self.logger.debug("Root directory of the Track Generator: [%s]" % self.dir)
        self.logger.debug("Data directory of the Track generator: [%s]" % self.data_dir)


    # ---------------------------------------------------------------------------------------------
    def load_track_generator_config_file(self,config_file):
        """
        Loads the information to send configuration mesages to the Track Generator (ptracks)

        :param config_file: configuration file name.
        :return: none
        """

        if os.path.exists(config_file):
            conf = ConfigParser.ConfigParser()
            conf.read(config_file)
            self.D_NET_CNFG = conf.get("net", "cnfg")
            self.D_NET_PORT = conf.get("net", "port")
        else:
            self.D_NET_CNFG = self.get_ptracks_data('D_NET_CNFG')
            self.D_NET_PORT = self.get_ptracks_data('D_NET_PORT')

        self.logger.debug("NET_CNFG [%s]" % self.D_NET_CNFG)
        self.logger.debug("NET_PORT [%s]" % self.D_NET_PORT)

        self.D_MSG_VRS = self.get_ptracks_data('D_MSG_VRS')
        self.D_MSG_FRZ = self.get_ptracks_data('D_MSG_FRZ')
        self.D_MSG_UFZ = self.get_ptracks_data('D_MSG_UFZ')

        self.D_MSG_VRS.strip('\n')

        self.logger.debug("MSG_VRS [%s]" % self.D_MSG_VRS)
        self.logger.debug("MSG_FRZ [%s]" % self.D_MSG_FRZ)
        self.logger.debug("MSG_UFZ [%s]" % self.D_MSG_UFZ)


    # ---------------------------------------------------------------------------------------------
    def send_pause_message(self):
        """

        :return:
        """

        self.logger.info("Sending pause message to the Track Generator")

        message = str(int(self.D_MSG_VRS)) + "#" + self.D_MSG_FRZ
        self.send_multicast_data(data=message, port=int(self.D_NET_PORT),
                                 addr=self.net_tracks_cnfg)


    # ---------------------------------------------------------------------------------------------
    def send_play_message(self):
        """

        :return:
        """

        self.logger.info("Sending play message to the Track Generator")

        message = str(int(self.D_MSG_VRS)) + "#" + self.D_MSG_UFZ
        self.send_multicast_data(data=message, port=int(self.D_NET_PORT),
                                 addr=self.net_tracks_cnfg)


    # ---------------------------------------------------------------------------------------------
    def send_multicast_data(self,data,port,addr):
        """

        :param data:
        :param port:
        :param addr:
        :return:
        """

        self.logger.debug("sending data: [%s] to [%s:%s]" % (data, addr, port))

        # Send the data
        self.sock.sendto(data, (addr, port))


# < the end >--------------------------------------------------------------------------------------
