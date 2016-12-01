"""--------------------------------------------------------------------------
Project ADS-B Security
Copyright (c) 2016, ICEA - Institute of Airspace Control
-----------------------------------------------------------------------------
Package....: radar/icea
Module.....: tagPR99.py
Description: This class implements a message of secondary track
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
import math

from HeaderPR99 import HeaderPR99

TAMCABECALHO = 50

PR800_NUMBER = 0x02
M_NM = 0.00054
DEG_RAD = 0.017453292   # Converte DEG para RAD

# -----------------------------------------------------------------------------
# class tagPR99
# -----------------------------------------------------------------------------
class tagPR99:

    xxASS = 0
    xxCAN = 1
    xxINI = 2
    xxPRI = 3
    xxSSR = 4

    xxNUL = 0
    xxCOM = 1
    xxEMG = 2
    xxHIJ = 3

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
        self._btMonograma = None                # 8 bits;
                      
        # numero do processador radar, byte de servico
        # -------------------------------------------------------------------
        self._btTCord     = None               # 8, tipo de coordenadas
        self._bSPI        = None               # 1, SPI - special pulse information
        self._btPrcRadar  = None               # 1, numero do processador radar
        self._bReal       = None               # 1,
        self._bSimulada   = None               # 1,
        self._bSintese    = None               # 1,
        self._bTeste      = None               # 1;
                                                                                              
        # PR800 track quality & detection misses
        # -------------------------------------------------------------------
        self._btQual      = None               # 8,
        self._btDetc      = None               # 8;
                                                                                                                    
        # numero da pista
        # -------------------------------------------------------------------
        self._wTrkNo      = None               # 16;
                                                                    
        # tipo de pista (primaria, secundaria, associada, cancelada)
        # -------------------------------------------------------------------
        self._enTrack     = None               # 32; 
                                                                                                                                         
        # codigo de auxilio (emergencia, spi, falha comunicacao, sequestro)
        # -------------------------------------------------------------------
        self._enAux       = None               # 32;
                                                                                                                                                        
        # coordenadas da pista (em milhas nauticas - NM)
        # -------------------------------------------------------------------
        self._dX          = None               # 64;
        self._dY          = None               # 64;
        self._dZ          = None               # 64;
                                                                                                                                                     
        # delta
        # -------------------------------------------------------------------
        self._siDX        = None               # 16;
        self._siDY        = None               # 16;
                                                                                                                                                                                    
        # nivel de voo (altitude em pes / 100)
        # -------------------------------------------------------------------
        self._siNivel     = None               # 16;
                                                                                                                                                                                                
        # velocidade (em knots)
        # -------------------------------------------------------------------
        self._siVel       = None               # 16;
                                                                                                                                                                                                           
        # direcao (em graus)
        # -------------------------------------------------------------------
        self._dProa       = None               # 64;
                                                                                                                                                                                                                       
        # modo & codigo transponder
        # -------------------------------------------------------------------
        self._cTMode      = None               # 8;
        self._szSSR       = None               # 40;
                                                                                                                                                                                                                                        
        # identificacao da pista (call sign)
        # -------------------------------------------------------------------
        self.szCSign      = None               # 64;


        # instance object
        # -------------------------------------------------------------------
        self.l_stHeaderPR99 = HeaderPR99()


    # -------------------------------------------------------------------------
    # method binstr
    # -------------------------------------------------------------------------
    def binstr(self):
        """
        set the size and type of attributes in binary mode
        """

        # initialize message
        msg = ""

        # btCode (8-bit)
        msg += bin(self._btCode)[2:].zfill(8)

        # btMonograma (8-bit)
        msg += bin(int(binascii.hexlify(self._btMonograma),16))[2:].zfill(8)

        # number of processor radar, byte of service (btTCord 8-bit)
        msg += bin(int(binascii.hexlify(self._btTCord),16))[2:].zfill(8)

        # byte of service (8-bit)
        msg += bin(self._bSPI)[2:].zfill(1)
        msg += bin(self._btPrcRadar)[2:].zfill(1)
        msg += bin(self._bReal)[2:].zfill(1)
        msg += bin(self._bSimulada)[2:].zfill(1)
        msg += bin(self._bSintese)[2:].zfill(1)
        msg += bin(self._bTeste)[2:].zfill(1)
        msg += bin(0)[2:].zfill(1)
        msg += bin(0)[2:].zfill(1)

        # btQual (8-bit)
        msg += bin(self._btQual)[2:].zfill(8)
        
        # btDetc (8-bit)
        msg += bin(self._btDetc)[2:].zfill(8)
	
        # wTrkNo (16-bit)
        _wTrkNo = bin(self._wTrkNo)[2:].zfill(16)
        _wTrkNo = self.invert_bytes(_wTrkNo)
        msg += _wTrkNo

        # enTrack (32-bit)
        #msg += bin(self._enTrack)[2:].zfill(32)
        _enTrack = bin(self._enTrack)[2:].zfill(32)
        _enTrack = self.invert_bytes(_enTrack)
        msg += _enTrack

        # enAux (32-bit)
        msg += bin(self._enAux)[2:].zfill(32)

        # ptoTrk X,Y,Z (64-bit)
        xpos = ''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in struct.pack('!d', self._dX))
        ypos = ''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in struct.pack('!d', self._dY))
        zpos = ''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in struct.pack('!d', self._dZ))

        # Invert bytes
        xpos = self.invert_bytes(xpos)
        ypos = self.invert_bytes(ypos)

        msg += xpos
        msg += ypos
        msg += zpos

        # siDX (16-bit)
        msg += bin(self._siDX)[2:].zfill(16)

        # siDY (16-bit)
        msg += bin(self._siDY)[2:].zfill(16)
        
        # siNivel (16-bit)
        si_nivel = bin(self._siNivel)[2:].zfill(16)
        si_nivel = self.invert_bytes(si_nivel)
        msg += si_nivel

        # siVel (16-bit)
        si_vel = bin(self._siVel)[2:].zfill(16)
        si_vel = self.invert_bytes(si_vel)
        msg += si_vel

        # dProa (64-bit)
        d_proa = ''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in struct.pack('!d', self._dProa))
        d_proa = self.invert_bytes(d_proa)
        msg += d_proa

        # cTMode (8-bit)
        msg += bin(int(binascii.hexlify(self._cTMode),16))[2:].zfill(8)

        # szSSR (5 bytes = 40-bit)
        msg += bin(int(binascii.hexlify(self._szSSR+'\0'),16))[2:].zfill(40)

        # szCSign (8 bytes = 64-bit)
        msg += bin(int(binascii.hexlify(self._szCSign+'\0'),16))[2:].zfill(64)

        # offset 2 bytes to ajust position of memory
        msg += bin(0)[2:].zfill(8)
        msg += bin(0)[2:].zfill(8)

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
        it displays the contents of the attributes
        """
        output = ""
        output += "_wTrkNo: %s\n" % self._wTrkNo
        return output


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
# end class tagPR99
#


