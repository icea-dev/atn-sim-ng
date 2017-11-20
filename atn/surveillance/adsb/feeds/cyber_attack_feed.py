#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
This file is part of atn-sim

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

revision 0.1  2017/Nov  Matias
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
# < imports >--------------------------------------------------------------------------------------
import logging
import netifaces as ni
import socket
import threading
import time

from .adsb_feed import AdsbFeed

__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/04"


class CyberAttackFeed(AdsbFeed):
    """
    Class that provides information for ADS-B Out transponders.
    Receives the information from the fake aircraft.
    The aircraft information is read through the CyberAttack.
    """

    # 'CA' Capability Field : 5 - Signifies Level 2 or above transponder, and the ability to set "CA"
    # code 7, and airbone
    CA = 5

    # ADS-B Emitter Category used to identify particular aircraft
    # 0 : No ADS-B Emitter Category Information
    EMITTER_CATEGORY = 0

    FT_TO_M = 0.3048
    KT_TO_MPS = 0.51444444444

    CALLSIGN = 'cs'
    GROUND_SPEED = 'gs'
    HEADING = 'h'
    VERTICAL_RATE = 'vr'
    ODD_MSG = 'om'
    EVEN_MSG = 'em'
    LAST_TYPE = 'lt'
    LATITUDE = 'lat'
    LONGITUDE = 'lng'
    ALTITUDE = 'alt'

    # -------------------------------------------------------------------------------------------------
    def __init__(self, fb_send_data_radar=True):
        """
        Constructor
        """
        logging.info(">> CyberAttackFeed.__init__")

        # Locking
        self.__data_lock = threading.Lock()
        self.__dict_lock = threading.Lock()

        self.__d_ptracks_data = {}

        # Init attributes aircraft data
        self.__s_ssr = None
        self.__b_spi = False
        self.__f_altitude = 0
        self.__f_latitude = 0
        self.__f_longitude = 0
        self.__f_ground_speed = 0
        self.__f_vertical_rate = 0
        self.__f_heading = 0
        self.__s_callsign = None
        self.__s_aircraft_type = None
        self.__l_timestamp = 0
        self.__l_old_timestamp = 0
        self.__s_icao24 = None

        logging.info("<< CyberAttackFeed.__init__")

    # -------------------------------------------------------------------------------------------------
    def get_ssr(self):
        """
         Returns the current squawk code of the aircraft.

        :return: string
        """
        self.__data_lock.acquire()
        ls_ssr = self.__s_ssr
        self.__data_lock.release()

        return ls_ssr


    # -------------------------------------------------------------------------------------------------
    def get_spi(self):
        """
        Returns the status of Special Pulse Identification (SPI) of aircraft
        :return: bool, True SPI is activated otherwise False
        """
        self.__data_lock.acquire()
        lb_spi = self.__b_spi
        self.__data_lock.release()

        return lb_spi


    # -------------------------------------------------------------------------------------------------
    def get_callsign(self):
        """
        Returns the callsign of aircraft
        :return: string
        """
        self.__data_lock.acquire()
        ls_callsign = self.__s_callsign
        self.__data_lock.release()

        return ls_callsign


    # -------------------------------------------------------------------------------------------------
    def get_timestamp(self):
        """
        Returns the timestamp of aircraft
        :return: float
        """
        self.__data_lock.acquire()
        ll_timestamp = self.__l_timestamp
        self.__data_lock.release()

        return ll_timestamp


    # -------------------------------------------------------------------------------------------------
    def get_position(self):
        """
        Returns latitude, longitude and altitude of aircraft
        :return: (latitude in degrees, longitude in degress, altitude in meters)
        """
        self.__data_lock.acquire()
        lf_latitude = self.__f_latitude
        lf_longitude = self.__f_longitude
        lf_altitude = self.__f_altitude
        self.__data_lock.release()

        return lf_latitude, lf_longitude, lf_altitude


    # -------------------------------------------------------------------------------------------------
    def get_velocity(self):
        """
        Returns heading, vertical rate and ground speed of aircraft
        :return: (heading in degrees, vertical rate in meters per second, ground speed in meters per second)
        """
        self.__data_lock.acquire()
        lf_heading = self.__f_heading
        lf_vertical_rate = self.__f_vertical_rate
        lf_ground_speed = self.__f_ground_speed
        self.__data_lock.release()

        # Esperar ajuste no ptracks, com a informação do ptracks não funciona !!!! Tem que ser zero.
        return lf_heading, 0, lf_ground_speed


    # -------------------------------------------------------------------------------------------------
    def get_icao24(self):
        """
        Returns the ICAO 24 bit code identifier of aircraft
        :return: ICAO 24 bit code
        """
        self.__data_lock.acquire()
        ls_icao24 = self.__s_icao24
        self.__data_lock.release()

        return ls_icao24


    # -------------------------------------------------------------------------------------------------
    def get_capabilities(self):
        """
        Returns the capability of an ADS-B trasnmitting installation that is based on a Mode-S transponder

        :return: int
        """
        return self.CA


    # -------------------------------------------------------------------------------------------------
    def get_type(self):
        """
        Returns the field that shall be used the identify particular aircraft or vehicle types within
        the ADS-B Emitter Category Sets A, B, C or D identified by Message Format TYPE Codes 4, 3, 2 and 1
        , respectively.
        :return: int
        """
        return self.EMITTER_CATEGORY


    # -------------------------------------------------------------------------------------------------
    def is_track_updated(self):
        """
        Check if aircraft data is updated.
        :return: bool, True if aircraft is updated otherwise False
        """
        return True

    # -------------------------------------------------------------------------------------------------
    def start(self):
        """
        Starts reading aircraft data from CyberAttack
        :return:
        """
        return

    # -------------------------------------------------------------------------------------------------
    def process_message(self, f_dct_aircraft=None, f_s_icao24_fake=None):
        """
        Processes the message from the Cyber Attack.

        :param fdict_aircraft: the information from the fake aircraft
        :return: None:
        """

        # SSR
        self.__s_ssr = "0000"

        # SPI
        self.__b_spi = False

        # Altitude (meters)
        self.__f_altitude = f_dct_aircraft[self.ALTITUDE]

        # Latitude (degrees)
        self.__f_latitude = f_dct_aircraft[self.LATITUDE]

        # Longitude (degrees)
        self.__f_longitude = f_dct_aircraft[self.LONGITUDE]

        # Ground speed (m/s)
        self.__f_ground_speed = f_dct_aircraft[self.GROUND_SPEED]

        # Vertical rate (m/s)
        self.__f_vertical_rate = f_dct_aircraft[self.VERTICAL_RATE]

        # Heading (degrees)
        self.__f_heading = f_dct_aircraft[self.HEADING]

        # Callsign
        self.__s_callsign = f_dct_aircraft[self.CALLSIGN]

        # Aircraft performance type
        self.__s_aircraft_type = None

        # Timestamp
        #self.old_timestamp = self.timestamp
        self.__l_timestamp = 0

        # ICAO 24 bit code
        self.__s_icao24 = f_s_icao24_fake


# < the end >--------------------------------------------------------------------------------------
