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

revision 0.2  2017/abr  mlabru
remoção MySQL, pep-8

revision 0.1  2016/dec  conte
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.2$"
__author__ = "Milton Abrunhosa"
__date__ = "2017/05"

# < imports >--------------------------------------------------------------------------------------

# python library
import logging

# atn-sim
import atn.geo_utils as geoutils

# < class BSensor >--------------------------------------------------------------------------------

class BSensor(object):
    """
    sensors class
    """
    # ---------------------------------------------------------------------------------------------
    def __init__(self, f_id, ff_lat, ff_lng, ff_alt):
        """
        constructor
        """
        # id
        self.__id = f_id

        # geographic
        self.__f_lat = ff_lat
        self.__f_lng = ff_lng
        self.__f_alt = ff_alt

        # cartesian (x, y, z)
        self.__f_x = 0.
        self.__f_y = 0.
        self.__f_z = 0.

    # ---------------------------------------------------------------------------------------------
    # def latlon2xy(self, lat0, lon0):
    #     return coreutils.calc_distance(lat0, lon0, self.__f_lat, self.__f_lng)

    # ---------------------------------------------------------------------------------------------
    def update(self, ff_latR=None, ff_lngR=None, ff_altR=None):

        # reference valid ?
        if (ff_latR is not None) and (ff_lngR is not None) and (ff_altR is not None):
            # convert to cartesian
            self.__f_x, self.__f_y, self.__f_z = geoutils.geog2enu(self.__f_lat, self.__f_lng, self.__f_alt, ff_latR, ff_lngR, ff_altR)
            #self.__f_x, self.__f_y = self.latlon2xy(ff_latR, ff_lngR)

            # return
            return True

        # return
        return False

    # ---------------------------------------------------------------------------------------------
    def __str__(self):
        return "sensor %s: (%s, %s, %s)=(%s, %s)" % (self.__id, self.__f_lat, self.__f_lng, self.__f_alt, self.__f_x, self.__f_y)

    # =============================================================================================
    # data
    # =============================================================================================

    # ---------------------------------------------------------------------------------------------
    @property
    def alt(self):
        return self.__f_alt

    # ---------------------------------------------------------------------------------------------
    @property
    def lat(self):
        return self.__f_lat

    # ---------------------------------------------------------------------------------------------
    @property
    def lng(self):
        return self.__f_lng

    # ---------------------------------------------------------------------------------------------
    @property
    def x(self):
        return self.__f_x

    # ---------------------------------------------------------------------------------------------
    @property
    def y(self):
        return self.__f_y

    # ---------------------------------------------------------------------------------------------
    @property
    def z(self):
        return self.__f_z

# < the end >--------------------------------------------------------------------------------------
