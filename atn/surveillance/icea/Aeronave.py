import array
import struct
import binascii
import ctypes
import socket
import time
import os

from  Message import Message

class Aeronave(object):

    def __init__(self):
    
        # endereco icao
        # -------------------------------------------------------------------
        self._icao24      = None

        # numero da pista
        # -------------------------------------------------------------------
        self._wTrkNo      = None               # 16 bits;
                                                                    
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
        self._szCSign      = None              # 64;

   	    # instance object Message
        self._Message      = Message()


    def binstr(self):
        # initialize message
        msg = ""

        # wTrkNo (16-bit)
        msg += bin(self._wTrkNo)[2:].zfill(16)

        # enTrack (32-bit)
        msg += bin(self._enTrack)[2:].zfill(32)

        # enAux (32-bit)
        msg += bin(self._enAux)[2:].zfill(32)

        # ptoTrk X,Y,Z (64-bit)
        msg += ''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in struct.pack('!d', self._dX))
        msg += ''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in struct.pack('!d', self._dY))
        msg += ''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in struct.pack('!d', self._dZ))
        
        # siNivel (16-bit)
        msg += bin(self._siNivel)[2:].zfill(16)

        # siVel (16-bit)
        msg += bin(self._siVel)[2:].zfill(16)

        # dProa (64-bit)
        msg += ''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in struct.pack('!d', self._dProa))

        # cTMode (8-bit)
        msg += bin(int(binascii.hexlify(self._cTMode),16))[2:].zfill(8)

        # szSSR (5 bytes = 40-bit)
        msg += bin(int(binascii.hexlify(self._szSSR+'\0'),16))[2:].zfill(40)

        # szCSign (8 bytes = 64-bit)
        msg += bin(int(binascii.hexlify(self._szCSign+'\0'),16))[2:].zfill(64)        
        return msg


    def tohex(self):
        return hex(int(self.binstr(), 2)).rstrip("L").lstrip("0x")


    def __str__(self):
        output = ""
        output += "_icao24.: %s\n" % self._icao24
        output += "_wTrkNo.: %s\n" % self._wTrkNo
        output += "_enTrack: %s\n" % self._enTrack
        output += "_enAux..: %s\n" % self._enAux
        output += "_dX.....: %s\n" % self._dX
        output += "_dY.....: %s\n" % self._dY
        output += "_dZ.....: %s\n" % self._dZ
        output += "_siNivel: %s\n" % self._siNivel
        output += "_siVel..: %s\n" % self._siVel
        output += "_dProa..: %s\n" % self._dProa
        output += "_cTMode.: %s\n" % self._cTMode
        output += "_szSSR..: %s\n" % self._szSSR
        output += "_szCSign: %s\n" % self._szCSign
        return output

#
# end class Aeronave
#

if __name__ == "__main__":
	
	# instance object Aeronave
    l_Aeronave = Aeronave()
  
    # initialize attributs of object
    l_Aeronave._icao24        = binascii.b2a_hex(os.urandom(3))
    l_Aeronave._wTrkNo        = 7
    l_Aeronave._enTrack       = 0
    l_Aeronave._enAux         = 0
    l_Aeronave._dX            = -28.625687
    l_Aeronave._dY            = 11.468303
    l_Aeronave._dZ            = 0.0
    l_Aeronave._siNivel       = 330
    l_Aeronave._siVel         = 310
    l_Aeronave._dProa         = 90.0
    l_Aeronave._cTMode        = 'A'
    l_Aeronave._szSSR         = '7575'
    l_Aeronave._szCSign       = 'TAM7777'

    # output
    print ""
    print l_Aeronave
    print ""

