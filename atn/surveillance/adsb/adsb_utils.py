#!/usr/bin/env python
#
# Copyright 2010, 2012 Nick Foster
#
# This file is part of gr-air-modes
#
# gr-air-modes is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# gr-air-modes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gr-air-modes; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

import math
import time

MPS_TO_KT = 1.943844492
MPS_TO_FT_MIN = 196.850393701
RAD_360 = 2 * math.pi
RAD_90 = math.pi / 2.0
RAD_180 = math.pi
RAD_270 = 3.0 * math.pi / 2.0


class ADSBError(Exception):
    pass


class MetricAltError(ADSBError):
    pass


class ParserError(ADSBError):
    pass


class NoHandlerError(ADSBError):
    def __init__(self, msgtype=None):
        self.msgtype = msgtype


class MlatNonConvergeError(ADSBError):
    pass


class CPRNoPositionError(ADSBError):
    pass


class CPRBoundaryStraddleError(CPRNoPositionError):
    pass


class FieldNotInPacket(ParserError):
    def __init__(self, item):
        self.item = item


# this implements CPR position decoding and encoding.
# the decoder is implemented as a class, cpr_decoder, which keeps state for local decoding.
# the encoder is cpr_encode([lat, lon], type (even=0, odd=1), and surface (0 for surface, 1 for airborne))

# TODO: remove range/bearing calc from CPR decoder class. you can do this outside of the decoder.

latz = 15


def nz(ctype):
    return 4 * latz - ctype


def dlat(ctype, surface):
    if surface == 1:
        tmp = 90.0
    else:
        tmp = 360.0

    nzcalc = nz(ctype)
    if nzcalc == 0:
        return tmp
    else:
        return tmp / nzcalc


def nl(declat_in):
    if abs(declat_in) >= 87.0:
        return 1.0
    return math.floor( (2.0*math.pi) * math.acos(1.0- (1.0-math.cos(math.pi/(2.0*latz))) / math.cos( (math.pi/180.0)*abs(declat_in) )**2 )**-1)


def dlon(declat_in, ctype, surface):
    if surface:
        tmp = 90.0
    else:
        tmp = 360.0
    nlcalc = max(nl(declat_in)-ctype, 1)
    return tmp / nlcalc


def decode_lat(enclat, ctype, my_lat, surface):
    tmp1 = dlat(ctype, surface)
    tmp2 = float(enclat) / (2**17)
    j = math.floor(my_lat/tmp1) + math.floor(0.5 + ((my_lat % tmp1) / tmp1) - tmp2)

    return tmp1 * (j + tmp2)


def decode_lon(declat, enclon, ctype, my_lon, surface):
    tmp1 = dlon(declat, ctype, surface)
    tmp2 = float(enclon) / (2**17)
    m = math.floor(my_lon / tmp1) + math.floor(0.5 + ((my_lon % tmp1) / tmp1) - tmp2)

    return tmp1 * (m + tmp2)


def cpr_resolve_local(my_location, encoded_location, ctype, surface):
    [my_lat, my_lon] = my_location
    [enclat, enclon] = encoded_location

    decoded_lat = decode_lat(enclat, ctype, my_lat, surface)
    decoded_lon = decode_lon(decoded_lat, enclon, ctype, my_lon, surface)

    return [decoded_lat, decoded_lon]


