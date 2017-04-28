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
import netifaces as ni
import socket
import threading

from .adsb_feed import AdsbFeed


class CorePtracksFeed(AdsbFeed):
    """
    Class that provides information for ADS-B Out transponders.
    Receives the information from the aircraft of the track generator (ptracks).
    The aircraft information is read through the CORE control network.
    """

    log_file = "core_ptracks_feed.log"
    log_level = logging.DEBUG

    # Interface da rede de controle do CORE
    ctrl_net_iface = "ctrl0"
    ctrl_net_port = 4038

    # 'CA' Capability Field : 5 - Signifies Level 2 or above transponder, and the ability to set "CA"
    # code 7, and airbone
    CA = 5

    # ADS-B Emitter Category used to identify particular aircraft
    # 0 : No ADS-B Emitter Category Information
    EMITTER_CATEGORY = 0

    FT_TO_M = 0.3048
    KT_TO_MPS = 0.51444444444

    # -------------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Constructor
        """

        # Logging
        logging.basicConfig(filename=self.log_file, level=self.log_level, filemode='w',
                            format='%(asctime)s %(levelname)s: %(message)s')

        self.logger = logging.getLogger("core_ptracks_feed")

        # Locking
        self.data_lock = threading.Lock()

        # Init attributes aircraft data
        self.ssr = None
        self.spi = False
        self.atitude = 0
        self.latitude = 0
        self.longitude = 0
        self.ground_speed = 0
        self.vertical_rate = 0
        self.heading = 0
        self.callsign = None
        self.aircraft_type = None
        self.timestamp = 0
        self.old_timestamp = 0
        self.icao24 = None

        # IP address of incoming messages
        self.ctrl_net_host = ni.ifaddresses(self.ctrl_net_iface)[2][0]['addr']
        logging.debug("Control Network host %s port %s" % (self.ctrl_net_host, self.ctrl_net_port))


    # -------------------------------------------------------------------------------------------------
    def get_ssr(self):
        """
         Returns the current squawk code of the aircraft.

        :return: string
        """
        self.data_lock.acquire()
        ssr = self.ssr
        self.data_lock.release()

        return ssr


    # -------------------------------------------------------------------------------------------------
    def get_spi(self):
        """
        Returns the status of Special Pulse Identification (SPI) of aircraft
        :return: bool, True SPI is activated otherwise False
        """
        self.data_lock.acquire()
        spi = self.spi
        self.data_lock.release()

        return spi


    # -------------------------------------------------------------------------------------------------
    def get_callsign(self):
        """
        Returns the callsign of aircraft
        :return: string
        """
        self.data_lock.acquire()
        callsign = self.callsign
        self.data_lock.release()

        return callsign


    # -------------------------------------------------------------------------------------------------
    def get_position(self):
        """
        Returns latitude, longitude and altitude of aircraft
        :return: (latitude in degrees, longitude in degress, altitude in meters)
        """
        self.data_lock.acquire()
        latitude = self.latitude
        longitude = self.longitude
        altitude = self.altitude
        self.data_lock.release()

        return latitude, longitude, altitude


    # -------------------------------------------------------------------------------------------------
    def get_velocity(self):
        """
        Returns heading, vertical rate and ground speed of aircraft
        :return: (heading in degrees, vertical rate in meters per second, ground speed in meters per second)
        """
        self.data_lock.acquire()
        heading = self.heading
        vertical_rate = self.vertical_rate
        ground_speed = self.ground_speed
        self.data_lock.release()

        return heading, vertical_rate, ground_speed


    # -------------------------------------------------------------------------------------------------
    def get_icao24(self):
        """
        Returns the ICAO 24 bit code identifier of aircraft
        :return: ICAO 24 bit code
        """
        self.data_lock.acquire()
        icao24 = self.icao24
        self.data_lock.release()

        return icao24


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
        self.data_lock.acquire()
        ret_code = ( self.old_timestamp < self.timestamp )
        self.data_lock.release()

        return ret_code


    # -------------------------------------------------------------------------------------------------
    def start(self):
        """
        Starts reading aircraft data from track generator (ptracks)
        :return:
        """
        logging.info("Starting core ptracks feed ...")
        t1 = threading.Thread(target=self.ptracks_read, args=())
        t1.start()


    # -------------------------------------------------------------------------------------------------
    def process_message(self, message):
        """
        Processes the message from the track generator.
        Splits the message and store the aircraft information.

        :param message: the track generator message
        :return:
        """
        # ex: #1#7003#-1#4656.1#-16.48614#-47.947058#210.8#9.7#353.9#TAM6543#B737#21653.3006492#icao24

        # Node number
        msg_num = int(message[0])

        # SSR
        self.ssr = message[1]

        # SPI
        msg_spi = int(message[2])

        # if spi > 0, SPI=ON, otherwise SPI=OFF
        if msg_spi > 1:
            self.spi = True
        else:
            self.spi = False

        # Altitude (feet)
        self.altitude = float(message[3])
        self.altitude = self.altitude * self.FT_TO_M

        # Latitude (degrees)
        self.latitude = float(message[4])

        # Longitude (degrees)
        self.longitude = float(message[5])

        # Ground speed (knots)
        self.ground_speed = float(message[6])
        self.ground_speed = self.ground_speed * self.KT_TO_MPS

        # Vertical rate (m/s)
        self.vertical_rate = float(message[7])

        # Heading (degrees)
        self.heading = float(message[8])

        # Callsign
        self.callsign = message[9]

        # Aircraft performance type
        self.aircraft_type = message[10]

        # Timestamp
        self.old_timestamp = self.timestamp
        self.timestamp = float(message[11])

        # ICAO 24 bit code
        self.icao24 = message[12]


    # -------------------------------------------------------------------------------------------------
    def ptracks_read(self):
        """
        Thread for reading the track generator (ptracks) data
        :return:
        """
        logging.info ("Starting ptracks read")
        # Create a socket for receiving ptracks messages
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, 25, self.ctrl_net_iface+'\0')

        sock.bind((self.ctrl_net_host, self.ctrl_net_port))

        logging.info("Listen on IP %s port %s " % (self.ctrl_net_host, str(self.ctrl_net_port)))

        while True:
            # Buffer size is 1024 bytes
            data, addr = sock.recvfrom(1024)
            message = data.split("#")

            logging.info("Data received [%s]" % data)
            self.data_lock.acquire()
            self.process_message(message)
            self.data_lock.release()


# < the end >--------------------------------------------------------------------------------------
