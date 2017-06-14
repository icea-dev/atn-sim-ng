#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
Copyright 2016, ICEA

This file is part of atn-sim

atn-sim is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

atn-sim is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

revision 0.1  2017/may  mlabru
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.1$"
__author__ = "Milton Abrunhosa"
__date__ = "2017/05"

# < imports >--------------------------------------------------------------------------------------

# python library
import logging
import socket
import time

# atn-sim
import atn.surveillance.adsb.forwarders.adsb_fwrd as fads

# < module defs >----------------------------------------------------------------------------------

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)

# < class BusterForwarder >------------------------------------------------------------------------

class BusterForwarder(fads.AdsbForwarder):
    """
    buster server forwarder
    """
    # ---------------------------------------------------------------------------------------------
    def __init__(self, fi_id=0, fs_addr="localhost", fi_port=12270, f_options=None, fv_verbose=False):
        """
        constructor
        """
        # init super class
        super(BusterForwarder, self).__init__()

        # id
        self.__i_id = fi_id

        # socket
        self.__sock = None

        # timeout
        self.__timeout = 1.

        # options ?
        if f_options is not None:
            self.__t_ip_dst = (f_options["addr"], int(f_options["port"]))

        # senão,...
        else:
            self.__t_ip_dst = (fs_addr, fi_port)

        # create connection
        self.__connect()

        # enable/disable log messages 
        M_LOG.disabled = not fv_verbose

        # show
        print "creating an instance of BusterForwarder"

    # ---------------------------------------------------------------------------------------------
    def __str__(self):
        """
        return string representative
        """
        # return
        return "BusterForwarder --> {}:{}".format(self.__t_ip_dst[0], str(self.__t_ip_dst[1]))

    # ---------------------------------------------------------------------------------------------
    def __connect(self):
        """
        connect to destination client
        """
        # create socket
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        assert self.__sock 

        # set connection timeout 
        self.__sock.settimeout(self.__timeout)

    # ---------------------------------------------------------------------------------------------
    def forward(self, ls_message, lf_toa, tx_id=None, rx_id=None):
        """
        forward message
        """
        # socket exists ?
        if self.__sock:
            # build message
            ls_msg = "{}#{}#{}#{}#{}".format(self.__i_id, str(ls_message).upper(), lf_toa, time.clock(), tx_id)

            # send ok ?
            if self.__sock.sendto(ls_msg, self.__t_ip_dst) > 0:
                # logger
                M_LOG.info("BusterForwarder send: {}".format(ls_msg))

    # =============================================================================================
    # data
    # =============================================================================================
        
    # ---------------------------------------------------------------------------------------------
    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, f_val=0.5):
        self.__timeout = f_val

# < the end >--------------------------------------------------------------------------------------
