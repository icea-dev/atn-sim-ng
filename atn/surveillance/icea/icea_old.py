# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#
#  Projeto ADS-B Security
#  Copyright (c) 2016, ICEA - Institute of Airspace Control
#  ----------------------------------------------------------------------
#  Package....: adsb
#  Module.....: icea_old.py
#
#  Description: Read messages in the protocol ADS-B through dump1090  or
#               of SRBC and converts to icea protocol
#  ----------------------------------------------------------------------
#  Details change
#  ----------------------------------------------------------------------
#  Alexandre MG Silva  2016/04/04
#                      program created
#                      
#  Alexandre MG Silva  2016/05/23
#                      update of methods
#                      
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

import socket
import getopt
import sys
import logging
import decoder
import math
import time
import struct
import binascii
import ctypes
import array

import threading
import operator

import random

from  tagPR95  import tagPR95
from  tagPR99  import tagPR99
from  Aeronave import Aeronave

# Parametros do WGS84 - Defense Mapping Agency Technical Report
a  = 6378137.0          # semi-eixo maior em metros
b  = 6356752.3142       # semi-eixo menor em metros
e2 = 0.00669437999013   # primeira excentricidade ao quadrado

RAD_DEG = 57.29577951   # Converte RAD para DEG
DEG_RAD = 0.017453292   # Converte DEG para RAD
MPS_NOS	= 1.94384       # 3600 : 1852
M_FT    = 3.281       
M_NM    = 0.00054      
NM_M    = 1852


DEG_PI_3   = 60.0           # PI / 3
DEG_PI_2   = 90.0           # PI / 2
DEG_PI     = 180.0          # PI
DEG_3PI_2  = 270.0          # 3 PI / 2
DEG_2PI    = 360.0          # 2 PI
RAD_DEG    = 57.29577951    # Converte RAD para DEG
DEG_RAD    = 0.017453292    # Converte DEG para RAD


# Radar
MAX_SETOR     = 32
DEG_SETOR	  = 11.25
MAX_NUM_MSG	  = 20
MAX_ANV_MSG	  = 20
MAX_ANV_SETOR = (MAX_NUM_MSG * MAX_ANV_MSG)

# Types of destionations (corremu or dump1090)
DST_CORE     = "core"
DST_DUMP1090 = "dump1090"

