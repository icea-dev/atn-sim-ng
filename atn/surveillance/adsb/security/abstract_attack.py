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

from abc import ABCMeta, abstractmethod


class AbstractAttack(object):
    """
    Declara uma interface para um tipo de objeto de ataque.

    """
    __metaclass__ = ABCMeta

    # Número máximo de mensagens no buffer de mensagens ADS-B recebidas.
    M_MAX_REC_MSGS = 5000

    # ---------------------------------------------------------------------------------------------
    def __init__(self):
        """

        """

        # A posição do atacante no CORE
        self.__f_altitude = None
        self.__f_latitude = None
        self.__f_longitude = None



    # ---------------------------------------------------------------------------------------------
    @abstractmethod
    def calculateKinematics(self):
        """
        Calculos cinemáticos da aeronave vítima.
        :return:
        """
        raise NotImplementedError()


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
    def store_adsb_message(self, fs_message):
        """
        Armazena as mensagens ADS-B recebidas
        :return:
        """
        # store message
        if (not self.q_rec_msgs.full()):
            # put on queue
            self.q_rec_msgs.put(fs_message)


    # ---------------------------------------------------------------------------------------------
    def replay(self, fs_message, fo_adsbOut, fi_delay):
        """
        Retransmite a mensagem ADS-B
        :return:
        """
        raise NotImplementedError()


# < the end >--------------------------------------------------------------------------------------
