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

"""This class implements a message header
"""

import array
import struct
import binascii
import ctypes
import socket

__author__ = "Alexandre Magno"
__version__ = "0.1"
__date__ = "2016-dec-08"


class HeaderPR99:

    # -------------------------------------------------------------------------
    # method constructor
    # -------------------------------------------------------------------------
    def __init__(self):

        """
        Initialize attributs of class
        """

        self.CODE       = 0x0C
        self.ENDER      = 0x11

        self._ucOrig    = '00000000'        # 8  bytes - 64  bits

        self._siNMsg    = 0                 # 4  bytes - 32  bits
                                            # tam msg invertida
                                                   
        self._usComp    = 0                 # 2  bytes - 16  bits

                                            # 32 bytes - 256 bits # 32 consoles
        self._ucEndEth  = '11111100000000000000000000000000'

        self._ucLen     = 0                 # 1  byte  - 8   bits
        self._ucIndic   = 0                 # 1  byte  - 8   bits
        self._btSelCode = self.CODE         # 1  byte  - 8   bits # 0x0C
        self._btEnder   = self.ENDER        # 1  byte  - 8   bits # 0x11


    # -------------------------------------------------------------------------
    # method binstr
    # -------------------------------------------------------------------------
    def binstr(self):
        """
        set the size and type of attributes in binary mode
        """

        # initialize message
        header = ""

        # Orig (8 bytes + '\0' = 9 bytes (64-bit)
        header += bin(int(binascii.hexlify(self._ucOrig),16))[2:].zfill(64)

        # NMsg (32-bit)
        nmsg = bin(self._siNMsg)[2:].zfill(32)
        nmsg = self.invert_bytes(nmsg)
        header += nmsg

        # Comp (16-bit)
        comp = bin(self._usComp)[2:].zfill(16)
        comp = self.invert_bytes(comp)
        header += comp

        # EndEth (32 bytes  + '\0' = 33 (264-bit)
        for i in range(0,len(self._ucEndEth)):
            if self._ucEndEth[i] == '1':
                header += '00000001'
            else:
                header += '00000000'

        # Len (8-bit)
        header += bin(self._ucLen)[2:].zfill(8)

        # Indic (8-bit)
        header += bin(self._ucIndic)[2:].zfill(8)

        # SelCode (8-bit)
        header += bin(self._btSelCode)[2:].zfill(8)

        # Ender (8-bit)
        header += bin(self._btEnder)[2:].zfill(8)

        return header


    # -------------------------------------------------------------------------
    # method tohex
    # -------------------------------------------------------------------------
    def tohex(self):
        """
        convert the message to hexadecimal
        """
        msg = hex(int(self.binstr(), 2)).rstrip("L").lstrip("0x")
        msg = msg.replace('30', '00')

        return msg


    # -------------------------------------------------------------------------
    # method invert_bytes
    # -------------------------------------------------------------------------
    def invert_bytes(self, msg):
        """
        this method performs the inversion of bytes (LOHI)
        """

        invmsg = list(msg)
        n = len(msg)

        for x in range(0, n, 8):
            invmsg[x] = msg[n-x-8]
            invmsg[x+1] = msg[n-x-7]
            invmsg[x+2] = msg[n-x-6]
            invmsg[x+3] = msg[n-x-5]
            invmsg[x+4] = msg[n-x-4]
            invmsg[x+5] = msg[n-x-3]
            invmsg[x+6] = msg[n-x-2]
            invmsg[x+7] = msg[n-x-1]
        return "".join(invmsg)

#
# end class HeaderPR99
#


if __name__ == "__main__":

    # instance object
    # -----------------------------------------------------------------------
    l_stHeaderPR99 = HeaderPR99()

    # output
    print "BIN: %s" % l_stHeaderPR99.binstr()
    print "HEX: %s" % l_stHeaderPR99.tohex()
    #print binascii.unhexlify(l_stHeaderPR99.tohex())

