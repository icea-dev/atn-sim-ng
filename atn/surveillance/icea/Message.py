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

import binascii
import ctypes
import os

class Message(object):

    def __init__(self):
    
        # endereco icao
        self._icao24     = None
                                                                                                                                                                                                                                        
        # callsign
        self._szCSign    = None

        # message
        self._szMessage  = None

    def __str__(self):
        output = ""
        output += "_icao24...: %s\n" % self._icao24
        output += "_szCSign..: %s\n" % self._szCSign
        output += "_szMessage: %s\n" % self._szMessage
        return output
#
# end class Message
#

if __name__ == "__main__":
	
	# instance object Message
    l_Message = Message()
  
    # initialize attributs of object
    l_Message._icao24    = binascii.b2a_hex(os.urandom(3))
    l_Message._szCSign   = 'TAM7777'
    l_Message._szMessage = None

    # output
    print ""
    print l_Message
    print ""
