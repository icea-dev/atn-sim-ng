#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016, ICEA
#
# This file is part of atn-sim
#
# atn-sim is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# atn-sim is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from abc import ABCMeta, abstractmethod

__author__ = "Marcio Monteiro"
__version__ = "0.1"
__date__ = "2016-dec-08"


class AdsbFeed(object):
    """Abstract class that provides information for ADS-B Out transponders.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_kinematics(self):
        """

        :return:
        """
        raise NotImplementedError()


    @abstractmethod
    def get_hacker_position(self):
        """

        :return:
        """
        raise NotImplementedError()


    @abstractmethod
    def get_ssr(self):
        """Informs current squawk code of the given aircraft.

        Examples:
            - 7500: Hi-Jacking
            - 7600: Radio Failure
            - 7700: Emergency

        The complete list can be found in http://www.flightradars.eu/lsquawkcodes.html
        """
        raise NotImplementedError()


    @abstractmethod
    def get_spi(self):
        """Informs if SPI is activated.
        """
        raise NotImplementedError()


    @abstractmethod
    def get_callsign(self):
        """Provides the callsign of the given aircraft.
        """
        raise NotImplementedError()


    @abstractmethod
    def get_position(self):
        """Provides latitude, longitude, and altitude in meters.
        """
        raise NotImplementedError()


    @abstractmethod
    def get_velocity(self):
        """Provides azimuth, climb_rate, and speed in meters per second.
        """
        raise NotImplementedError()


    @abstractmethod
    def get_icao24(self):
        raise NotImplementedError()


    @abstractmethod
    def get_capabilities(self):
        raise NotImplementedError()


    @abstractmethod
    def get_type(self):
        raise NotImplementedError()


    @abstractmethod
    def is_track_updated(self):
        raise NotImplementedError()


    @abstractmethod
    def start(self):
        raise NotImplementedError()
