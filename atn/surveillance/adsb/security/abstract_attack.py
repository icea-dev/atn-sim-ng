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

revision 0.1  2017/oct  matiasims
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
# < imports >--------------------------------------------------------------------------------------

# python library
import binascii
import logging
import math
import os

from abc import ABCMeta, abstractmethod
from time import time

import atn.surveillance.adsb.adsb_utils as AdsbUtils
import atn.surveillance.adsb.security.glb_defs as ldefs

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)

__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/10"


class AbstractAttack(object):
    """
    Declara uma interface para um tipo de objeto de ataque.

    """
    __metaclass__ = ABCMeta

    # A posição do atacante no CORE
    __f_altitude = None
    __f_latitude = None
    __f_longitude = None

    __i_time_to_attack = 0
    __i_interval_to_attack = 0

    # tempo de início da simulação
    __tt_start = 0

    #
    __b_attack = False


    # ---------------------------------------------------------------------------------------------
    @abstractmethod
    def calculate_kinematics(self):
        """
        Calculos cinemáticos da aeronave vítima.
        :return:
        """
        raise NotImplementedError()


    # ---------------------------------------------------------------------------------------------
    def __calculate_velocity(self, ff_radians, fi_direction, ff_ground_speed):
        """
        Calculate the direction and ground speed component.

        :param ff_radians (float): the heading of airborne in radians.
        :param fi_direction (int): indicate the direction of velocity. 0 or 1.
        :param ff_ground_speed (float): the ground speed of airbone in knots (kt).
        :return: Returns the direction of velocity vector and velocity.
        """
        li_direction_velocity = 0

        # Check the direction of the ground speed module
        if fi_direction == ldefs.EW_DIRECTION:
            lf_velocity = math.sin(ff_radians) * ff_ground_speed
            # Calculate the e/w direction
            if ff_radians > ldefs.RAD_180 and ff_radians <= ldefs.RAD_360:
                li_direction_velocity = 1
        elif fi_direction == ldefs.NS_DIRECTION:
            lf_velocity = math.cos(ff_radians) * ff_ground_speed
            # Calculate the n/s direction
            if ff_radians > ldefs.RAD_90 and ff_radians <= ldefs.RAD_270:
                li_direction_velocity = 1
        else:
            return None

        # Velocity to be sent
        lf_velocity_module = int(round(abs(math.fabs(lf_velocity) + 1.0)))

        return li_direction_velocity, lf_velocity_module


    # ---------------------------------------------------------------------------------------------
    def __calculate_vertical_rate(self, ff_vertical_rate):
        """
        Calculate the direction of the vertical rate and your module.

        :param ff_vertical_rate (float): the vertical rate in ft/min.
        :return: the direction of the vertical rate (0: UP, 1 :DOWN) and vertical rate module.
        """
        sign = ldefs.VERTICAL_RATE_UP
        if ff_vertical_rate < 0.0:
            sign = ldefs.VERTICAL_RATE_DOWN

        return sign, int(round(abs(math.fabs(ff_vertical_rate))))


    # ---------------------------------------------------------------------------------------------
    def can_attack(self):
        """

        :return:
        """
        if self.__b_attack is False:
            ltt_end = time()

            ltt_time_taken = ( ltt_end - self.__tt_start ) / 60

            if self.__i_time_to_attack <= ltt_time_taken:
                self.__b_attack = True

        return self.__b_attack


    # ---------------------------------------------------------------------------------------------
    def encode_airborne_position(self, fs_icao24, fi_sv, ff_latitude, ff_longitude, ff_altitude, fs_last_position_msg):
        """

        :param fs_icao24:
        :param fi_sv:
        :param ff_latitude:
        :param ff_longitude:
        :param ff_altitude:
        :param fs_last_position_msg:
        :return:
        """

        '''Altitude encoding'''

        # Encode altitude
        if ff_altitude < 50175:  # (2^11 -1)*25 - 1000 : 25 feet increment
            ls_qbit = "1"
            fi_enc_alt= int(round((ff_altitude+1000)/25.0))
        else:  # 100 feet increment
            ls_qbit = "0"
            fi_enc_alt = int(round((ff_altitude+1000)/100.0))

        ls_enc_alt_bin = bin(fi_enc_alt)[2:].zfill(11)                   # binary string:
        ls_enc_alt     = int(ls_enc_alt_bin[0:7]+ls_qbit+ls_enc_alt_bin[7:11], 2)  # Inserting qbit

        '''Lat/Lon CPR Encoding'''
        ff_even_lat = ff_latitude
        ff_even_lon = ff_longitude
        ff_odd_lat = ff_even_lat
        ff_odd_lon = min(ff_even_lon, 180)

        (l_even_enc_lat, l_even_enc_lon) = AdsbUtils.cpr_encode(ff_even_lat, ff_even_lon, False, False)
        (l_odd_enc_lat, l_odd_enc_lon)   = AdsbUtils.cpr_encode(ff_odd_lat, ff_odd_lon, True, False)

        msg_even = AdsbUtils.encode_airborne_position(ldefs.CA, fs_icao24, l_even_enc_lat, l_even_enc_lon, fi_sv, ldefs.NIC_SB, ls_enc_alt, ldefs.T_FLAG, 0)
        msg_odd  = AdsbUtils.encode_airborne_position(ldefs.CA, fs_icao24, l_odd_enc_lat, l_odd_enc_lon, fi_sv, ldefs.NIC_SB, ls_enc_alt, ldefs.T_FLAG, 1)

        # Alternate through even or odd messages
        if fs_last_position_msg == ldefs.ODD_MSG:
            # Send even msg
            return hex(int(msg_even, 2)).rstrip("L").lstrip("0x")
        else:
            # Send odd msg
            return hex(int(msg_odd, 2)).rstrip("L").lstrip("0x")


    # ---------------------------------------------------------------------------------------------
    def encode_airbone_velocity(self, fs_icao24, ff_heading, ff_vertical_rate, ff_ground_speed):
        """
        This method encodes the ADS-B Airbone Velocity Message and sends it to
        the network. There are two different types of message for velocities,
        determined by 3-bit subtype in the message. Only subtype 1 and 2,
        surface velocity (ground speed) is reported.

        :param fs_icao24: icao address of aircraft
        :param ff_heading: heading of aircraft
        :param ff_vertical_rate:  vertical rate of aircraft
        :param ff_ground_speed:  ground speed of aircarft
        :return: A string with ADS-B Airbone Velocity Message encodes in hexadecimal.
        """

        lf_heading_radians = ff_heading * math.pi / 180.0

        # Intent Change Flag = 0, No Change in Intent
        li_ic_flag = 0

        # Reserved-A ZEROS
        li_reserved_a = 0

        # NACv (Navigate Accuracy Category for Velocity), determining NACv
        # based on position source declared horizontal velocity Error
        # 0 : Unknown or >= 10 m/s
        # 1 : < 10 m/s
        # 2 : < 3 m/s
        # 3 : < 1 m/s
        # 4 : < 0.3 m/s
        li_nacv = 0

        # East/West Velocity in knots
        # East/West Direction Bit: indicate the direction of the East/West
        # Velocity Vector
        # 0 : flying West to East
        # 1 : flying East to West
        (li_ew_dir, li_ewv) = self.__calculate_velocity(lf_heading_radians,
                                                ldefs.EW_DIRECTION, ff_ground_speed)

        # North/South Velocity in knots
        # North/South Direction Bit: indicate the direction of the North/South
        # Velocity Error
        # 0 : flying South to North
        # 1 : flying North to South
        (li_ns_dir, li_nsv) = self.__calculate_velocity(lf_heading_radians,
                                                ldefs.NS_DIRECTION, ff_ground_speed)

        # Vertical Rate Source: indicate the source of Vertical Rate information
        # as specified:
        # 0 : Vertical Rate information from Geometric Source (GNSS or INS)
        # 1 : Vertical Rate information from Barometric Source
        li_vrate_src = ldefs.BAROMETRIC_SOURCE

        # Vertical rate Sign: indicate the direction of the Vertical rate as
        # specified:
        # 0 : Up
        # 1 : Down
        # If vrate < 0 the aircraift is going DOWN otherwise is going UP
        (li_vertical_rate_sign, li_vertical_rate) = self.__calculate_vertical_rate(
                                                                ff_vertical_rate)

        # Reserved-B ZEROS
        li_reserved_b = 0

        # Difference From barometric Altitude Sign Bit: used to indicate the
        # direction of the GNSS Altitude Source data as specified:
        # 0 : Geometric (GNSS or INS) Altitude Source data is greater than
        #     (above) Barometric
        # 1 : Geometric (GNSS or INS) Altitude Source data is less than
        #     (below) Barometric
        li_h_sign = 0

        # Difference From Barometric Altitude: is used to report the difference
        # between Geometric (GNSS or INS) Altitude Source data and Barometric
        # Altitude when both types of Altitude Data are available and valid
        # 0 : No GNSS Altitude Source data Difference information available
        li_h_diff = 0

        # Supersonic Version of the Airbone Velocity Message
        # Subtype = 2 shall be used if either the East/West Velocity or the
        # North/South Velocity exceeds 1022 knots. A switch to the normal
        # velocity message (Subtype 1) shall be made if both the East/West
        # and the North/South Velocities drop below 1000 knots
        li_es_subtype = self.__get_msg_subtype(li_ewv, li_nsv)

        if li_es_subtype == ldefs.MSG_SUBTYPE_2:
            li_ewv = int(round(abs(li_ewv / 2)))
            li_nsv = int(round(abs(li_nsv / 2)))

        # Encodes the ADS-B Airbone Velocity Message
        msg = AdsbUtils.encode_airborne_velocity(ldefs.CA,
            fs_icao24, li_es_subtype, li_ic_flag, li_reserved_a, li_nacv, li_ew_dir,
            li_ewv, li_ns_dir, li_nsv, li_vrate_src, li_vertical_rate_sign, li_vertical_rate,
            li_reserved_b, li_h_sign, li_h_diff)

        return hex(int(msg, 2)).rstrip("L").lstrip("0x")


    # ---------------------------------------------------------------------------------------------
    def encode_aircraft_identification(self, fs_callsign, fs_icao24):
        """
        Codifica a mensagem ADS-B de identificação da aeronave

        :param fs_callsign: a identificação da aeronave
        :param fs_icao24: o endereço icao da aeronave
        :return: mensagem ADS-B de identificação da aeronave.
        """

        ls_msg = AdsbUtils.encode_aircraft_id(ldefs.CA, fs_icao24, ldefs.AIR_TYPE, fs_callsign)
        return hex(int(ls_msg, 2)).rstrip("L").lstrip("0x")


    # ---------------------------------------------------------------------------------------------
    def __get_msg_subtype(self, fi_ew_velocity, fi_ns_velocity):
        """
        Determines the subtype of ADS-B velocity message.

        :param fi_ew_velocity (int): the E/W velocity vector.
        :param fi_ns_velocity (int): the N/S velocity vector.
        :return: the subtype of ADS-B velocity message.
        """
        if (fi_ew_velocity - 1) >= 1022 or (fi_ns_velocity - 1) >= 1022:
            return ldefs.MSG_SUBTYPE_2
        else:
            return ldefs.MSG_SUBTYPE_1


    # ---------------------------------------------------------------------------------------------
    def set_position(self, ff_latitude, ff_longitude, ff_altitude):
        """

        :param ff_latitude:
        :param ff_longitude:
        :param ff_altitude:
        :return:
        """
        self.__f_altitude = ff_altitude
        self.__f_latitude = ff_latitude
        self.__f_longitude = ff_longitude


    # ---------------------------------------------------------------------------------------------
    @abstractmethod
    def spy(self, fo_adsbOut=None, fdict_aircraft_table=None, flst_icao24_fake=None):
        """
        Escuta da mensagens ADS-B.

        :param fo_adsbOut: o transmissor da mensagem ADS-B
        :param fdict_aircraft_table: dicionário com as informações das aeronaves espionadas.
        :param flst_icao24_fake: lista com o endereços ICAO24 fake.
        :return: None.
        """
        raise NotImplementedError()


    # ---------------------------------------------------------------------------------------------
    def start(self, fi_time_to_attack, fi_interval_to_attack):
        """
        Obtém o tempo em que se iniciou a simulação.

        :return: None
        """
        M_LOG.info (">> AbstractAttack.start")

        self.__i_time_to_attack = fi_time_to_attack
        self.__i_interval_to_attack = fi_interval_to_attack

        self.__tt_start = time()

        M_LOG.info ("<< AbstractAttack.start")


    # ---------------------------------------------------------------------------------------------
    def replay(self, fs_message, fo_adsbOut, fi_delay):
        """
        Retransmite a mensagem ADS-B
        :return:
        """
        raise NotImplementedError()


    # ---------------------------------------------------------------------------------------------
    def get_new_icao24(self):
        """
        Retorna um novo endereço ICAO
        :return:
        """
        return binascii.b2a_hex(os.urandom(3))

# < the end >--------------------------------------------------------------------------------------