def cpr_resolve_global(evenpos, oddpos, mypos, mostrecent, surface):
    # cannot resolve surface positions unambiguously without knowing receiver position
    if surface and mypos is None:
        raise CPRNoPositionError

    dlateven = dlat(0, surface)
    dlatodd  = dlat(1, surface)

    evenpos = [float(evenpos[0]), float(evenpos[1])]
    oddpos = [float(oddpos[0]), float(oddpos[1])]

    j = math.floor(((nz(1)*evenpos[0] - nz(0)*oddpos[0])/2**17) + 0.5)  # latitude index

    rlateven = dlateven * ((j % nz(0))+evenpos[0]/2**17)
    rlatodd  = dlatodd  * ((j % nz(1))+ oddpos[0]/2**17)

    # limit to -90, 90
    if rlateven > 270.0:
        rlateven -= 360.0
    if rlatodd > 270.0:
        rlatodd -= 360.0

    # This checks to see if the latitudes of the reports straddle a transition boundary
    # If so, you can't get a globally-resolvable location.
    if nl(rlateven) != nl(rlatodd):
        raise CPRBoundaryStraddleError

    if mostrecent == 0:
        rlat = rlateven
    else:
        rlat = rlatodd

    # disambiguate latitude
    if surface:
        if mypos[0] < 0:
            rlat -= 90

    dl = dlon(rlat, mostrecent, surface)
    nl_rlat = nl(rlat)

    m = math.floor(((evenpos[1]*(nl_rlat-1)-oddpos[1]*nl_rlat)/2**17)+0.5) #longitude index

    # when surface positions straddle a disambiguation boundary (90 degrees),
    # surface decoding will fail. this might never be a problem in real life, but it'll fail in the
    # test case. the documentation doesn't mention it.

    if mostrecent == 0:
        enclon = evenpos[1]
    else:
        enclon = oddpos[1]

    rlon = dl * ((m % max(nl_rlat-mostrecent,1)) + enclon/2.**17)

    # print "DL: %f nl: %f m: %f rlon: %f" % (dl, nl_rlat, m, rlon)
    # print "evenpos: %x, oddpos: %x, mostrecent: %i" % (evenpos[1], oddpos[1], mostrecent)

    if surface:
        # longitudes need to be resolved to the nearest 90 degree segment to the receiver.
        wat = mypos[1]
        if wat < 0:
            wat += 360
        zone = lambda lon: 90 * (int(lon) / 90)
        rlon += (zone(wat) - zone(rlon))

    # limit to (-180, 180)
    if rlon > 180:
        rlon -= 360.0

    return [rlat, rlon]


# calculate range and bearing between two lat/lon points
# should probably throw this in the mlat py somewhere or make another lib
def range_bearing(loc_a, loc_b):
    [a_lat, a_lon] = loc_a
    [b_lat, b_lon] = loc_b

    esquared = (1/298.257223563)*(2-(1/298.257223563))
    earth_radius_mi = 3963.19059 * (math.pi / 180)

    delta_lat = b_lat - a_lat
    delta_lon = b_lon - a_lon

    avg_lat = ((a_lat + b_lat) / 2.0) * math.pi / 180

    R1 = earth_radius_mi*(1.0-esquared)/pow((1.0-esquared*pow(math.sin(avg_lat),2)),1.5)

    R2 = earth_radius_mi/math.sqrt(1.0-esquared*pow(math.sin(avg_lat),2))

    distance_North = R1*delta_lat
    distance_East = R2*math.cos(avg_lat)*delta_lon

    bearing = math.atan2(distance_East,distance_North) * (180.0 / math.pi)
    if bearing < 0.0:
        bearing += 360.0

    rnge = math.hypot(distance_East,distance_North)
    return [rnge, bearing]


class cpr_decoder:
    def __init__(self, my_location):
        self.my_location = my_location
        self.evenlist = {}
        self.oddlist = {}
        self.evenlist_sfc = {}
        self.oddlist_sfc = {}

    def set_location(self, new_location):
        self.my_location = new_location

    def weed_poslists(self):
        for poslist in [self.evenlist, self.oddlist]:
            for key, item in poslist.items():
                if time.time() - item[2] > 10:
                    del poslist[key]
        for poslist in [self.evenlist_sfc, self.oddlist_sfc]:
            for key, item in poslist.items():
                if time.time() - item[2] > 25:
                    del poslist[key]

    def decode(self, icao24, encoded_lat, encoded_lon, cpr_format, surface):
        if surface:
            oddlist = self.oddlist_sfc
            evenlist = self.evenlist_sfc
        else:
            oddlist = self.oddlist
            evenlist = self.evenlist

        # add the info to the position reports list for global decoding
        if cpr_format==1:
            oddlist[icao24] = [encoded_lat, encoded_lon, time.time()]
        else:
            evenlist[icao24] = [encoded_lat, encoded_lon, time.time()]

        [decoded_lat, decoded_lon] = [None, None]

        # okay, let's traverse the lists and weed out those entries that are older than 10 seconds
        self.weed_poslists()

        if (icao24 in evenlist) and (icao24 in oddlist):
            newer = (oddlist[icao24][2] - evenlist[icao24][2]) > 0  # figure out which report is newer
            [decoded_lat, decoded_lon] = cpr_resolve_global(evenlist[icao24][0:2], oddlist[icao24][0:2], self.my_location, newer, surface) #do a global decode
        else:
            raise CPRNoPositionError

        if self.my_location is not None:
            [rnge, bearing] = range_bearing(self.my_location, [decoded_lat, decoded_lon])
        else:
            rnge = None
            bearing = None

        return [decoded_lat, decoded_lon, rnge, bearing]


