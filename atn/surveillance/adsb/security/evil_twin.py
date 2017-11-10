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

from .abstract_attack import AbstractAttack

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)

__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/10"


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
        M_LOG.info("<< EvilTwin.__init__")


    # ---------------------------------------------------------------------------------------------
    def spy(self, fo_adsbOut=None, fdict_aircraft_table=None, flst_icao24_fake=None):
        """
        Escuta da mensagens ADS-B.

        :param fo_adsbOut: o transmissor da mensagem ADS-B
        :param fdict_aircraft_table: dicionário com as informações das aeronaves espionadas.
        :param flst_icao24_fake: lista com o endereços ICAO24 fake.
        :return: None.
        """
        M_LOG.info(">> EvilTwin.spy")
        M_LOG.info("<< EvilTwin.spy")


    # ---------------------------------------------------------------------------------------------
    def calculateKinematics(self):
        """

        :return:
        """
        raise NotImplementedError()


# < the end >--------------------------------------------------------------------------------------
