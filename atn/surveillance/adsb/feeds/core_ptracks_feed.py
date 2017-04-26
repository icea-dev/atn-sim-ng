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

revision 0.1  2017/April  Matias
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/04"

# < imports >--------------------------------------------------------------------------------------
import logging
import threading

from .adsb_feed import AdsbFeed

class CorePtracksFeed(AdsbFeed):
    """

    """
    log_file = "core_ptracks_feed.log"
    log_level = logging.DEBUG

    # 'CA' Capability Field : 5 - Signifies Level 2 or above transponder, and the ability to set "CA"
    # code 7, and airbone
    CA = 5

    # ADS-B Emitter Category used to identify particular aircraft
    # 0 : No ADS-B Emitter Category Information
    EMITTER_CATEGORY = 0


    # -------------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Constructor
        """

        # Logging
        logging.basicConfig(filename=self.log_file, level=self.log_level, filemode='w',
                            format='%(asctime)s %(levelname)s: %(message)s')

        self.logger = logging.getLogger("core_ptracks_feed")

        # Init attributes aircraft data
        self.ssr           = None
        self.spi           = False
        self.atitude       = 0
        self.latitude      = 0
        self.longitude     = 0
        self.ground_speed  = 0
        self.vertical_rate = 0
        self.heading       = 0
        self.callsign      = None
        self.aircraft_type = None
        self.timestamp     = 0
        self.icao24        = None


    # -------------------------------------------------------------------------------------------------
    def get_ssr(self):
        """
         Returns the current squawk code of the aircraft.

        :return: string
        """
        return self.ssr


    # -------------------------------------------------------------------------------------------------
    def get_spi(self):
        """
        Returns the status of Special Pulse Identification (SPI) of aircraft
        :return: bool, True SPI is activated otherwise False
        """
        return self.spi


    # -------------------------------------------------------------------------------------------------
    def get_callsign(self):
        """
        Returns the callsign of aircraft
        :return: string
        """
        return self.callsign


    # -------------------------------------------------------------------------------------------------
    def get_position(self):
        """
        Returns latitude, longitude and altitude of aircraft
        :return: (latitude in degrees, longitude in degress, altitude in meters)
        """
        return self.latitude, self.longitude, self.altitude


    # -------------------------------------------------------------------------------------------------
    def get_velocity(self):
        """
        Returns heading, vertical rate and ground speed of aircraft
        :return: (heading in degrees, vertical rate in meters per second, ground speed in meters per second)
        """
        return self.heading, self.vertical_rate, self.ground_speed


    # -------------------------------------------------------------------------------------------------
    def get_icao24(self):
        """
        Returns the ICAO 24 bit code identifier of aircraft
        :return: ICAO 24 bit code
        """
        return self.icao24


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
        if self.tracksrv_perftype is None:
            return False
        if self.get_callsign() is None:
            return False
        return True

    # -------------------------------------------------------------------------------------------------
    def start(self):
        """
        Starts reading aircraft data from CORE
        :return:
        """
        t1 = threading.Thread(target=self.core_read, args=())
        t1.start()


    # -------------------------------------------------------------------------------------------------
    def core_read(self):
        pass


'''
msg_num = int(message[2])  # node id
msg_ssr = message[3]
msg_spi = int(message[4])  # if spi > 0, SPI=ON, otherwise SPI=OFF
msg_alt = float(message[5])  # altitude (feet)
msg_lat = float(message[6])  # latitude (degrees)
msg_lon = float(message[7])  # longitude (degrees)
msg_vel = float(message[8])  # velocity (knots)
msg_cbr = float(message[9])  # climb rate (m/s)
msg_azm = float(message[10])  # azimuth (degrees)
msg_csg = message[11]  # callsign
msg_per = message[12]  # aircraft performance type
msg_tim = float(message[13])  # timestamp (see "hora de inicio")
'''

# < the end >--------------------------------------------------------------------------------------
