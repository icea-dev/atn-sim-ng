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
__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/10"

# < imports >--------------------------------------------------------------------------------------

# python library
import logging
import random
import threading
import time
import atn.surveillance.adsb.security.glb_defs as ldefs

from .abstract_attack import AbstractAttack

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)


class EvilTwin(AbstractAttack):
    """
    Classe responsável pelo ataque de spoofing que altera a LATITUDE e ENDEREÇO ICAO da
    aeronave. As outras informações são exatamente as mesmas.
    """
    # ---------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Construtor
        """
        M_LOG.info(">> EvilTwin.__init__")

        # endereço icao24 da vítima
        self.__s_spoof_icao24 = None

        # endereço icao24 fake
        self.__s_fake_icao24 = None

        # dicionário com as infromações da aeronave vítima
        self.__dct_aircraft = {}

        # timeout de espera de mensagens ADS-B da vítima selecionada em segundos
        self.__time_out = 20

        #
        self.__s_last_position_msg = "ODD"

        # tempo para iniciar o ataque
        M_LOG.info("<< EvilTwin.__init__")


    # ---------------------------------------------------------------------------------------------
    def __airborne_pos_threaded(self):
        """

        :return:
        """
        time.sleep(random.randint(0, 5))

        while True:

            if (ldefs.LATITUDE and ldefs.LONGITUDE and ldefs.LAST_TYPE and ldefs.ALTITUDE) in self.__dct_aircraft:
                li_sv = 0

                lf_latitude = self.__dct_aircraft[ldefs.LATITUDE]
                lf_latitude += 0.05
                lf_longitude = self.__dct_aircraft[ldefs.LONGITUDE]
                lf_altitude = self.__dct_aircraft[ldefs.ALTITUDE]

                # Hex
                ls_msg, ls_last_msg = self.encode_airborne_position(self.__s_fake_icao24, li_sv, lf_latitude,
                                                       lf_longitude, lf_altitude, self.__s_last_position_msg)
                if ls_msg is not None:
                    self.__s_last_position_msg = ls_last_msg
                    self.replay(ls_msg)

                # mensagens de meio em meio segundo.
                time.sleep(0.5)


    # ---------------------------------------------------------------------------------------------
    def __airborne_vel_threaded(self):
        """

        :return:
        """
        time.sleep(random.randint(0,5))

        while True:
            if  (ldefs.HEADING and ldefs.VERTICAL_RATE and ldefs.GROUND_SPEED) in self.__dct_aircraft:
                lf_heading = self.__dct_aircraft[ldefs.HEADING]
                lf_vertical_rate = self.__dct_aircraft[ldefs.VERTICAL_RATE]
                lf_ground_speed = self.__dct_aircraft[ldefs.GROUND_SPEED]

                # Hex
                ls_msg = self.encode_airbone_velocity(self.__s_fake_icao24, lf_heading, lf_vertical_rate, lf_ground_speed)
                self.replay(ls_msg)

                # mensagens de meio em meio segundo.
                time.sleep(0.5)


    # ---------------------------------------------------------------------------------------------
    def __aircraft_id_threaded(self):
        """

        :return:
        """
        time.sleep(random.randint(0,5))

        while True:
            if ldefs.CALLSIGN in self.__dct_aircraft:
                ls_callsing = self.__dct_aircraft[ldefs.CALLSIGN]

                # Hex
                ls_msg = self.encode_aircraft_identification(ls_callsing, self.__s_fake_icao24)
                self.replay(ls_msg)

                # mensagens de 5 em 5 segundos
                time.sleep(5.0)


    # ---------------------------------------------------------------------------------------------
    def spy(self, fdct_aircraft_table=None, flst_icao24_fake=None):
        """
        Escuta da mensagens ADS-B.

        :param fo_adsbOut: o transmissor da mensagem ADS-B
        :param fdct_aircraft_table: dicionário com as informações das aeronaves espionadas.
        :param flst_icao24_fake: lista com o endereços ICAO24 fake.
        :return: None.
        """
        M_LOG.info(">> EvilTwin.spy")

        if self.can_attack() is False:
            M_LOG.info("!! Waiting to start the attack")
            return

        # Auto selecting vitim
        if self.__s_spoof_icao24 is None:

            #lst_icao24 = fdct_aircraft_table.keys()
            llst_icao24 = []

            for ls_icao24 in fdct_aircraft_table:
                ldct_aircraft_data = fdct_aircraft_table[ls_icao24]
                if (ldefs.UNLAWFUL_INTERFERENCE in ldct_aircraft_data):
                    if ldct_aircraft_data[ldefs.UNLAWFUL_INTERFERENCE] is False:
                        llst_icao24.append(ls_icao24)

            M_LOG.debug("!! Lista de endereco ICAO24 simulados %s" % llst_icao24)

            if len(llst_icao24) > 0:
                self.__s_spoof_icao24 = random.choice(llst_icao24)
                self.__s_fake_icao24 = self.get_new_icao24()
                flst_icao24_fake.append(self.__s_fake_icao24)
                fdct_aircraft_table[self.__s_spoof_icao24][ldefs.UNLAWFUL_INTERFERENCE] = True

        else:
            self.__dct_aircraft = fdct_aircraft_table[self.__s_spoof_icao24]

            logging.info("!! Victim:  %s (%s)" % (self.__dct_aircraft[ldefs.CALLSIGN], self.__s_spoof_icao24))
            logging.info("!! Spoofer: %s (%s)" % (self.__dct_aircraft[ldefs.CALLSIGN], self.__s_fake_icao24))

            # if not received a message in 20 seconds, looking for another one
            if (ldefs.LAST_UPDATE in self.__dct_aircraft):
                if (time.time() - self.__dct_aircraft[ldefs.LAST_UPDATE]) > self.__time_out:
                    logging.info("!! Aircraft lost")
                    if self.__s_fake_icao24 in flst_icao24_fake:
                        flst_icao24_fake.remove(self.__s_fake_icao24)

                    self.__s_spoof_icao24 = None
                    self.__s_fake_icao24 = None
                    self.__dct_aircraft = {}

                    # waiting for new attack
                    self.restart()


        M_LOG.info("<< EvilTwin.spy")
        return


    # ---------------------------------------------------------------------------------------------
    def start(self, fi_time_to_attack, fi_interval_to_attack):
        """

        :param fi_interval_to_attack:
        :return:
        """
        super(EvilTwin, self).start(fi_time_to_attack, fi_interval_to_attack)

        # iniciar as threads aqui!!!!
        t1 = threading.Thread(target=self.__airborne_pos_threaded, args=())
        t2 = threading.Thread(target=self.__airborne_vel_threaded, args=())
        t3 = threading.Thread(target=self.__aircraft_id_threaded, args=())

        # Start broadcasting
        t1.start()  # Airborne position
        t2.start()  # Airborne velocity
        t3.start()  # Aircraft identification

        return


    # ---------------------------------------------------------------------------------------------
    def __str__(self):
        """Returns the object information as a string.

        Returns:
            string:

        """
        return "CyberAttack::EvilTwin"


# < the end >--------------------------------------------------------------------------------------
        # "Surveillance Status"
        #
        # Encode information from the aircraft's Mode-A transponder code as follows:
        #
        # 0 : No condition information
        # 1 : Permanent alert condition (emergency)
        # 2 : Temporary alert condition (change in Mode A Identity Code other than emergency condition)
        # 3 : Special position identification (SPI) condition
        #
        # Note: When not implemented in a Mode-S Transponder-Based system, the ADS-B function shall set
        # the "Surveillance Status" subfield to ZERO.
        #sv = 0

        # get SSR and SPI
        #ssr = self.adsbfeed.get_ssr()

        #spi = self.adsbfeed.get_spi()

        # implementation of SSR
        #if (ssr == self.HIJ) or (ssr == self.COM) or (ssr == self.EMG):
        #    sv = 1

        # implementation of SPI
        #if spi:
        #    sv = 3
