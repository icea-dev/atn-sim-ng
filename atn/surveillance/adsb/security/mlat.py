#!/usr/bin/env python
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

revision 0.1  2017/jun  mlabru
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.1$"
__author__ = "Milton Abrunhosa"
__date__ = "2017/06"

# < imports >--------------------------------------------------------------------------------------

# python library
import copy
import math

# numpy & scipy
import numpy as np

# atn-sim
import atn.geo_utils as gutl
import atn.surveillance.adsb.security.vincenty as vdst

# -------------------------------------------------------------------------------------------------
def mlat_1(fmat_sns_ecef, flst_toa):
    """
    multilateration
    """
    # init matrix
    lmat_x = []

    # number of measurements
    li_nmeas = len(fmat_sns_ecef)

    # for all measurements...
    for li_m in xrange(li_nmeas):
        # get position
        lf_x = fmat_sns_ecef[li_m][0]
        lf_y = fmat_sns_ecef[li_m][1]
        lf_z = fmat_sns_ecef[li_m][2]

        # calculate constants from measured distances and time for each receiver 
        Am = -2 * lf_x
        Bm = -2 * lf_y
        Cm = -2 * lf_z
        Dm = gutl.a * gutl.a + (pow(lf_x, 2) + pow(lf_y, 2) + pow(lf_z, 2)) - pow(flst_toa[li_m], 2)

        # put on matrix
        lmat_x += [[Am, Bm, Cm, Dm]]

    # convert to numpy matrix
    lmat_x = np.array(lmat_x)

    # solve using SVD
    (_, _, l_v) = np.linalg.svd(lmat_x)

    # get the minimizer
    l_pos = l_v[3, :]

    # resulting position in ECEF
    l_pos /= l_pos[3]

    # return estimated position in ECEF
    return l_pos[0], l_pos[1], l_pos[2]

# -------------------------------------------------------------------------------------------------
def mlat_2(fmat_sns_ecef, flst_toa):
    """
    multilateration
    """
    # init matrix
    lmat_a = []
    lmat_b = []

    # number of measurements
    li_nmeas = len(fmat_sns_ecef)

    # for all measurements...
    for li_m in xrange(li_nmeas):
        lf_x = fmat_sns_ecef[li_m][0]
        lf_y = fmat_sns_ecef[li_m][1]
        lf_z = fmat_sns_ecef[li_m][2]

        lf_Am = 2 * lf_x
        lf_Bm = 2 * lf_y
        lf_Cm = 2 * lf_z
        lf_Dm = gutl.a * gutl.a + (pow(lf_x, 2) + pow(lf_y, 2) + pow(lf_z, 2)) - pow(flst_toa[li_m], 2)

        lmat_a += [[lf_Am, lf_Bm, lf_Cm]]
        lmat_b += [[lf_Dm]]

    # convert to numpy matrix
    lmat_a = np.array(lmat_a)
    lmat_b = np.array(lmat_b)

    # solve using Least Squares of an MxN System
    # A*x = b --> x = (ATA)_inv.AT.b = A+.b
    l_AT = lmat_a.T
    l_ATA = np.matmul(l_AT, lmat_a)
    l_ATA_inv = np.linalg.inv(l_ATA)
    l_Aplus = np.matmul(l_ATA_inv, l_AT)

    # estimated positions
    l_pos = np.matmul(l_Aplus, lmat_b)

    # return estimated position in ECEF
    return l_pos[0], l_pos[1], l_pos[2]

# -------------------------------------------------------------------------------------------------
# this is the bootstrap process
                    
if "__main__" == __name__:

    # receivers
    ldct_sns = {1:[ -14.0831650347, -49.4030984872, 2. ],
                2:[ -15.2586421098, -47.8988661098, 2. ],
                3:[ -17.6120604234, -49.3750919052, 2. ],
                4:[ -17.6105780563, -46.2006404987, 2. ],
                5:[ -14.451676914,  -46.1818781943, 2. ]}

    # real position
    l_real = (-15.5, -47.5)

    # time of arrival
    llst_toa = [vdst.vincenty((l_sns[0], l_sns[1]), l_real) for l_sns in ldct_sns.values()]

    # init positions matrix
    lmat_sns_ecef = [[0., 0., 0.] for _ in xrange(len(ldct_sns))]

    # for all stations...
    for li_ndx, llst_sns in enumerate(ldct_sns.values()):
        # convert stations positions to ECEF
        lmat_sns_ecef[li_ndx][0], lmat_sns_ecef[li_ndx][1], lmat_sns_ecef[li_ndx][2] = gutl.geog2ecef(llst_sns[0], llst_sns[1], llst_sns[2])

    # calc estimated (method 2)
    l_xe, l_ye, l_ze = mlat_1(lmat_sns_ecef, llst_toa)

    # estimated position
    lat = math.degrees(math.asin(l_ze / gutl.a))
    lng = math.degrees(math.atan2(l_ye, l_xe))
    print "lat / lng estimated:", lat, lng 
    print "lat / lng real.....:", l_real[0], l_real[1]

    # converte real to ecef
    l_xr, l_yr, l_zr = gutl.geog2ecef(l_real[0], l_real[1], 1500.)

    print "distance:", math.sqrt(pow((l_xr - l_xe), 2) + pow((l_yr - l_ye), 2))

    # calc estimated (method 2)
    l_xe, l_ye, l_ze = mlat_2(lmat_sns_ecef, llst_toa)

    # estimated position
    lat = math.degrees(math.asin(l_ze / gutl.a))
    lng = math.degrees(math.atan2(l_ye, l_xe))
    print "lat / lng estimated:", lat, lng 
    print "lat / lng real.....:", l_real[0], l_real[1]

    # converte real to ecef
    l_xr, l_yr, l_zr = gutl.geog2ecef(l_real[0], l_real[1], 1500.)

    print "distance:", math.sqrt(pow((l_xr - l_xe), 2) + pow((l_yr - l_ye), 2))

# < the end >--------------------------------------------------------------------------------------
