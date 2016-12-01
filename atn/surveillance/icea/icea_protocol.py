"""--------------------------------------------------------------------------
Project ADS-B Security
Copyright (c) 2016, ICEA - Institute of Airspace Control
-----------------------------------------------------------------------------
Package....: radar/icea
Module.....: tagPR95.py
Description: This class formats and preparing message for protocol icea
             (header+PR99)
-----------------------------------------------------------------------------
Details change
-----------------------------------------------------------------------------
Alexandre MG Silva  2016/06/23
                    program created
                    documentation of class in docstrings

Alexandre MG Silva  2016/06/29
                    inclusion of treatment coverage of primary and secondary
                    radars
--------------------------------------------------------------------------"""

import socket
import getopt
import sys
import logging
import math
import time
import struct
import binascii
import ctypes
import array

import threading
import operator

import random

import ConfigParser
import os

from tagPR95 import tagPR95
from tagPR99 import tagPR99

# -----------------------------------------------------------------------------
# class ICEA
# -----------------------------------------------------------------------------
class Icea:

    RAD_DEG = 57.29577951       # Converte RAD para DEG
    DEG_RAD = 0.017453292       # Converte DEG para RAD
    MPS_NOS	= 1.94384           # 3600 : 1852
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

    BUFFER_SIZE   = 1024

    FT_TO_M      = 0.3048
    KT_TO_MPS    = 0.514444
    FTPM_TO_MPS  = 0.00508

    TAMCABECALHO = 50

    # -------------------------------------------------------------------------
    # method constructor (__init__)
    # -------------------------------------------------------------------------
    def __init__(self, config="radar.cfg"):

        """
        Initialize attributs of class
        """

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

        self.xxASS            = 0     # associada
        self.xxCAN            = 1     # cancelada
        self.xxINI            = 2     # iniciada
        self.xxPRI            = 3     # primaria
        self.xxSSR            = 4     # secundaria

        # instance object tagPR95
        self.stPR95 = tagPR95()

        # instance object tagPR99
        self.stPR99 = tagPR99()

        # counter global of messages
        self.countmgs = 0

        # Reading configuration file
        if os.path.exists(config):
            print "Configuration file %s found." % config
            conf = ConfigParser.ConfigParser()
            conf.read(config)

            # Radar position
            self.latitude          = conf.getfloat("Location", "latitude")
            self.longitude         = conf.getfloat("Location", "longitude")
            self.altitude          = conf.getfloat("Location", "altitude")

            # Radar parameters
            self.psr_coverage      = conf.getint("PSR", "psr_horizontal_coverage")
            self.ssr_coverage      = conf.getint("PSR", "ssr_horizontal_coverage")
            self.vertical_coverage = conf.getint("PSR", "vertical_coverage")
            self.min_angle         = conf.getint("PSR", "min_angle")
            self.max_angle         = conf.getint("PSR", "max_angle")
        else:
            # Radar position
            self.latitude          = -19.174167
            self.longitude         = -47.198333
            self.altitude          = 2681

            # Radar parameters
            self.psr_coverage      = 80
            self.ssr_coverage      = 240
            self.vertical_coverage = 60000
            self.min_angle         = 0
            self.max_angle         = 85


    # -------------------------------------------------------------------------
    # method encode_icea
    # -------------------------------------------------------------------------
    def encode_icea(self, tracks):

        """method encode_icea

        This method has the function to prepare messages in the icea protocol
        format (Header+PR99) of objects are within radar coverage.

        Args:
            tracks: Receive a list of objects (aircrafts)
        """

        if len(tracks) == 0:
            return None

        # search object equal on list
        messages = []

        for track in tracks:

            # get datos of aircraft
            nodenumber = track[0]
            x_pos      = track[1]
            y_pos      = track[2]
            z_pos      = track[3]
            azimuth    = track[4]
            speed      = track[5]
            ssr        = track[6]
            callsign   = track[7]

            # positions the radar screen center
            radX = 0.0
            radY = 0.0

            # calculates the distance from the aircraft to the radar
            dstanvradX = abs(radX - x_pos)
            dstanvradY = abs(radY - y_pos)
            dstanvrad  = math.sqrt ( math.pow(dstanvradX, 2 ) + math.pow(dstanvradY, 2 ) )

            # -----------------------------------------------------------------
            # checks if aircraft is within the radar secondary coverage
            # -----------------------------------------------------------------
            if dstanvrad > self.ssr_coverage:
                print
                print "========"
                print "Aircraft out of SSR radar coverage:"
                print "  ssr           :  %s" % ssr
                print "  callsign      :  %s" % callsign
                print "  dstanvrad     :  %d NM" % dstanvrad
                print "  ssr_coverage  :  %d NM" % self.ssr_coverage
                print "========"
                continue

            # -----------------------------------------------------------------
            # checks if aircraft is within the radar primary coverage
            # -----------------------------------------------------------------
            if len(ssr) <= 2:                                      # ssr=''?

                if self.calculate_coverage_radar(x_pos, y_pos, z_pos) == True:

                    # -----------------------------------------------------------
                    # prepare message PR99 radar primary
                    # -----------------------------------------------------------

                    self.stPR99._btCode        = self.P_P            # 0xFE
                    self.stPR99._btMonograma   = 'G'
                    self.stPR99._btTCord       = 'C'

                    self.stPR99._bSPI          = 0
                    self.stPR99._btPrcRadar    = 0                   # ERRO: sistema nao permite PR800_NUMBER (0x02) em um bit
                    self.stPR99._bReal         = 0
                    self.stPR99._bSimulada     = 0
                    self.stPR99._bSintese      = 0
                    self.stPR99._bTeste        = 1

                    self.stPR99._btQual        = self.QUAL           # 0x6E
                    self.stPR99._btDetc        = 0
                    self.stPR99._wTrkNo        = int (nodenumber)
                    self.stPR99._enTrack       = self.xxPRI          # self.xxPRI = 3
                    self.stPR99._enAux         = 0

                    self.stPR99._dX            = x_pos               # NM
                    self.stPR99._dY            = y_pos               # NM
                    self.stPR99._dZ            = 0                   # unsed

                    self.stPR99._siDX          = 0
                    self.stPR99._siDY          = 0

                    self.stPR99._siNivel       = 0
                    self.stPR99._siVel         = int(speed)
                    self.stPR99._dProa         = int(azimuth)
                    self.stPR99._cTMode        = 'A'
                    self.stPR99._szSSR         = ""
                    self.stPR99._szCSign       = ""
                else:
                    continue
            else:
            # -----------------------------------------------------------------
            # checks if aircraft is within the radar secondary coverage
            # -----------------------------------------------------------------
               if dstanvrad <= self.ssr_coverage:

                  # -----------------------------------------------------------
                  # prepare message PR99 radar secondary
                  # -----------------------------------------------------------

                  self.stPR99._btCode        = self.P_S            # 0xFF
                  self.stPR99._btMonograma   = 'G'
                  self.stPR99._btTCord       = 'C'

                  self.stPR99._bSPI          = 0
                  self.stPR99._btPrcRadar    = 0                   # ERRO: sistema nao permite PR800_NUMBER (0x02) em um bit
                  self.stPR99._bReal         = 0
                  self.stPR99._bSimulada     = 0
                  self.stPR99._bSintese      = 0
                  self.stPR99._bTeste        = 1

                  self.stPR99._btQual        = self.QUAL           # 0x6E
                  self.stPR99._btDetc        = 0
                  self.stPR99._wTrkNo        = int (nodenumber)

                  # checks whether the aircraft is within the coverage of the primary radar and secondary
                  if self.is_in_range(x_pos, y_pos, z_pos) == True:
                     self.stPR99._enTrack       = self.xxASS       # self.xxASS = 0
                  else:
                     self.stPR99._enTrack       = self.xxSSR       # self.xxSSR = 4

                  self.stPR99._enAux         = 0

                  self.stPR99._dX            = x_pos               # NM
                  self.stPR99._dY            = y_pos               # NM
                  self.stPR99._dZ            = 0                   # unsed

                  self.stPR99._siDX          = 0
                  self.stPR99._siDY          = 0

                  self.stPR99._siNivel       = int(z_pos / 100)
                  self.stPR99._siVel         = int(speed)
                  self.stPR99._dProa         = int(azimuth)
                  self.stPR99._cTMode        = 'A'
                  self.stPR99._szSSR         = ssr
                  self.stPR99._szCSign       = callsign

            # -----------------------------------------------------------------
            # prepare message header
            # -----------------------------------------------------------------

            # converts message PR99 for hexa
            msgPR99 = self.stPR99.tohex()

            l_iTamMsg = len(msgPR99)/2
            self.stPR99.l_stHeaderPR99._ucLen     = l_iTamMsg+2
            self.stPR99.l_stHeaderPR99._ucIndic   = 0
            self.stPR99.l_stHeaderPR99._usComp    = l_iTamMsg + self.TAMCABECALHO
            self.stPR99.l_stHeaderPR99._siNMsg    = self.countmgs

            # convert message HeaderPR99 for hexa
            headerPR99 = self.stPR99.l_stHeaderPR99.tohex()

            # -----------------------------------------------------------------
            # prepare message complete (header+PR99)
            # -----------------------------------------------------------------
            message = headerPR99 + msgPR99
            messages.append(message)

            # output
            #print "MSG: ",message

            # -----------------------------------------------------------------
            # increment counter of messages
            # -----------------------------------------------------------------
            self.countmgs += 1
            if self.countmgs > 999:
               self.countmgs = 0

        return messages


    # -------------------------------------------------------------------------
    # method get_empty_sector_msg
    # -------------------------------------------------------------------------
    def get_empty_sector_msg(self, setor):

        """method get_empty_sector_msg

        This method has the function to prepare message in the icea protocol
        format (Header+PR95) of empty sector.

        Args:
            setor: Receive sector actual
        """

        # ---------------------------------------------------------------------
        # prepare message PR95 empty sector
        # ---------------------------------------------------------------------

        self.stPR95._btCode        = 0xFD
        self.stPR95._btMonograma   = 'G'
        self.stPR95._btSetor       = int(setor)
        self.stPR95._btDivisor     = self.MAX_SETOR

        # convert message PR95 for hexa
        msgPR95 = self.stPR95.tohex()

        # initialize some specifics attributes of class HeaderPR99
        l_iTamMsg = len(msgPR95)/2
        self.stPR95.l_stHeaderPR99._ucLen     = l_iTamMsg + 2
        self.stPR95.l_stHeaderPR99._ucIndic   = 0
        self.stPR95.l_stHeaderPR99._usComp    = l_iTamMsg + self.TAMCABECALHO
        self.stPR95.l_stHeaderPR99._siNMsg    = self.countmgs

        # convert message Header for hexa
        header = self.stPR95.l_stHeaderPR99.tohex()

        # prepare message complete (header+PR95)
        message = header + msgPR95

        # increment counter of messages
        self.countmgs += 1
        if self.countmgs > 999:
           self.countmgs = 0

        return message


    # -------------------------------------------------------------------------
    # method calculate_coverage_radar
    # -------------------------------------------------------------------------
    def calculate_coverage_radar(self, x, y, z):
        return self.in_range(x,y,z)

    def is_in_range(self, x, y, z):

        """method calculate_coverage_radar

        This method has the function to calculate whether the aircraft is within
        the radar coverage.

        Args:
            x: x-coordinate of the aircraft
            y: y-coordinate of the aircraft
            z: aircraft altitude
        """

        # positions the radar screen center
        radX = 0.0
        radY = 0.0

        # calculates the distance from the aircraft to the radar
        dstanvradX = abs(radX - x)
        dstanvradY = abs(radY - y)
        dstanvrad  = math.sqrt ( math.pow(dstanvradX, 2 ) + math.pow(dstanvradY, 2 ) )

        # output
        '''
        print "Location of Aircraft:"
        print "  anvX       :  %f" % x
        print "  anvY       :  %f" % y
        print "  anvZ       :  %d FT" % z
        print
        print "Location Radar in  X,Y:"
        print "  radX       :  %f" % radX
        print "  radY       :  %f" % radY
        print
        print "Distance of aircraft from radar:"
        print "  dstanvradX :  %f" % dstanvradX
        print "  dstanvradY :  %f" % dstanvradY
        print "  dstanvrad  :  %d NM" % dstanvrad
        print
        '''

        # radar coverage applies filters
        if z > (self.altitude + self.vertical_coverage):
            # print "Out coverage: z [%d] > altitude + vertical_coverage [%d] FT" % (z, self.altitude + self.vertical_coverage)
            # print
            return False

        if z < self.altitude:
            # print "Out coverage: z [%d] < altitude [%d] FT" % (z, self.altitude)
            # print
            return False

        if dstanvrad == 0:
            # print "Out coverage: dstanvrad [%d] NM" % (dstanvrad)
            # print
            return False

        #if dstanvrad > self.ssr_coverage:
        if dstanvrad > self.psr_coverage:
            # print "Out coverage: dstanvrad [%d] > psr_coverage [%d] NM" % (dstanvrad, self.psr_coverage)
            # print
            return False

        # calculate angles min and max
        tmp   = math.atan2(z, dstanvrad)
        angle = ( (tmp * 180.0) / 3.1416 )

        # output
        '''
        print "Calc. Angles (min/max) of radar:"
        print "  tmp        :  %d" % tmp
        print "  angle      :  %d" % angle
        print
        '''

        if angle < self.min_angle:
            # print "Out coverage: angle [%d] < Angle min [%d]" % (angle, self.min_angle)
            # print
            return False

        if angle > self.max_angle:
            # print "Out coverage: angle [%d] > Angle max [%d]" % (angle, self.max_angle)
            # print
            return False
        else:
            return True