# encode CPR position
def cpr_encode(lat, lon, ctype, surface):
    if surface is True:
        scalar = 2.**19
    else:
        scalar = 2.**17

    # encode using 360 constant for segment size.
    dlati = dlat(ctype, False)
    yz = math.floor(scalar * ((lat % dlati)/dlati) + 0.5)
    rlat = dlati * ((yz / scalar) + math.floor(lat / dlati))

    # encode using 360 constant for segment size.
    dloni = dlon(lat, ctype, False)
    xz = math.floor(scalar * ((lon % dloni)/dloni) + 0.5)

    yz = int(yz) & (2**17-1)
    xz = int(xz) & (2**17-1)

    return (yz, xz)  # lat, lon


'''
ADS-B encoder funciotions
'''


def encode_header(df, ca, icao_addr):
    # Assemble bits
    msg = ''

    # DF (5-bit)
    msg += bin(df)[2:].zfill(5)

    # CA (3-bit)
    msg += bin(ca)[2:].zfill(3)

    # ICAO Address (24-bit)
    msg += bin(int(icao_addr, 16))[2:].zfill(24)

    return msg


def encode_aircraft_id(ca, icao24, aircraft_cat, callsign, df=17, es_type=4):

    ais_charcode = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9, "J": 10, "K": 11,
                    "L": 12, "M": 13, "N": 14, "O": 15, "P": 16, "Q": 17, "R": 18, "S": 19, "T": 20, "U": 21,
                    "V": 22, "W": 23, "X": 24, "Y": 25, "Z": 26, " ": 32, "0": 48, "1": 49, "2": 50, "3": 51,
                    "4": 52, "5": 53, "6": 54, "7": 55, "8": 56, "9": 57}
    n = len(callsign)

    msg = encode_header(df, ca, icao24)

    # Putting all to uppercase, just in case
    callsign = str(callsign).upper()

    # Extended Squitter Type (5 bit)
    msg += bin(es_type)[2:].zfill(5)

    # Aircraft Category (3 bits)
    msg += bin(aircraft_cat)[2:].zfill(3)

    for i in range(0, n):
        # Callsign Character (6 bits)
        msg += bin(ais_charcode[callsign[i]])[2:].zfill(6)

    # Complete with blank spaces tha remaining bits
    if 8 - n > 0:
        for i in range(n, 8):
            msg += bin(ais_charcode[" "])[2:].zfill(6)

    # CRC
    msg += calc_crc(msg)

    return msg


def encode_airborne_position(ca, icao_addr, lat, lon, sv, nicsb, alt, t_flag, f_flag, es_type=11, df=17):

    msg = encode_header(df, ca, icao_addr)

    # Extended Squitter Type (5 bit)
    msg += bin(es_type)[2:].zfill(5)

    # Surveillance status (2-bit)
    msg += bin(sv)[2:].zfill(2)

    # NIC Suppliment B
    msg += bin(nicsb)[2:].zfill(1)

    # Altitude (12-bit)
    msg += bin(alt)[2:].zfill(12)

    # UTC (1 bit)
    msg += bin(t_flag)[2:].zfill(1)

    # CPR format (1 bit)
    msg += bin(f_flag)[2:].zfill(1)

    # Latitude (CPR encoded, 17 bit)
    msg += bin(lat)[2:].zfill(17)

    # Longitude (CPR encoded, 17 bit)
    msg += bin(lon)[2:].zfill(17)

    # CRC
    msg += calc_crc(msg)

    return msg


