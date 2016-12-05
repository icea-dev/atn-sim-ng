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


import math
import subprocess

from emanesh.emaneshell import EMANEShell

__author__ = "Márcio Monteiro"
__email__ = "muriloconte@gmail.com"
__date__ = "2016/12"
__version__ = "0.1"

shell = EMANEShell("127.0.0.1", 47000)


def set_location(nemid, lat, lon, alt, heading, speed, climb):

    if speed > 0:  # Avoids division by zero
        elev = math.degrees(math.atan(float(climb)/float(speed)))
        mag = math.sqrt(float(speed*speed) + float(climb*climb))
    else:
        elev = 0.0
        mag = 0.0

    # Updating location
    subprocess.call(['/usr/bin/emaneevent-location', str(nemid), 'latitude=%s' % lat, 'longitude=%s' % lon,
                     'altitude=%s' % alt, 'azimuth=%s' % heading, 'elevation=%s' % elev, 'magnitude=%s' % mag])


def get_nem_location(nem_id):
    locations = get_all_locations()

    for i in locations:
        if i['nem'] == nem_id:
            return i
    return None


def get_all_locations():

    # output = subprocess.check_output(["/usr/bin/emanesh", "127.0.0.1",
    #                                   "get", "table", '*', "phy", "LocationEventInfoTable"])
    output = subprocess.check_output(["/usr/bin/emanesh", "127.0.0.1",
                                     "get", "table", "nems", "phy", "LocationEventInfoTable"])

    # shell.onecmd("get table nems phy LocationEventInfoTable")

    lines = output.splitlines()[2:]

    nems = []

    for l in lines:
        if l.strip() == "":
            continue

        params = l.split()

        nemid = int(params[1])
        latitude = float(params[3])  # decimal degrees
        longitude = float(params[5])  # decimal degrees
        altitude = float(params[7])  # meters
        pitch = float(params[9])  # degrees
        roll = float(params[11])  # degrees
        yaw = float(params[13])  # degrees
        azimuth = float(params[15])  # degrees
        elevation = float(params[17])  # degrees
        magnitude = float(params[19])  # meters per second

        obj = {
            'nem': nemid,
            'latitude': latitude,
            'longitude': longitude,
            'altitude': altitude,
            'pitch': pitch,
            'roll': roll,
            'yaw': yaw,
            'azimuth': azimuth,
            'elevation': elevation,
            'magnitude': magnitude
        }

        nems.append(obj)

    return nems