# -----------------------------------------------------------------------------
# class ICEA
# -----------------------------------------------------------------------------
class ICEA:

    # -------------------------------------------------------------------------
    # method constructor (__init__)
    # -------------------------------------------------------------------------
    def __init__(self, destination, portRead, portWrite, destination_type):

        # initialize attributes of class
        self.logger           = logging.getLogger('ICEA')

        self.destination_type = destination_type      # dump1090  or
                                                      # VisIR
        
        self.net_client       = destination           # "172.18.104.186"
                                                      # "172.18.104.255"

        self.port_read        = portRead              # 30002 dump1090
                                                      # 60000 srbc

        self.port_write       = portWrite             # 30001 dump1090
                                                      # 65000 VisIR

        self.sock             = None
        self.conn             = None
        self.addr             = None

        self.logger.info('creating an instance of ICEA')
        self.logger.disabled  = True

        self.BUFFER_SIZE      = 1024

        self.FT_TO_M          = 0.3048
        self.KT_TO_MPS        = 0.514444
        self.FTPM_TO_MPS      = 0.00508

        self.SYN              = 0x32
        self.SOH              = 0x01
        self.CODE             = 0x0C
        self.CODEEX           = 0x0D
        self.ADR              = 0x40
        self.DLE              = 0x10
        self.STX              = 0x02 
        self.ETX              = 0x03 
        self.PAD              = 0xFF
        self.P_P              = 0xFE
        self.P_S              = 0xFF
        self.C_P              = 0xFA
        self.F_D              = 0xFD
        self.COUNT            = 0x0E
        self.CONT             = 0x14
        self.ZERO             = 0x00
        self.PR800_NUMBER     = 0x02
        self.QUAL             = 0x6E
        self.ENDER            = 0x11 

        self.df               = ''
        self.ca               = ''
        self.callsign         = ''
        self.tc               = ''
        self.st               = ''
        self.nic              = ''
        self.time             = ''
        self.cpr              = ''
        self.cprlat           = ''
        self.cprlon           = ''
        self.speed            = 0
        self.heading          = 0
        self.ssr              = ''
        self.spi              = ''
        self.alt              = ''
        self.lat              = 0.0
        self.lon              = 0.0
        self.icao24           = None
        self.azimuth          = 0
        self.climb_rate       = 0

        self.l_iEvenOddAnt    = -1

        self.lastEvenMsg      = "" #None
        self.lastOddMsg       = "" #None
        self.mostRecentType   = None

        self.latrad           = -22.9824471121
        self.lonrad           = -46.3730366141
        self.altrad           = 2.0

        self.xxASS            = 0     # associada
        self.xxCAN            = 1     # cancelada
        self.xxINI            = 2     # iniciada
        self.xxPRI            = 3     # primaria
        self.xxSSR            = 4     # secundaria
        
        # instance object tagPR95
        self.stPR95 = tagPR95()

        # instance object tagPR99
        self.stPR99 = tagPR99()

        # list of instance of objects Aeronave
        self.aeronaveList = []

        # connection of read message of network (TCP or UDP)
        # read srbc - UDP
        if destination_type == DST_CORE:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            l_bind = (self.net_client, self.port_read)
            self.sock.bind(l_bind)
        # read dump1090 - TCP
        elif destination_type == DST_DUMP1090:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.connect((self.net_client, self.port_read))
            #l_bind = (self.net_client, self.port_read)
            #self.sock.bind(l_bind)                         # bind it to server port number 
            #self.sock.listen(1)                            # listen, allow 5 pending connects


    # -------------------------------------------------------------------------
    # method clearAttributes
    # clear attributes of class
    # -------------------------------------------------------------------------
    def clearAttributes(self):
        self.stPR99._dX      = 0.0
        self.stPR99._dY      = 0.0
        self.stPR99._dZ      = 0.0
        self.stPR99._siVel   = 0
        self.stPR99._siDX    = 0
        self.stPR99._siDY    = 0
        self.stPR99._siNivel = 0
        self.stPR99._dProa   = 0.0
        self.stPR99._wTrkNo  = 0
        self.stPR99._cTMode  = ''
        self.stPR99._szSSR   = ''

    # -------------------------------------------------------------------------
    # method usage
    # -------------------------------------------------------------------------
    def usage(self):
        print "Usage: python icea_old.py [options]"
        print ""
        print "Options:"
        print " -h, --help            Display this help and exit"
        print " -s, --server=IP       IP address of ip_server"
        print " -p, --port-rx=PORT    The port number used by the applicaton"
        print " --port-adsb_in=PORT   The same port as used by the Dump1090"
        print " -v                    Explain what is being done"

    # -------------------------------------------------------------------------
    # method process_command_line
    # -------------------------------------------------------------------------
    def process_command_line(self, logger):
        try:
            opts, args = getopt.getopt(
                sys.argv[1:], "hd:s:p:vx",
                ["help", "dump1090=", "server=", "port-rx=", "port-dump1090=",
                "port-dtoa="])
        except getopt.GetoptError as err:
            # print help information and exit:
            print str(err)
            self.usage()
            sys.exit(2)

        for opt, arg in opts:
            if opt == "-v":
                self.verbose = True
                logger.disabled = False
                self.logger.disabled = False
            elif opt == "-x":
                self.no_data_dump1090 = True
            elif opt == "--port-dump1090":
                self.port_dump1090 = int(arg)
            elif opt == "--port-dtoa":
                self.port_dtoa_server = int(arg)
            elif opt in ("-h", "--help"):
                self.usage()
                sys.exit()
            elif opt in ("-d", "--dump1090"):
                self.ip_dump1090 = arg
            elif opt in ("-s", "--server"):
                self.ip_dtoa_server = arg
            elif opt in ("-p", "--port-rx"):
                self.port_adsb_out = int(arg)


    # -------------------------------------------------------------------------
    # method sendmessage
    # -------------------------------------------------------------------------
    def sendmessage(self, message):

        # UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 

        # send msg
        #sock.sendto(message, (self.net_client, self.port_write))
        broadcast = "172.18.104.255"
        sock.sendto(message, (broadcast, self.port_write))
        sock.close()



    # =========================================================================
    #
    #            methods of conversion of Geographic for Cartesina
    #
    # =========================================================================


    # -------------------------------------------------------------------------
    # method geog2ecef
    # -------------------------------------------------------------------------
    def geog2ecef(self, lat, lon, alt):
        """
        Geografica para ECEF
	    entrada: lat e lon (graus), alt (m)
        saida: x, y, z   (m)
        """
        N = a / math.sqrt(1.0 - (e2 * math.sin(math.radians(lat)) * math.sin(math.radians(lat))))
        x = (N + alt) * math.cos(math.radians(lat)) * math.cos(math.radians(lon))
        y = (N + alt) * math.cos(math.radians(lat)) * math.sin(math.radians(lon))
        z = (N * (1.0 - e2) + alt) * math.sin(math.radians(lat))
        return x, y, z

    # -------------------------------------------------------------------------
    # method ecef2enu
    # -------------------------------------------------------------------------
    def ecef2enu(self, X, Y, Z, latrad, lonrad, altrad):
        """
        ECEF para ENU
        entrada: X, Y, Z (m) - coordenadas ECEF do alvo
                 latrad e lonrad (graus), altrad (m) - coordenadas do radar
        saida:   x, y, z (m) - coordenadas ENU do alvo em relacao ao radar
        """
        xrad, yrad, zrad = self.geog2ecef(latrad, lonrad, altrad)

        xdif = X - xrad
        ydif = Y - yrad
        zdif = Z - zrad

        x = - math.sin(math.radians(lonrad))*xdif + math.cos(math.radians(lonrad))*ydif
        y = - math.sin(math.radians(latrad))*math.cos(math.radians(lonrad))*xdif - math.sin(math.radians(latrad))*math.sin(math.radians(lonrad))*ydif + math.cos(math.radians(latrad))*zdif
        z =   math.cos(math.radians(latrad))*math.cos(math.radians(lonrad))*xdif + math.cos(math.radians(latrad))*math.sin(math.radians(lonrad))*ydif + math.sin(math.radians(latrad))*zdif
        return x, y, z

    # -------------------------------------------------------------------------
    # method geog2enu
    # -------------------------------------------------------------------------
    def geog2enu(self, latalvo, lonalvo, altalvo, latrad, lonrad, altrad):
        """
        Geografica para ENU
	    entrada: latalvo e lonalvo (graus), altalvo (m)  - coord geograficas do alvo
	             latrad e lonrad (graus), altrad (m)     - coord geograficas do radar
        saida: x, y, z   (m)  -  coordenadas cartesianas do alvo em relacao ao radar
        """
        X, Y, Z = self.geog2ecef(latalvo, lonalvo, altalvo)
        x, y, z = self.ecef2enu(X, Y, Z, latrad, lonrad, altrad)
        return x, y, z

    

    # =========================================================================
    #
    #                methods decode of fields message ads-b
    #
    # =========================================================================

    # -------------------------------------------------------------------------
    # method decode_DF
    # -------------------------------------------------------------------------
    def decode_DF(self, msg):
        self.df = decoder.get_df(msg)

    # -------------------------------------------------------------------------
    # method decode_CA
    # -------------------------------------------------------------------------
    def decode_CA(self, msg):
        self.ca = decoder.get_ca(msg)

    # -------------------------------------------------------------------------
    # method decode_icao24
    # -------------------------------------------------------------------------
    def decode_icao24(self, msg):
        self.icao24 = decoder.get_icao_addr(msg)

    # -------------------------------------------------------------------------
    # method decode_callsign
    # -------------------------------------------------------------------------
    def decode_callsign(self, msg):
        self.callsign = decoder.get_callsign(msg)

    # -------------------------------------------------------------------------
    # method decode_tc
    # -------------------------------------------------------------------------
    def decode_tc(self, msg):
        self.tc = decoder.get_tc(msg)

    # -------------------------------------------------------------------------
    # method decode_st
    # -------------------------------------------------------------------------
    def decode_st(self, msg):
        self.st = decoder.get_st(msg)

    # -------------------------------------------------------------------------
    # method decode_nic
    # -------------------------------------------------------------------------
    def decode_nic(self, msg):
        self.nic = decoder.get_nic(msg)

    # -------------------------------------------------------------------------
    # method decode_altitude
    # -------------------------------------------------------------------------
    def decode_altitude(self, msg):
        self.alt = decoder.get_alt(msg)

    # -------------------------------------------------------------------------
    # method decode_time
    # -------------------------------------------------------------------------
    def decode_time(self, msg):
        self.time = decoder.get_time(msg)

    # -------------------------------------------------------------------------
    # method decode_cpr
    # -------------------------------------------------------------------------
    def decode_cpr(self, msg):
        self.cpr = decoder.get_oe_flag(msg)

    # -------------------------------------------------------------------------
    # method decode_position
    # -------------------------------------------------------------------------
    def decode_position(self, msg):
        self.cprlat = decoder.get_cprlat(msg)
        self.cprlon = decoder.get_cprlon(msg)

    # -------------------------------------------------------------------------
    # method decode_speed and heading
    # -------------------------------------------------------------------------
    def decode_speed_heading(self, msg):
        self.speed, self.heading = decoder.get_speed_heading(msg)


    # =========================================================================
    #
    #      method of obtainment of datos of message in protocol ads-b
    #
    # =========================================================================

    # -------------------------------------------------------------------------
    # process_position
    # -------------------------------------------------------------------------
    def process_position(self, msg):
        # 0 -> Even frame - 1 -> Odd frame
        l_iEvenOddAtu = int(decoder.get_oe_flag(msg))

        # save message
        if l_iEvenOddAtu == 1:
           self.lastOddMsg = msg
           self.mostRecentType = "odd"           
        else:
           self.lastEvenMsg = msg
           self.mostRecentType = "even"

        # initialize times msg
        if self.mostRecentType == "even":
           t0 = 1
           t1 = 0
        else:
           t0 = 0
           t1 = 1

        # decode position altitude and longitude
        #if self.lastOddMsg and self.lastEvenMsg:
        if len(self.lastOddMsg) > 0 and len(self.lastEvenMsg) > 0:
           # if cannot decoded, the method will return None, None
           
           if len(self.lastOddMsg) != len(self.lastEvenMsg):
              return
			   
           try:
              _lat, _lon =  decoder.get_position(self.lastEvenMsg, self.lastOddMsg, t0, t1)
           except ValueError:
              return

           if _lat and _lon:
              self.lat = _lat
              self.lon = _lon
           else:
              return


           # clear attributes
           self.lastEvenMsg = ""
           self.lastOddMsg  = ""


           # decode altitude
           #self.alt = decoder.get_alt(msg) * self.FT_TO_M
           self.alt = decoder.get_alt(msg)  # FT

           # convert message ads-b for protocol icea
           self.adsb_icea()


    # -------------------------------------------------------------------------
    # process_velocity
    # -------------------------------------------------------------------------
    def process_velocity(self, msg):

        # int(spd), hdg, int(rocd), tag
        (spd, hdg, rocd, tag) = decoder.get_velocity(msg)

        #self.speed      = spd * self.KT_TO_MPS
        self.speed      = spd  # KT
        self.azimuth    = hdg
        self.climb_rate = rocd * self.FTPM_TO_MPS
        return True


    # -------------------------------------------------------------------------
    # process_identification
    # -------------------------------------------------------------------------
    def process_identification(self, msg):
        self.callsign = decoder.get_callsign(msg).replace("_","")
        return True


    # =========================================================================
    #
    #      method of convertion of protocol ads-b for protocol icea
    #
    # =========================================================================


    # -------------------------------------------------------------------------
    # convertion of float to hex
    # -------------------------------------------------------------------------
    def float_to_hex(self, f):
       return hex(struct.unpack('<I', struct.pack('<f', f))[0])

    # -------------------------------------------------------------------------
    # method adsb_icea
    # -------------------------------------------------------------------------
    def adsb_icea(self):

        # ---------------------------------------------------------------------
        # prepare message with datos for protocol icea (header+PR99)
        # ---------------------------------------------------------------------

        # initialize attributs of class PR99
        self.stPR99._btCode        = 0xFF
        self.stPR99._btMonograma   = 'G'
        self.stPR99._btTCord       = 'C'
        self.stPR99._bSPI          = False
        self.stPR99._btPrcRadar    = False               # tagPR99.PR800_NUMBER;
        self.stPR99._bReal         = True
        self.stPR99._bSimulada     = False
        self.stPR99._bSintese      = False
        self.stPR99._bTeste        = False
        self.stPR99._btQual        = 0x6E
        self.stPR99._btDetc        = 0
        self.stPR99._wTrkNo        = random.randint(0,10)
        self.stPR99._enTrack       = 0                   # tagPR99.xxSSR
        self.stPR99._enAux         = 0                   # tagPR99.xxNUL

        # coordenadas da pista (em milhas nauticas - NM)
        _alt= (self.alt * self.FT_TO_M)
        X, Y, Z = self.geog2enu(self.lat, self.lon, _alt, self.latrad, self.lonrad, self.altrad)

        X_M_NM = (X * M_NM)
        Y_M_NM = (Y * M_NM)
        Z_M_NM = 0.0 #(Z * M_NM)

        if X_M_NM <= -60.0:
           print "+++++++++++++++++++++++++++++++++++++++++++++++++++++"
           print "[adsb_icea] DX : %f" % (X_M_NM)
           print "self.stPR99._dX <= -60"
           print
           print  "AERONAVE NAO PROCESSADA"
           print "+++++++++++++++++++++++++++++++++++++++++++++++++++++"
           print
           self.clearAttributes()
           return

        if Y_M_NM <= -60.0:
           print "+++++++++++++++++++++++++++++++++++++++++++++++++++++"
           print "[adsb_icea] DY : %f" % (Y_M_NM)
           print "self.stPR99._dY <= -60"
           print
           print  "AERONAVE NAO PROCESSADA"
           print "+++++++++++++++++++++++++++++++++++++++++++++++++++++"
           print
           self.clearAttributes()
           return

        if X_M_NM >= 60.0:
           print "+++++++++++++++++++++++++++++++++++++++++++++++++++++"
           print "[adsb_icea] DX : %f" % (X_M_NM)
           print "self.stPR99._dX > 60"
           print
           print  "AERONAVE NAO PROCESSADA"
           print "+++++++++++++++++++++++++++++++++++++++++++++++++++++"
           print
           self.clearAttributes()
           return

        if Y_M_NM >= 60.0:
           print "+++++++++++++++++++++++++++++++++++++++++++++++++++++"
           print "[adsb_icea] DY : %f" % (Y_M_NM)
           print "self.stPR99._dY > 60"
           print
           print  "AERONAVE NAO PROCESSADA"
           print "+++++++++++++++++++++++++++++++++++++++++++++++++++++"
           print
           self.clearAttributes()
           return

        # coordenadas da pista (em milhas nauticas - NM)
        self.stPR99._dX  = X_M_NM
        self.stPR99._dY  = Y_M_NM
        self.stPR99._dZ  = Z_M_NM

        # velocidade (em KT)
        if self.speed <= 0:
           #self.stPR99._siVel      = 0
           self.clearAttributes()
           return
        else:
           self.stPR99._siVel      = int(self.speed)

        # delta DX, DY
        #dx  = (self.speed*10) * math.sin(self.azimuth*DEG_RAD)
        #dy  = (self.speed*10) * math.cos(self.azimuth*DEG_RAD)
        self.stPR99._siDX          = 0 #int((dx * M_NM))
        self.stPR99._siDY          = 0 #int((dy * M_NM))

        # nivel de voo (calcula altitude em centena de pes)
        alt = int (self.alt / 100)
        if alt <= 0:
           #self.stPR99._siNivel    = 0
           self.clearAttributes()
           return
        else:
           self.stPR99._siNivel    = alt

        # proa (direcao em graus)
        self.stPR99._dProa         = int(self.azimuth)

        # modo
        self.stPR99._cTMode        = 'A'


        # codigo transponder
        #self.stPR99._szSSR         = '4231'
        self.stPR99._szSSR = '%04d' % random.randint(0,7777)

        # identificacao da pista (call sign)
        # --------------------------------------------------------------
        _szCSign = ''

        # Extract lenght callsign
        n = len(self.callsign)

        # Putting all to uppercase, just in case
        self.callsign = str(self.callsign).upper()

        # Extract characters of callsign
        for i in range(0, n):
            _szCSign += self.callsign[i]

        # Complete with null the remaining bytes
        '''if 8 - n > 0:
           for i in range(n, 8):
               _szCSign += '\0'
        '''

        if len(self.callsign) <= 0:
           print
           print "+++++++++++++++++++++++++++++++++++++++++++++++++++++"
           print  "AERONAVE NAO PROCESSADA"
           print "**** NAO TEM CALLSIGN *****"
           print "+++++++++++++++++++++++++++++++++++++++++++++++++++++"
           print
           self.clearAttributes()
           return
        else:
           self.stPR99._szCSign = _szCSign

        # output
        print "[adsb_icea] self.icao24      : %s" % (self.icao24)

        # ---------------------------------------------------------------------
        # prepare message header
        # ---------------------------------------------------------------------

        # converts message PR99 for hexa
        msgPR99 = self.stPR99.tohex()

        # initialize some specifics attributes of class HeaderPR99
        self.stPR99.l_stHeaderPR99._ucLen     = len(msgPR99)            # LEN   = g_iIndMsgOut
        self.stPR99.l_stHeaderPR99._ucIndic   = 0                       # INDIC = 0
        self.stPR99.l_stHeaderPR99._usComp    = len(msgPR99) + 48       # COMP  = InvertShort( (short)(g_iIndMsgOut + xxTAMCABECALHO) )
        self.stPR99.l_stHeaderPR99._siNMsg    = len(msgPR99)            # NMSG  = InvertInt(g_iMsgCount)

        # convert message HeaderPR99 for hexa
        headerPR99 = self.stPR99.l_stHeaderPR99.tohex()

        # ---------------------------------------------------------------------
        # prepare message complete (header+PR99)
        # ---------------------------------------------------------------------
        message = headerPR99 + msgPR99


        # instance new object Aeronave
        l_Aeronave = Aeronave()
        
        # initialize datos of object Aeronave
        l_Aeronave._icao24   = self.icao24
        l_Aeronave._wTrkNo   = self.stPR99._wTrkNo
        l_Aeronave._enTrack  = self.stPR99._enTrack
        l_Aeronave._enAux    = self.stPR99._enAux
        l_Aeronave._dX       = self.stPR99._dX
        l_Aeronave._dY       = self.stPR99._dY
        l_Aeronave._dZ       = self.stPR99._dZ
        l_Aeronave._siNivel  = self.stPR99._siNivel
        l_Aeronave._siVel    = self.stPR99._siVel
        l_Aeronave._dProa    = self.stPR99._dProa
        l_Aeronave._cTMode   = self.stPR99._cTMode
        l_Aeronave._szSSR    = self.stPR99._szSSR
        l_Aeronave._szCSign  = self.stPR99._szCSign
        
        # initialize datos of Message on object Aeronave
        l_Aeronave._Message._icao24    = self.icao24
        l_Aeronave._Message._szCSign   = self.stPR99._szCSign
        l_Aeronave._Message._szMessage = binascii.unhexlify(message)

        # output
        # print l_Aeronave

        l_indLst = 0
        l_bAchei = False

        # search object equal on list
        if len(self.aeronaveList) >= 1:
           self.aeronaveList.sort(key=operator.attrgetter('_szCSign'))
           for aeronave in self.aeronaveList:
               if self.stPR99._szCSign in aeronave._szCSign:

                  # a cada chamada deste metodo, o sistema gera um numero da pista
                  # se a pista ja foi cadastrada na lista, este trecho do codigo
                  # procura preservar o numero da pista gerado pela primeira vez
                  # entretanto tem que atualizar o objeto 'self.stPR99' com os dados
                  # da aeronave da lista para que possa ser gerada uma nova mensagem
                  if int(aeronave._wTrkNo) != int(l_Aeronave._wTrkNo):

                     # update datos of track with datos of object aircraft of list
                     self.stPR99._dX      = aeronave._dX
                     self.stPR99._dY      = aeronave._dY
                     self.stPR99._dZ      = aeronave._dZ
                     self.stPR99._siNivel = aeronave._siNivel
                     self.stPR99._siVel   = aeronave._siVel
                     self.stPR99._dProa   = aeronave._dProa
                     self.stPR99._cTMode  = aeronave._cTMode
                     self.stPR99._szSSR   = aeronave._szSSR
                     self.stPR99._szCSign = aeronave._szCSign
                     self.stPR99._wTrkNo  = aeronave._wTrkNo

                     # convert new message PR99 for hexa
                     msgPR99 = self.stPR99.tohex()

                     # initialize some specifics attributes of class HeaderPR99
                     self.stPR99.l_stHeaderPR99._ucLen     = len(msgPR99)
                     self.stPR99.l_stHeaderPR99._ucIndic   = 0
                     self.stPR99.l_stHeaderPR99._usComp    = len(msgPR99) + 48
                     self.stPR99.l_stHeaderPR99._siNMsg    = len(msgPR99)

                     # convert new message HeaderPR99 for hexa
                     headerPR99 = self.stPR99.l_stHeaderPR99.tohex()

                     # prepare message complete update (header+PR99)
                     message = headerPR99 + msgPR99


                     # destroy atual object 
                     l_Aeronave = None

                     # instance new object Aeronave
                     l_Aeronave = Aeronave()
        
                     # initialize datos of object Aeronave
                     l_Aeronave._icao24   = self.icao24
                     l_Aeronave._wTrkNo   = self.stPR99._wTrkNo
                     l_Aeronave._enTrack  = self.stPR99._enTrack
                     l_Aeronave._enAux    = self.stPR99._enAux
                     l_Aeronave._dX       = self.stPR99._dX
                     l_Aeronave._dY       = self.stPR99._dY
                     l_Aeronave._dZ       = self.stPR99._dZ
                     l_Aeronave._siNivel  = self.stPR99._siNivel
                     l_Aeronave._siVel    = self.stPR99._siVel
                     l_Aeronave._dProa    = self.stPR99._dProa
                     l_Aeronave._cTMode   = self.stPR99._cTMode
                     l_Aeronave._szSSR    = self.stPR99._szSSR
                     l_Aeronave._szCSign  = self.stPR99._szCSign
        
                     # initialize datos of Message on object Aeronave
                     l_Aeronave._Message._icao24    = self.icao24
                     l_Aeronave._Message._szCSign   = self.stPR99._szCSign
                     l_Aeronave._Message._szMessage = binascii.unhexlify(message)

                     # remove object on list
                     self.aeronaveList.pop( l_indLst )
                     #self.aeronaveList.remove( self.Aeronave )

                     # update datos of object on list
                     self.aeronaveList.append( l_Aeronave )
                     l_bAchei = True

                     break
               else:
                  l_indLst += 1

        if l_bAchei == False:
           # save object on list
           self.aeronaveList.append( l_Aeronave )

        # destroy object
        l_Aeronave = None

        # output objects of list
        '''
        self.aeronaveList.sort(key=operator.attrgetter('_szCSign'))
        for anv in self.aeronaveList:
            print "[adsb_icea] aeronaveList: _szCSign: %s  _siNivel: %03d  _siVel: %03d  _dProa: %03d" % (anv._szCSign, anv._siNivel, anv._siVel, anv._dProa)
        print '---------------------------------------------------------------------'
        print
        '''

        # ---------------------------------------------------------------------
        # send message udp for VisIR or CommServer->STVD
        # ---------------------------------------------------------------------
        #hex_msg = binascii.unhexlify(message)
        #self.sendmessage(hex_msg)

    # eol def adsb_icea



    # =========================================================================
    #
    #                     methods for the process of message 
    #
    # =========================================================================

    # -----------------------------------------------------------------------------------------
    # start_threaded
    # -----------------------------------------------------------------------------------------
    def start_threaded(self):
        t1 = threading.Thread(target=self.airborne_position_threaded, args=())
        t1.start()


    # -----------------------------------------------------------------------------------------
    # airborne_position_threaded
    # -----------------------------------------------------------------------------------------
    def airborne_position_threaded(self, rate=4.0):

        while True:

            time_ini = int (time.time())

            # process aircrafts for each sector (max 32)
            for setor in range(0, MAX_SETOR):

               # create list of aircrafts by setor
               anvSetorList = []

               # sort objects of list through of callsign
               self.aeronaveList.sort(key=operator.attrgetter('_szCSign'))

               # get objects of list
               for anv in self.aeronaveList:

                   # calculate radial
                   RadialCabRad = self.ProaDemanda ( anv._dX, anv._dY )

                   # calculates that sector the aircraft belongs.
                   setorAnv = int( RadialCabRad / DEG_SETOR )

                   # aircraft is in the current sector
                   if int(setor) == setorAnv:

                      # save aircraft on list
                      anvSetorList.append( anv )

               # end for anv

               # exist aircrafts on the current sector?
               if len(anvSetorList) > 0:

                  # output
                  #print "[threaded]  ------------ SETOR ATUAL : %d ---------------- " % int(setor)

                  for anvSetor in anvSetorList:

                      # output
                      '''print "[threaded] _szCSign    : %s" % (anvSetor._Message._szCSign)
                      print "[threaded] DX          : %f" % (anvSetor._dX)
                      print "[threaded] DY          : %f" % (anvSetor._dY)
                      print "[threaded] Altitude    : %d" % int(anvSetor._siNivel)
                      print "[threaded] Speed    KT : %d" % int(anvSetor._siVel)
                      print "[threaded] Proa        : %d" % int(anvSetor._dProa)
                      RadialCabRad = self.ProaDemanda ( anvSetor._dX, anvSetor._dY )
                      print "[threaded] RadialCabRad: %d" % int(RadialCabRad)
                      print'''

                      # send message
                      self.sendmessage(anvSetor._Message._szMessage)

                  # destroy list anvSetorList
                  del anvSetorList

               else:
                  # prepare message empty sector  - class PR95
                  self.stPR95._btCode        = 0xFD
                  self.stPR95._btMonograma   = 'G'
                  self.stPR95._btSetor       = int(setor)
                  self.stPR95._btDivisor     = int(MAX_SETOR)

                  # convert message PR95 for hexa
                  msgPR95 = self.stPR95.tohex()

                  # initialize some specifics attributes of class HeaderPR99
                  self.stPR95.l_stHeaderPR99._ucLen     = len(msgPR95)            # LEN   = g_iIndMsgOut
                  self.stPR95.l_stHeaderPR99._ucIndic   = 0                       # INDIC = 0
                  self.stPR95.l_stHeaderPR99._usComp    = len(msgPR95) + 48       # COMP  = InvertShort( (short)(g_iIndMsgOut + xxTAMCABECALHO) )
                  self.stPR95.l_stHeaderPR99._siNMsg    = len(msgPR95)            # NMSG  = InvertInt(g_iMsgCount)

                  # convert message Header for hexa
                  header = self.stPR95.l_stHeaderPR99.tohex()

                  # prepare message complete (header+PR95)
                  message = header + msgPR95

                  # send message
                  hex_msg = binascii.unhexlify(message)
                  self.sendmessage(hex_msg)

            # end for setor

            time_fim = int(time.time())

            dif_time = int(time_fim - time_ini)

            if dif_time > 0:
               _time = int(rate - dif_time)
            else:
               _time = rate

            '''
            print
            print "rate    : %d" % (rate)
            print "time_ini: %d" % (time_ini)
            print "time_fim: %d" % (time_fim)
            print "DIF time: %d" % (dif_time)
            print "_time   : %d" % int(_time)
            print
            '''

            if _time > 0:
               time.sleep(_time)
            else:
               time.sleep(1)

        # end  while

    # end  airborne_position_threaded


    # -------------------------------------------------------------------------
    # method ProaDemanda
    # -------------------------------------------------------------------------
    def ProaDemanda(self, pntDeltX, pntDeltY ):

        # calcula a nova radial (proa de demanda)
        if pntDeltX > 0:
          return ( DEG_PI_2 - math.atan (( pntDeltY / pntDeltX ) * RAD_DEG ) )
   
        if pntDeltX < 0:
           angTemp = DEG_3PI_2 - math.atan (( pntDeltY / pntDeltX ) * RAD_DEG )

           if angTemp >= DEG_2PI:
              return ( angTemp - DEG_2PI )
           else:
              return angTemp

        if pntDeltY >= 0:
           return ( 0 )
        else:
           return ( DEG_PI )

    # end ProaDemanda()



    # -------------------------------------------------------------------------
    # process_first_id_msg
    # -------------------------------------------------------------------------
    def process_first_id_msg(self, msg):
        icao24 = decoder.get_icao_addr(msg)
        tc = decoder.get_tc(msg)

        # is aircraft identification message?
        if tc in range(1,5):
            self.icao24   = icao24
            self.callsign = decoder.get_callsign(msg).replace("_","")
            return True

        return False


    # -------------------------------------------------------------------------
    # method process_message_core
    # -------------------------------------------------------------------------
    def process_message_core(self):

        print "process_message_core()"
        print "read message UDP"
        print ""

        while True:
            # read message core
            msg, cliente = self.sock.recvfrom(1024)

            # send message udp for VisIR or CommServer->STVD
            self.sendmessage(msg)
        # end while

        # close connection
        self.sock.close()

    # end process_message_core()


    # -------------------------------------------------------------------------
    # method process_message_dump1090
    # -------------------------------------------------------------------------
    def process_message_dump1090(self):
       
        print "process_message_dump1090()"
        print "read message TCP"
        print ""

        # process messages from dump1090
        while True:

            # read message
            data = self.sock.recv(self.BUFFER_SIZE)
            
            # extract of message the characters "\n, *, ;"
            msg = data.replace("\n","")
            msg = msg.replace("*","")
            msg = msg.replace(";","")
            
            # empty message ?
            if msg is None:
               print 'empty message .....!!!'
               continue

            # message without characters
            data = msg

            # checking type message (DF=17 - 112 bits)?
            self.decode_DF(data)
            if self.df != 17:
               #print "message ads-b [< 112 bits]...:", str(data)
               continue

            '''
            # extract address icao of message
            icao24_msg = decoder.get_icao_addr(data)

            # first message? update current icao addr and callsign
            if self.icao24 is None:
               self.process_first_id_msg(data)
               continue
               
            # Process only msgs with icao24 = self.icao24
            if icao24_msg != self.icao24:
               continue
            '''

            self.decode_icao24(data)

            # extract type code (tc) of message
            #
            #  DF = 17 (msg 112 bits)
            #  |
            #  |__ TC = 1 to 4  -> msg Aircraft identification
            #  |__ TC = 9 to 18 -> msg Airborne position (Baro Alt)
            #  |__ TC = 19      -> msg Airborne velocities
            # 
            self.decode_tc(data)

            # message is airbone_position?
            #if self.tc in range(9,19):
            if self.tc == 11:
               self.process_position(data)
            
            # message is airborne velocity?
            elif self.tc == 19:
                 self.process_velocity(data)

            # message is aircraft identification?
            #elif self.tc in range(1,5):
            elif self.tc == 4:
                 self.process_identification(data)

            # decode message ads-b
            self.decode_CA(data)
            self.decode_icao24(data)
            self.decode_st(data)
            self.decode_nic(data)
            self.decode_time(data)
            self.decode_cpr(data)
    
            '''
            # output
            print ""
            print "--------------------------------------------------------------------------"
            print "message ads-b......................:", str(data)
            print ""
            print 'Downlink Format (DF)...............:', self.df
            print 'Message Subtype (CA)...............:', self.ca
            print 'ICAO aircraft address..............:', self.icao24
            print 'Callsign...........................:', self.callsign
            print 'Type Code (TC).....................:', self.tc
            print 'Surveillance status (ST)...........:', self.st
            print 'Navigation Integrity Category (NIC):', self.nic
            print 'Altitude (Ft)......................:', self.alt
            print 'Time...............................:', self.time
            print 'CPR odd/even flag..................:', self.cpr
            print 'Latitude in CPR format.............:', self.cprlat
            print 'Longitude in CPR format............:', self.cprlon
            print 'Latitude...........................:', self.lat
            print 'Longitude..........................:', self.lon
            print 'speed..............................:', self.speed
            print 'azimuth............................:', self.azimuth
            '''             
        # end while

        # close connection
        self.sock.close()

    # end process_message_dump1090()


    # -----------------------------------------------------------------------------------------
    # start
    # -----------------------------------------------------------------------------------------
    def start(self):

        # output
        print "------------------------------------------------------------------------------------"
        print "start()"
        print "Connecting to %s:%s  : " % (self.net_client, self.port_read)
        print 'self.destination_type: ',self.destination_type
        print ""

        self.start_threaded()

        if self.destination_type == DST_CORE:
            self.process_message_core()
        elif self.destination_type == DST_DUMP1090:
            self.process_message_dump1090()

# end class ICEA
# -----------------------------------------------------------------------------

 

# -----------------------------------------------------------------------------
# method main
# -----------------------------------------------------------------------------
def main():
    # create logger with 'adsb_in_app'
    logger = logging.getLogger('icea_app')
    logger.setLevel(logging.DEBUG)

    # create a console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s -%(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(ch)

    # instance the object ICEA
    logger.info('Creating an instance of ICEA')
    '''
    icea = ICEA(destination="172.18.104.255", portRead=60000, portWrite=65000, destination_type="core")
    icea = ICEA(destination="172.18.104.186", portRead=30002, portWrite=65000, destination_type="dump1090")
    '''
    icea = ICEA(destination="172.18.104.186", portRead=30002, portWrite=64000, destination_type="dump1090")

    # Execute application
    logger.info('Executing application')
    icea.start()


# -----------------------------------------------------------------------------
# method main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
