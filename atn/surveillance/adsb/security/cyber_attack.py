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
import logging
import multiprocessing
import sys
import time

from .factory_attack import FactoryAttack

from ..adsb_in import AdsbIn
from ..adsb_out import AdsbOut
from ..feeds.adsb_feed import AdsbFeed

import atn.surveillance.adsb.decoder as AdsbDecoder
import atn.surveillance.adsb.adsb_utils as AdsbUtils

__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/10"


class CyberAttack(AdsbFeed):
    """

    """
    ODD_FRAME = 1

    ODD_TYPE = 'odd'
    EVEN_TYPE = 'even'

    FT_TO_M = 0.3048
    KT_TO_MPS = 0.514444
    FTPM_TO_MPS = 0.00508

    DELAY = 1.0

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

    # ---------------------------------------------------------------------------------------------
    def __init__(self, fs_argv=None):
        """
        Construtor
        """
        logging.info(">> Constructor : CyberAttack")

        # Verifica se os argumentos da linha de comando foi passado para o construtor
        if fs_argv == None:
            logging.error("!! Não foram passados argumentos na linha de comando!")
            logging.info("<< Constructor : CyberAttack")
            return None

        self.__dct_aircraft_table = {}
        self.__lst_icao24 = []
        self.__lst_icao24_fake = []

        # Recupera os argumentos da linha de comando
        # O identificador do sensor
        li_id = int(sys.argv[1])

        # Coordenadas da posição do ataque cibernético.
        self.__f_latitude = float(sys.argv[2])
        self.__f_longitude = float(sys.argv[3])
        self.__f_altitude = float(sys.argv[4])

        llst_attacks = []

        logging.info("!! Criando os objetos para os ataques cibernéticos.")

        # Tipos de ataques cibernéticos
        if "--spoofing-flasher" in sys.argv:
            llst_attacks.append("Flasher")

        if "--spoofing-evil-twin" in sys.argv:
            llst_attacks.append("EvilTwin")

        if "--spoofing-kinematics" in sys.argv:
            llst_attacks.append("EvilTwinKinemtics")

        if "--spoofing-callsign" in sys.argv:
            llst_attacks.append("EvilTwinCallsign")

        if "--flooding" in sys.argv:
            llst_attacks.append("Flooding")

        # lista de objetos que fazem o ataque cibernético
        self.__lst_cyber_attack = []

        logging.debug("!! Lista de ataques cibernéticos %s" % llst_attacks)

        # cria os ataques
        for ls_attacks in llst_attacks:
            logging.debug ("!! Cyber attack : %s", ls_attacks)
            lo_cyber_attack = FactoryAttack.createCyberAttack(fs_type=ls_attacks)
            assert lo_cyber_attack
            self.__lst_cyber_attack.append(lo_cyber_attack)

        # Cria os objetos para escuta e transmissão de mensagens ADS-B
        logging.info("!! Criar o receptor de mensagens ADS-B (AdsbIn).")
        self.__o_adsbIn = AdsbIn(fi_id= li_id, ff_lat=self.__f_latitude,
                             ff_lng=self.__f_longitude, ff_alt=self.__f_altitude,
                             fv_store_msgs=True)

        logging.info("!! Criar o transmissor de mensagens ADS-B fake (AdsbOut).")
        self.__o_adsbOut = AdsbOut(nodename=None,feed=self)

        logging.info("<< Constructor : CyberAttack")

    # ---------------------------------------------------------------------------------------------
    def __decode_position_message(self, f_dct_aircraft, fs_message):
        """
        Decodifica os dados de posicionamento de uma mensagem ADS-B.

        :param f_dct_aircraft: dicionário com as informações da aeronave.
        :param fs_message: a mensagem ADS-B.
        :return: None.
        """
        # 0 -> Even frame - 1 -> Odd frame
        li_evenOddMsg = int(AdsbDecoder.get_oe_flag(fs_message))

        # Save ADS-B message
        if li_evenOddMsg == self.ODD_FRAME:
            f_dct_aircraft[self.ODD_MSG] = fs_message
            f_dct_aircraft[self.LAST_TYPE] = self.ODD_TYPE
        else:
            f_dct_aircraft[self.EVEN_MSG] = fs_message
            f_dct_aircraft[self.LAST_TYPE] = self.EVEN_TYPE

        # Initialize times
        if f_dct_aircraft[self.LAST_TYPE] == self.EVEN_TYPE:
            li_t0 = 1
            li_t1 = 0
        else:
            li_t0 = 0
            li_t1 = 1

        # Decode position and altitude
        if f_dct_aircraft[self.ODD_MSG] and f_dct_aircraft[self.EVEN_MSG]:
            lf_lat, lf_lng = AdsbDecoder.get_position(f_dct_aircraft[self.ODD_MSG],
                                                      f_dct_aircraft[self.EVEN_MSG],
                                                      li_t0, li_t1)

            if lf_lat and lf_lng:
                f_dct_aircraft[self.LATITUDE] = lf_lat
                f_dct_aircraft[self.LONGITUDE] = lf_lng

            f_dct_aircraft[self.ALTITUDE] = AdsbDecoder.get_alt(fs_message) * self.FT_TO_M

        return


    # ---------------------------------------------------------------------------------------------
    def __decode_velocity_message(self, f_dct_aircraft, fs_message):
        """
        Decodifica os dados de velocidade de uma mensagem ADS-B.

        :param f_dct_aircraft: dicionário com as informações da aeronave.
        :param fs_message: a mensagem ADS-B.
        :return: None.
        """

        (lf_ground_speed, lf_heading, lf_vertical_rate, lf_tag) = AdsbDecoder.get_velocity(fs_message)
        f_dct_aircraft[self.GROUND_SPEED] = lf_ground_speed * self.KT_TO_MPS
        f_dct_aircraft[self.HEADING] = lf_heading
        f_dct_aircraft[self.VERTICAL_RATE] = lf_vertical_rate * self.FTPM_TO_MPS

        return


    # ---------------------------------------------------------------------------------------------
    def __decode_identification_message(self, f_dct_aircraft, fs_message):
        """
        Decodifica a identificação do voo (callsign) de uma mensagem ADS-B.

        :param f_dct_aircraft: dicionário com as informações da aeronave.
        :param fs_message: a mensagem ADS-B.
        :return: None.
        """
        f_dct_aircraft[self.CALLSIGN]= AdsbDecoder.get_callsign(fs_message).replace("_","")

        return


    # ---------------------------------------------------------------------------------------------
    def __eavesdropping(self, fi_icao24, fs_message):
        """
        Faz a espionagem das mensagens ADS-B

        :param message: mensagem ADS-B
        :return:
        """
        logging.info(">> CyberAttack.eavesdropping")

        logging.info("!! ICAO24 %s" % fi_icao24 )
        # Empty message
        if fs_message is None:
            logging.info("<< CyberAttack.eavesdropping: fs_message is None.")
            return

        ldct_aircraft = {}
        ldct_aircraft[self.ODD_MSG] = None
        ldct_aircraft[self.EVEN_MSG] = None

        # New aircraft?
        if self.__dct_aircraft_table.has_key(fi_icao24):
            ldct_aircraft = self.__dct_aircraft_table[fi_icao24]

        # Retrieve type code
        li_type_code = AdsbDecoder.get_tc(fs_message)
        logging.debug("!! Type Code da mensagem %d" % li_type_code)

        # Is it a position message ?
        if li_type_code in range(9,19):
            self.__decode_position_message(ldct_aircraft, fs_message)

        # Is it a velocity message ?
        if li_type_code == 19:
            self.__decode_velocity_message(ldct_aircraft, fs_message)

        # Is it a identification message ?
        if li_type_code in range(1,5):
            self.__decode_identification_message(ldct_aircraft, fs_message)

        # Updates the aircraft information
        self.__dct_aircraft_table[fi_icao24] = ldct_aircraft

        logging.info("<< CyberAttack.eavesdropping")

    # ---------------------------------------------------------------------------------------------
    def __disclaimer(self):
        """

        :return:
        """
        print " DISCLAIMER: This software is for testing and educational"
        print " purposes only. Any other usage for this code is not allowed."
        print " Use at your own risk."
        print
        print " 'With great power comes great responsibility.' - Uncle Ben"


    # ---------------------------------------------------------------------------------------------
    def run(self):
        """
        Executa o cyber ataque.

        :return:
        """
        logging.info (">> CyberAttack.run")

        self.__disclaimer()

        # Receive message ADS-B
        self.__o_adsbIn.run();

        while True:
            logging.info ("!! Retrieve message ADS-B.")
            ls_message = self.__o_adsbIn.retrieve_msg()

            if ls_message is None:
                time.sleep(0.2)
            else:
                logging.debug("!! message ADS-B: %s" % str(ls_message).upper())
                # Retrieve ICAO code
                li_icao24 = AdsbDecoder.get_icao_addr(ls_message)

                # Do not handle fake messages
                if li_icao24 in self.__lst_icao24_fake:
                    continue

                if li_icao24 not in self.__lst_icao24:
                    self.__lst_icao24.append(li_icao24)

                logging.debug("!! List of ICAO 24 %s" % self.__lst_icao24)
                # eavesdropping ads-b messages
                self.__eavesdropping(li_icao24, ls_message)

                logging.debug("!! Table of aircraft %s" % self.__dct_aircraft_table)

                # for all configured cyber attacks...
                for l_attack in self.__lst_cyber_attack:
                    # attack received ADS-B message
                    logging.debug("!! attack ")
                    l_attack.spy(self.__o_adbsOut, self.__dct_aircraft_table, self.__lst_icao24_fake)

        logging.info ("<< CyberAttack.run")

    # ---------------------------------------------------------------------------------------------
    def get_ssr(self):
        """Informs current squawk code of the given aircraft.

        Examples:
            - 7500: Hi-Jacking
            - 7600: Radio Failure
            - 7700: Emergency

        The complete list can be found in http://www.flightradars.eu/lsquawkcodes.html
        """
        raise NotImplementedError()


    # ---------------------------------------------------------------------------------------------
    def get_spi(self):
        """Informs if SPI is activated.
        """
        raise NotImplementedError()


    # ---------------------------------------------------------------------------------------------
    def get_callsign(self):
        """Provides the callsign of the given aircraft.
        """
        raise NotImplementedError()


    # ---------------------------------------------------------------------------------------------
    def get_position(self):
        """
        Returns latitude, longitude and altitude of aircraft
        :return: (latitude in degrees, longitude in degress, altitude in meters)
        """
        return self.__f_latitude, self.__f_longitude, self.__f_altitude


    # ---------------------------------------------------------------------------------------------
    def get_velocity(self):
        """Provides azimuth, climb_rate, and speed in meters per second.
        """
        raise NotImplementedError()


    # ---------------------------------------------------------------------------------------------
    def get_icao24(self):
        raise NotImplementedError()


    # ---------------------------------------------------------------------------------------------
    def get_capabilities(self):
        raise NotImplementedError()


    # ---------------------------------------------------------------------------------------------
    def get_type(self):
        raise NotImplementedError()


    # ---------------------------------------------------------------------------------------------
    def is_track_updated(self):
        raise NotImplementedError()


    # ---------------------------------------------------------------------------------------------
    def start(self):
        return


if "__main__" == __name__:

    # Logging
    logging.basicConfig(filename="cyber_attack.log", level=logging.DEBUG, filemode='w',
                        format='%(asctime)s %(levelname)s: %(message)s')

    # multiprocessing logger
    multiprocessing.log_to_stderr()

    # cria a aplicacao
    l_cyber_attack = CyberAttack(sys.argv)
    assert l_cyber_attack

    # executa a aplicação
    l_cyber_attack.run()

# < the end >--------------------------------------------------------------------------------------