def encode_airborne_velocity(ca, icao24, es_subtype, ic_flag, reserved_a,
                             nacv, ew_dir, ew_vel, ns_dir, ns_vel, vrate_src,
                             vrate_sign, vrate, reserved_b, h_sign, h_diff):
    """
    This method creates a binary buffer that defines the ADS-B Airbone Velocity
    Message

    Args:
        ca : Capability
        icao24 : ICAO address
        es_subtype : Subtype code
        ic_flag : Intent change flag
        reserved_a : Reseved-A
        nacv : Navigation accuracy category for velocity
        ew_dir : East/West velocity sign
        ew_vel : East/West velocity (knots)
        ns_dir : North/South velocity sign
        ns_vel : North/South velocity (knots)
        vrate_src : Vertical rate source
        vrate_sign : Vertical rate sign
        vrate : Vertical rate (ft/min)
        reserved_b : Reserved-B
        h_sign : Diff from baro alt, sign
        h_diff : Diff from baro alt

    Returns:
        The binary buffer that defines the ADS-B Airbone Velocity Message.

    """
    # Downlink Format Field DF=17
    df = 17

    # Type Code for determining ADS-B Message Type [19-Airbone Velocity Message]
    type_code = 19

    # Mode-S header
    msg = encode_header(df, ca, icao24)

    # Extended Squitter Type (5 bit)
    msg += bin(type_code)[2:].zfill(5)

    # Extended Squitter Sub Type (3 bit)
    msg += bin(es_subtype)[2:].zfill(3)

    # Intent Change Flag (1 bit)
    msg += bin(ic_flag)[2:].zfill(1)

    # Reserved-A (1 bit)
    msg += bin(reserved_a)[2:].zfill(1)

    # NACv: Navigation Accuracy category for Velocity (3 bits)
    msg += bin(nacv)[2:].zfill(3)

    # East-West Velocity sign (1 bit)
    msg += bin(ew_dir)[2:].zfill(1)

    # East-West Velocity (10 bits)
    msg += bin(ew_vel)[2:].zfill(10)

    # North-South Velocity sign (1 bit)
    msg += bin(ns_dir)[2:].zfill(1)

    # North-South Velocity (10 bits)
    msg += bin(ns_vel)[2:].zfill(10)

    # Vertical Rate Src (1 bit)
    msg += bin(vrate_src)[2:].zfill(1)

    # Vertical Rate Src Sign (1 bit)
    msg += bin(vrate_sign)[2:].zfill(1)

    # Vertical Rate (9 bits)
    msg += bin(vrate)[2:].zfill(9)

    # Reserved-B (2-bit)
    msg += bin(reserved_b)[2:].zfill(2)

    # Difference From Barometric Altitude Sign (1 bit)
    msg += bin(h_sign)[2:].zfill(1)

    # Difference From Barometric Altitude (7 bits)
    msg += bin(h_diff)[2:].zfill(7)

    # CRC
    msg += calc_crc(msg)

    return msg


def calc_crc(msg):
    msg_bytes = bin2bytes(msg)
    crc = modes_check_crc(msg_bytes, len(msg_bytes))
    return bin(crc)[2:].zfill(24)

''' Mode-S related functions '''

crc_table = [0]*256
POLY = 0xFFF409

#
# generate a bytewise lookup CRC table
#
def generate_crc_table():
    crc = 0
    for n in range(0, 256):
        crc = n << 16
        for k in range(0, 8):
            if crc & 0x800000:
                crc = ((crc << 1) ^ POLY) & 0xFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFF

        crc_table[n] = crc & 0xFFFFFF


#
# Perform a bytewise CRC check
#
def modes_check_crc(data, length):
    if crc_table[1] != POLY:
        generate_crc_table()
    crc = 0
    for i in range(0, length):
        crc = crc_table[((crc >> 16) ^ data[i]) & 0xff] ^ (crc << 8)
    return crc & 0xFFFFFF

#
# Converts a binary string ('101010101...') to a list of bytes (each element from 0 to 255)
#
def bin2bytes(bits):
    nbytes = len(bits) / 8
    bytevec = [0]*nbytes

    for i in range(0, nbytes):
        bytevec[i] = int(bits[i*8:i*8+8], 2)

    return bytevec


def to_unit_adsb(heading, vertical_rate, ground_speed):
    """Convert to units of ADS-B message

    Args:
        heading (float): The heading of airborne in degress.
        vertical_rate (float): The vertical rate of airborne in m/s.
        ground_speed (float): The ground speed of airborne in m/s.

    Returns:
        Returns heading in radians, vertical_rate in ft/min and ground
        speed in knots.
    """
    # Converting degrees to radians
    radians = heading * math.pi / 180.0

    # Converting m/s to feet/min
    rate = vertical_rate * MPS_TO_FT_MIN

    # Converting m/s to knots
    speed = ground_speed * MPS_TO_KT

    return radians, rate, speed
