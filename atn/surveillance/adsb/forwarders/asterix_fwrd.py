#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016, ICEA
#
# This file is part of atn-sim
#
# atn-sim is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# atn-sim is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import logging
import socket
import time

from .adsb_fwrd import AdsbForwarder

__author__ = "Ivan Matias"
__version__ = "0.1"
__date__ = "2016-dec-08"


class AsterixForwarder(AdsbForwarder):
    """This class is responsible for forwarding ADS-B messages to the ASTERIX Server.
    """

    def __init__(self, verbose=False, items=None, server="127.0.0.1", port="60000"):
        """The contructor.

        Args:
            verbose (bool): Explain what is being done.
            items (dict): A dictionary of the configuration data (server and port).
            server (string): The destination of the ADS-B messages.
            port (string): The ADS-B messages receiving port.

        """
        # logger [Logger Object]:
        self.logger = logging.getLogger('adsb_in_app.AsterixForwarder')

        # s [socket]: The end point to send data.
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # verbose [bool]: Explain what is being done.
        self.verbose = verbose

        if self.verbose:
            self.logger.disabled = False
        else:
            self.logger.disabled = True

        self.logger.info('Creating an instance of Asterix forwarder')

        if items is not None:
            # ip_destination [string]: The destination of the ADS-B messages.
            self.ip_destination = items["server"]
            # port_d [int]: The ADS-B messages receiving port.
            self.port_d = int(items["port"])
        else:
            self.ip_destination = server
            self.port_d = port

    def send_msg(self, message, verbose=False):
        """Sends the ADS-B messages to the server.

        Args:
            message (string): the ADS-B message.
            verbose (bool): Explain what is being done.

        Returns:
            bool: True if the function was executed successfully; otherwise False.

        """
        if self.s:
            sent = self.s.sendto(str(message).upper(),(self.ip_destination, self.port_d))

            if sent == 0:
                return False

            if verbose:
                self.logger.info("ASTERIX SERVER : " + str(message).upper() + "\n")

            return True
        else:
            return False

    def forward(self, message, time_of_arrival=None, tx_id=None, rx_id=None):
        """Forwarding the ADS-B message

        The time of applicability (time_of_arrival) indicates the exact time at which the
        position transmitted in the target report is valid.

        Args:
            message (string): The ADS-B message
            time_of_arrival (int): Is the time a transmission from a target is received at a Receiving Unit,

        """
        time_utc = time.gmtime(time.time()+1)
        time_of_day = int(time_utc.tm_hour) * 3600 + int(time_utc.tm_min) * 60 + int(time_utc.tm_sec)

        data = message + hex(time_of_day).rstrip("L").lstrip("0x")

        self.send_msg(data)

    def __str__(self):
        """Returns the object information as a string.

        Returns:
            string:

        """
        return "ASTERIX SERVER IP...: " + self.ip_destination + ":" + str(self.port_d)