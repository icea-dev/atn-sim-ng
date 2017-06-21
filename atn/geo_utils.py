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

""" 
conversao de coordenadas geográficas para ENU. Parametros do WGS84 - Defense Mapping Agency Technical Report
"""

import math

__author__ = "Roberto Xavier"
__version__ = "0.1"
__date__ = "2016-dec-08"

# ellipsoid flattening
f = 1. / 298.257223563
# semi-eixo maior em metros
a = 6378137.
# semi-eixo menor em metros
b = a * (1. - f)
# b = 6356752.31424518
# primeira excentricidade
e = math.sqrt(((a ** 2) - (b ** 2)) / (a ** 2))
# segunda excentricidade
e_ = math.sqrt(((a ** 2) - (b ** 2)) / (b ** 2))
# primeira excentricidade ao quadrado
e2 = 0.00669437999013


def geog2ecef(lat, lng, alt):
    """
    geográfica para ECEF

    entrada: lat e lng (graus), alt (m)

    saída: x, y, z (m)
    """
    lat_r = math.radians(lat)
    lng_r = math.radians(lng)

    N = a / math.sqrt(1. - (e2 * math.sin(lat_r) * math.sin(lat_r)))

    x = (N + alt) * math.cos(lat_r) * math.cos(lng_r)
    y = (N + alt) * math.cos(lat_r) * math.sin(lng_r)
    z = (N * (1. - e2) + alt) * math.sin(lat_r)

    return x, y, z


def ecef2enu(X, Y, Z, latRef, lngRef, altRef):
    """
    ECEF para ENU

    entrada: X, Y, Z (m): coordenadas ECEF do alvo
             latRef e lngRef (graus), altRef (m): coordenadas do radar

    saída: x, y, z (m): coordenadas ENU do alvo em relação ao radar
    """
    xRef, yRef, zRef = geog2ecef(latRef, lngRef, altRef)

    xdif = X - xRef
    ydif = Y - yRef
    zdif = Z - zRef

    latRef_r = math.radians(latRef)
    lngRef_r = math.radians(lngRef)

    x = - math.sin(lngRef_r) * xdif + math.cos(lngRef_r) * ydif
    y = - math.sin(latRef_r) * math.cos(lngRef_r) * xdif - math.sin(latRef_r) * math.sin(lngRef_r) * ydif + math.cos(latRef_r) * zdif
    z =   math.cos(latRef_r) * math.cos(lngRef_r) * xdif + math.cos(latRef_r) * math.sin(lngRef_r) * ydif + math.sin(latRef_r) * zdif

    return x, y, z


def geog2enu(latPto, lngPto, altPto, latRef, lngRef, altRef):
    """
    geografica para ENU

    entrada: latPto e lngPto (graus), altPto (m): coord geográficas do ponto
             latRef e lngRef (graus), altRef (m): coord geográficas do radar

    saída: x, y, z (m) coordenadas cartesianas do ponto em relação ao radar
    """
    # convert from geographic to ECEF
    X, Y, Z = geog2ecef(latPto, lngPto, altPto)
    # convert from ECEF to ENU
    x, y, z = ecef2enu(X, Y, Z, latRef, lngRef, altRef)

    return x, y, z

if __name__ == "__main__":
    print ""

    latRef = float(raw_input("Entre com latitude  do radar (em graus):  "))
    lngRef = float(raw_input("Entre com longitude do radar (em graus):  "))
    altRef = float(raw_input("Entre com altitude  do radar (em metros):  "))

    print ""

    while True:
        latPto = float(raw_input("Entre com latitude  do ponto (em graus):  "))
        lngPto = float(raw_input("Entre com longitude do ponto (em graus):  "))
        altPto = float(raw_input("Entre com altitude  do ponto (em metros):  "))

        x, y, z = geog2enu(latPto, lngPto, altPto, latRef, lngRef, altRef)

        print "Coord X do ponto:  %15.10f m" % x, "  | %15.10f mn" % float(x/1852)
        print "Coord Y do ponto:  %15.10f m" % y, "  | %15.10f mn" % float(y/1852)
        print "Coord Z do ponto:  %15.10f m" % z, "  | %15.10f mn" % float(z/1852)
        print ""
