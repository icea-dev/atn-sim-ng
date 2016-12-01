"""--------------------------------------------------------------------------
Project ADS-B Security
Copyright (c) 2016, ICEA - Institute of Airspace Control
-----------------------------------------------------------------------------
Package....: radar/icea
Module.....: tagPR95.py
Description: This class implements a message of empty sector
-----------------------------------------------------------------------------
Details change
-----------------------------------------------------------------------------
Alexandre MG Silva  2016/06/23
                    program created
                    documentation of class in docstrings
--------------------------------------------------------------------------"""

import array
import struct
import binascii
import ctypes
import socket
import time

from HeaderPR99 import HeaderPR99

F_D = 0xFD
MAX_SETOR = 32

TAMCABECALHO = 50

# -----------------------------------------------------------------------------
# class tagPR95
# -----------------------------------------------------------------------------
class tagPR95:

    # -------------------------------------------------------------------------
    # method constructor
    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Initialize attributs of class
        """

        # codigo & monograma radar
        # -------------------------------------------------------------------
        self._btCode      = None                # 8 bits,
        self._btMonograma = None                # 8 bits
                      
        # numero do setor & divisor
        # -------------------------------------------------------------------
        self._btSetor     = None                # 8 bits
        self._btDivisor   = None                # 8 bits

        # instance object
        # -------------------------------------------------------------------
        self.l_stHeaderPR99 = HeaderPR99()


    # -------------------------------------------------------------------------
    # method binstr
    # -------------------------------------------------------------------------
    def binstr(self):
        """
        formatting attributes to binary
        """

        # initialize message
        msg = ""

        # btCode (8-bit)
        msg += bin(self._btCode)[2:].zfill(8)

        # btMonograma (8-bit)
        msg += bin(int(binascii.hexlify(self._btMonograma),16))[2:].zfill(8)

        # _btSetor (8-bit)
        msg += bin(self._btSetor)[2:].zfill(8)

        # _btDivisor (8-bit)
        msg += bin(self._btDivisor)[2:].zfill(8)
        return msg


    # -------------------------------------------------------------------------
    # method tohex
    # -------------------------------------------------------------------------
    def tohex(self):
        """
        convert the message to hexadecimal
        """
        return hex(int(self.binstr(), 2)).rstrip("L").lstrip("0x")


    # -------------------------------------------------------------------------
    # method __str__
    # -------------------------------------------------------------------------
    def __str__(self):
        """
        It displays the contents of the attributes
        """

        output = ""
        output += "_btSetor  : %s\n" % self._btSetor
        output += "_btDivisor: %s\n" % self._btDivisor
        return output

#
# end class tagPR95
#


if __name__ == "__main__":
	
    """
    main - Begin the processment of classe
    """

	# instance object tagPR95 (setor)
    l_stPR95 = tagPR95()
  
    # -----------------------------------------------------------------------
    # initialize attributs of class PR95
    # -----------------------------------------------------------------------
    l_stPR95._btCode        = F_D
    l_stPR95._btMonograma   = 'G'
    l_stPR95._btSetor       = 7
    l_stPR95._btDivisor     = MAX_SETOR


    # -----------------------------------------------------------------------
    # prepare message (header+msg)
    # -----------------------------------------------------------------------

    # get message PR95 in hexa
    msgPR95 = l_stPR95.tohex()

    l_iTamMsg = len(msgPR95)/2
    l_stPR95.l_stHeaderPR99._ucLen     = l_iTamMsg+2
    l_stPR95.l_stHeaderPR99._ucIndic   = 0
    l_stPR95.l_stHeaderPR99._usComp    = l_iTamMsg + TAMCABECALHO
    l_stPR95.l_stHeaderPR99._siNMsg    = l_iTamMsg

    # get message HeaderPR99 in hexa
    headerPR99 = l_stPR95.l_stHeaderPR99.tohex()

    # mount message complete
    message = headerPR99 + msgPR95

    # output
    print
    print l_stPR95
    print
    print 'headerPR99   =', headerPR99
    print 'Tam header   =', len(headerPR99)/2
    print
    print 'msgPR95      =', msgPR95
    print 'len(msgPR95) =', len(msgPR95)/2
    print
    print 'msg complete =', message
    print 'len(message) =', len(message)/2
    print
    print 'l_stPR95.l_stHeaderPR99._ucLen   =', l_stPR95.l_stHeaderPR99._ucLen
    print 'l_stPR95.l_stHeaderPR99._ucIndic =', l_stPR95.l_stHeaderPR99._ucIndic
    print 'l_stPR95.l_stHeaderPR99._usComp  =', l_stPR95.l_stHeaderPR99._usComp
    print 'l_stPR95.l_stHeaderPR99._siNMsg  =', l_stPR95.l_stHeaderPR99._siNMsg
