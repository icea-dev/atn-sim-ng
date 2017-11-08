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
from .abstract_attack import AbstractAttack


class Flooding(AbstractAttack):
    """

    """


    def __init__(self):
        """
        Construtor
        """
        self.__l_icao24 = []
        self.__d_icao24_table = {}
        self.__l_icao24_flooded = []


    def spy(self, fo_adsbOut):
        """

        :param fo_adsbOut:
        :return:
        """
        raise NotImplementedError()


    def calculateKinematics(self):
        """

        :return:
        """
        raise NotImplementedError()

# < the end >--------------------------------------------------------------------------------------
