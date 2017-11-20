#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
glb_defs

defines e constantes válidas globalmente

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

revision 0.1  2017/nov  matias
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.1$"
__author__ = "Ivan Matias"
__date__ = "2017/11"

import math

# < config >---------------------------------------------------------------------------------------

CA = 5
AIR_TYPE = 0

NIC_SB = 0         # NIC Supplement-B
# "TIME" (T)
#
# Indicate wether or not the epoch of validity for horizontal position data in an airborne position message is
# an exact 0.2 UTC epoc. If the time of applicability of the position data is synchronized to an exact 0.2
# second UTC epoch, the "TIME" (T) subfield shall be set to "1"; otherwize, the "TIME" (T) subfield shall be set
# to ZERO (0).
T_FLAG = 0

EW_DIRECTION = 0
NS_DIRECTION = 1

BAROMETRIC_SOURCE = 1
ODD_FRAME = 1

MSG_SUBTYPE_1 = 1
MSG_SUBTYPE_2 = 2

VERTICAL_RATE_UP = 0
VERTICAL_RATE_DOWN = 1

ODD_TYPE = 'odd'
EVEN_TYPE = 'even'

FT_TO_M = 0.3048
KT_TO_MPS = 0.514444
FTPM_TO_MPS = 0.00508

NM_H_TO_NM_S = 0.000277778
DELAY = 1.0

# < chaves do dicionario de informações da aeronave >----------------------------------------------
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
LAST_UPDATE ='lu'
UNLAWFUL_INTERFERENCE = "ui"

# Número máximo de mensagens no buffer de mensagens ADS-B recebidas.
M_MAX_REC_MSGS = 5000

RAD_360 = 2 * math.pi
RAD_90 = math.pi / 2.0
RAD_180 = math.pi
RAD_270 = 3.0 * math.pi / 2.0
