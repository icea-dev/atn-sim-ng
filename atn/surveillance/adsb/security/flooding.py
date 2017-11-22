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

revision 0.1  2017/nov  matiasims
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
# < imports >--------------------------------------------------------------------------------------
import atn.surveillance.adsb.security.glb_defs as ldefs
import logging
import random
import time

# python library
from .abstract_attack import AbstractAttack
from ..adsb_out import AdsbOut
from ..feeds.cyber_attack_feed import CyberAttackFeed

M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)

__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/11"


class Flooding(AbstractAttack):
    """

    """


    # ---------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Construtor
        """
        M_LOG.info(">> Flooding.__init__")

        self.__i_amount_fake_aircraft = 10
        self.__i_total_fake_aircraft = 100

        M_LOG.info("<< Flooding.__init__")


    # ---------------------------------------------------------------------------------------------
    def spy(self, fdct_aircraft_table=None, flst_icao24_fake=None):
        """

        :param fdct_aircraft_table:
        :param flst_icao24_fake:
        :return:
        """
        M_LOG.info(">> Flooding.spy")

        if self.can_attack() is False:
            M_LOG.info("!! Waiting to start the attack")
            return

        # Auto selecting vitim
        llst_icao24 = fdct_aircraft_table.keys()

        if len(llst_icao24) > 0:
            ls_spoof_icao24 = random.choice(llst_icao24)
            ldct_aircraft = fdct_aircraft_table[ls_spoof_icao24]

            logging.info("!! Victim:  %s (%s)" % (self.__dct_aircraft[ldefs.CALLSIGN], ls_spoof_icao24))

            for x in range(self.__i_amount_fake_aircraft):
                lo_cyberAttackFeed = CyberAttackFeed()
                lf_lat, lf_lng, lf_alt = self.get_position()
                lo_cyberAttackFeed.set_position(lf_lat, lf_lng, lf_alt)
                ls_fake_icao24 = self.get_new_icao24()
                ls_callsign = self.get_new_callsign()
                lo_cyberAttackFeed.process_message(ldct_aircraft, ls_fake_icao24, ls_callsign)

                lo_adsbOut = AdsbOut(nodename="cyber_attack",feed=lo_cyberAttackFeed)
                lo_adsbOut.start()

                M_LOG.info("!! Creating new thread for aircraft !")

                time.sleep(1)

        self.restart()

        M_LOG.info("<< Flooding.spy")
        return


    # ---------------------------------------------------------------------------------------------
    def start(self, fi_time_to_attack, fi_interval_to_attack):
        """

        :param fi_time_to_attack:
        :param fi_interval_to_attack:
        :return:
        """
        M_LOG.info(">> Flooding.start")

        super(Flooding, self).start(fi_time_to_attack, fi_interval_to_attack)

        M_LOG.info("<< Flooding.start")


    # ---------------------------------------------------------------------------------------------
    def __str__(self):
        """
        Returns the object information as a string.
        :return:
        """
        return "CyberAttack::Flooding"


# < the end >--------------------------------------------------------------------------------------
