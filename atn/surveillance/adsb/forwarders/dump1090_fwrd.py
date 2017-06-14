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

from .adsb_fwrd import AdsbForwarder

__author__ = "Marcio Monteiro"
__version__ = "0.1"
__date__ = "2016-dec-08"


class Dump1090Forwarder(AdsbForwarder):

    __TYPE__ = "DUMP1090"

    def __init__(self, verbose=False, items=None, server="localhost", port="30001"):
        self.logger = logging.getLogger('adsb_in_app.Dump1090')
        self.s = None
        self.timeout = 1.0
        self.verbose = verbose

        if self.verbose:
            self.logger.disabled = False

        else:
            self.logger.disabled = True

        self.logger.info('Creating an instance of Dump1090')

        if items is not None:
            self.ip_destination = items["server"]
            self.tcp_port_d = int(items["port"])

        else:
            self.ip_destination = server
            self.tcp_port_d = port

    def set_timeout(self, timeout=0.5):
        self.timeout = timeout

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.s.settimeout(self.timeout)
            self.s.connect((self.ip_destination, self.tcp_port_d))
            return True

        except socket.error:
            self.s = None
            return False

    def send_msg(self, message, verbose=False):
        if self.s:
            sent = self.s.send("*" + str(message).upper() + ";\n")

            if sent == 0:
                return False

            if verbose:
                self.logger.info("DUMP1090 : " + "*" + str(message).upper() + ";\n")

            return True

        return False

    def disconnect(self):
        if self.s:
            self.s.close()

    def forward(self, message, time_of_arrival=None, tx_id=None, rx_id=None):
        self.connect()
        self.send_msg(message=message)
        self.disconnect()

    def __str__(self):
        return "DUMP1090 IP...: " + self.ip_destination + ":" + str(self.tcp_port_d)