# -----------------------------------------------------------------------------
# method send_msg
# -----------------------------------------------------------------------------
def send_msg(hex_msg):
    """
    This method performs the post on the network in broadcast mode and udp
    """

    # connection udp, send message
    HOST = '172.18.104.255'              # Endereco IP do Servidor ICEA
    PORT = 65000                         # Porta do Servidor ICEA

    udp  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 
    dest = (HOST, PORT)

    udp.sendto (binascii.unhexlify(hex_msg), dest)
    udp.close()


# -----------------------------------------------------------------------------
# method __main__
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    """
    main - Begin the processment of classe
    """

	# instance object tagPR99
    l_stPR99 = tagPR99()
  
    # -------------------------------------------------------------------------
    # initialize attributs of class PR99
    # -------------------------------------------------------------------------

    l_stPR99._btCode        = 0xFF
    l_stPR99._btMonograma   = 'G'
    l_stPR99._btTCord       = 'C'


    # Codigos de servico do protocolo ICEA
    # real(0x01), simulada(0x02), sintese(0x04), teste(0x08)
    # Setou-se REAL por causa da X4000
    l_stPR99._bSPI          = 0
    l_stPR99._btPrcRadar    = 0
    l_stPR99._bReal         = 0
    l_stPR99._bSimulada     = 0
    l_stPR99._bSintese      = 0
    l_stPR99._bTeste        = 1
  
    l_stPR99._btQual        = 0x6E
    l_stPR99._btDetc        = 0
    l_stPR99._wTrkNo        = 7

    l_stPR99._enTrack       = 0                          #tagPR99.xxSSR
    l_stPR99._enAux         = tagPR99.xxNUL

    l_stPR99._dX            = -28.625687
    l_stPR99._dY            = 11.468303
    l_stPR99._dZ            = 2000

    '''
    dx = float( (210.0*10.0) * math.sin((45.0 * DEG_RAD)) )
    dy = float( (210.0*10.0) * math.cos((45.0 * DEG_RAD)) )
    l_stPR99._siDX           = int(dx * M_NM * 32.0)
    l_stPR99._siDY           = int(dy * M_NM * 32.0)

    print
    print 'dx             =', dx
    print 'dy             =', dy
    print 'l_stPR99._siDX =', l_stPR99._siDX
    print 'l_stPR99._siDY =', l_stPR99._siDY
    print
    '''

    l_stPR99._siDX          = 0
    l_stPR99._siDY          = 0

    l_stPR99._siNivel       = 200
    l_stPR99._siVel         = 210
    l_stPR99._dProa         = 45.0
    l_stPR99._cTMode        = 'A'
    l_stPR99._szSSR         = '4231'
    l_stPR99._szCSign       = 'TAM7777'


    # -------------------------------------------------------------------------
    # prepare message (header+msg)
    # -------------------------------------------------------------------------

    # get message PR99 in hexa
    msgPR99 = l_stPR99.tohex()

    l_iTamMsg = len(msgPR99)/2
    l_stPR99.l_stHeaderPR99._ucLen     = l_iTamMsg+2
    l_stPR99.l_stHeaderPR99._ucIndic   = 0
    l_stPR99.l_stHeaderPR99._usComp    = l_iTamMsg + TAMCABECALHO
    l_stPR99.l_stHeaderPR99._siNMsg    = l_iTamMsg

    # get message HeaderPR99 in hexa
    headerPR99 = l_stPR99.l_stHeaderPR99.tohex()

    # mount message complete
    message = headerPR99 + msgPR99

    # output
    #print l_stPR99
    print
    print 'headerPR99   =', headerPR99
    print 'Tam header   =', len(headerPR99)/2
    print
    print 'msgPR99      =', msgPR99
    print 'len(msgPR99) =', len(msgPR99)/2
    print
    print 'msg complete =', message
    print 'len(message) =', len(message)/2
    print
    print 'l_stPR99.l_stHeaderPR99._ucLen   =', l_stPR99.l_stHeaderPR99._ucLen
    print 'l_stPR99.l_stHeaderPR99._ucIndic =', l_stPR99.l_stHeaderPR99._ucIndic
    print 'l_stPR99.l_stHeaderPR99._usComp  =', l_stPR99.l_stHeaderPR99._usComp
    print 'l_stPR99.l_stHeaderPR99._siNMsg  =', l_stPR99.l_stHeaderPR99._siNMsg
    print

    while True:
       # send message
       send_msg(message)
       time.sleep(0.5)
