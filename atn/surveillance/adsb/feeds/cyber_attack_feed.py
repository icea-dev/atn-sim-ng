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
import math
import random
import threading
import time
import atn.surveillance.adsb.security.glb_defs as ldefs

from .adsb_feed import AdsbFeed


M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)


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

        self.__f_hacker_lat = 0.0
        self.__f_hacker_lng = 0.0
        self.__f_hacker_alt = 0.0

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

    # ---------------------------------------------------------------------------------------------
    def calculate_kinematics(self):
        """

        :return:
        """
        logging.info(">> CyberAttackFeed.calculate_kinematics")
        ff_heading_radians = math.radians(self.__f_heading)
        ff_dx = (self.__f_ground_speed * ldefs.NM_H_TO_NM_S * math.sin(ff_heading_radians)) / 60.
        ff_dy = (self.__f_ground_speed * ldefs.NM_H_TO_NM_S * math.cos(ff_heading_radians)) / 60.

        self.__f_longitude += ff_dx
        self.__f_latitude += ff_dy

        logging.info("<< CyberAttackFeed.calculate_kinematics")

        return


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
    def get_hacker_position(self):
        """
        Returns latitude, longitude and altitude of hacker
        :return: (latitude in degrees, longitude in degress, altitude in meters)
        """
        self.__data_lock.acquire()
        lf_latitude = self.__f_hacker_lat
        lf_longitude = self.__f_hacker_lng
        lf_altitude = self.__f_hacker_alt
        self.__data_lock.release()

        return lf_latitude, lf_longitude, lf_altitude


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
    def set_position(self, ff_latitude, ff_longitude, ff_altitude):
        """

        :param ff_latitude:
        :param ff_longitude:
        :param ff_altitude:
        :return:
        """
        self.__f_hacker_alt = ff_altitude
        self.__f_hacker_lat = ff_latitude
        self.__f_hacker_lng = ff_longitude



    # -------------------------------------------------------------------------------------------------
    def start(self):
        """
        Starts reading aircraft data from CyberAttack
        :return:
        """

        M_LOG.info(">> CyberAttackFeed.start")
        M_LOG.info("<< CyberAttackFeed.start")

        return

    # -------------------------------------------------------------------------------------------------
    def process_message(self, f_dct_aircraft=None, f_s_icao24_fake=None, f_s_callsign=None):
        """
        Processes the message from the Cyber Attack.

        :param fdict_aircraft: the information from the fake aircraft
        :return: None:
        """
        ls_distance = range(10,65,5)

        # SSR
        self.__s_ssr = "0000"

        # SPI
        self.__b_spi = False

        # Altitude (meters)
        self.__f_altitude = f_dct_aircraft[ldefs.ALTITUDE]

        # Latitude (degrees)
        self.__f_latitude = f_dct_aircraft[ldefs.LATITUDE]

        # Longitude (degrees)
        self.__f_longitude = f_dct_aircraft[ldefs.LONGITUDE]

        # Ground speed (m/s)
        self.__f_ground_speed = f_dct_aircraft[ldefs.GROUND_SPEED]

        # Vertical rate (m/s)
        self.__f_vertical_rate = f_dct_aircraft[ldefs.VERTICAL_RATE]

        # Heading (degrees)
        self.__f_heading = random.randrange(0.0,360.0)

        li_chosen_distance = random.choice(ls_distance)
        lf_heading_radians = math.radians(self.__f_heading)

        self.__f_longitude += ( li_chosen_distance * math.sin(lf_heading_radians))
        self.__f_latitude += ( li_chosen_distance * math.cos(lf_heading_radians))

        # Callsign
        self.__s_callsign = f_s_callsign

        # Aircraft performance type
        self.__s_aircraft_type = None

        # Timestamp
        #self.old_timestamp = self.timestamp
        self.__l_timestamp = 0

        # ICAO 24 bit code
        self.__s_icao24 = f_s_icao24_fake


# < the end >--------------------------------------------------------------------------------------
