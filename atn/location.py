#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
location

provides conversions between Cartesian and geographic coordinate systems. Depends on utm
contributed module, from https://pypi.python.org/pypi/utm (version 0.3.0).

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

revision 0.1  2017/abr  mlabru
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.1$"
__author__ = "mlabru, sophosoft"
__date__ = "2017/04"

# < imports >--------------------------------------------------------------------------------------

# python library
import logging

# 
import utm

# < module data >----------------------------------------------------------------------------------

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)

# -------------------------------------------------------------------------------------------------

class CLocation(object):
    """
    handling global location data. 
    keeps track of a latitude/longitude/altitude reference point and scale in order to convert between X,Y and geo coordinates.
    """
    # ---------------------------------------------------------------------------------------------
    def __init__(self):
        """
        constructor
        """
        self.reset()
        self.zonemap = {}

        for n, l in utm.ZONE_LETTERS:
            self.zonemap[l] = n

    # ---------------------------------------------------------------------------------------------
    def reset(self):
        """
        reset to initial state
        """
        # (x, y, z) coordinates of the point given by self.refgeo
        self.refxyz = (0., 0., 0.)
        # decimal latitude, longitude, and altitude at the point (x, y, z)
        self.setrefgeo(0., 0., 0.)
        # 100 pixels equals this many meters
        self.refscale = 1.
        # cached distance to refpt in other zones
        self.zoneshifts = {}

    # ---------------------------------------------------------------------------------------------
    def configure_values(self, values):
        """ 
        receive configuration message for setting the reference point and scale
        """
        if values is None:
            # logger
            M_LOG.debug("location data missing")
            # return
            return None

        values = values.split('|')

        # cartesian coordinate reference point
        refx,refy = map(lambda x: float(x), values[0:2])
        refz = 0.
        self.refxyz = (refx, refy, refz)

        # geographic reference point
        lat, long, alt = map(lambda x: float(x), values[2:5])

        self.setrefgeo(lat, long, alt)
        self.refscale = float(values[5])

    # ---------------------------------------------------------------------------------------------
    def px2m(self, val):
        """ 
        convert the specified value in pixels to meters using the configured scale. The scale is given as s, where 100 pixels = s meters
        """
        return (val / 100.) * self.refscale

    # ---------------------------------------------------------------------------------------------
    def m2px(self, val):
        """ 
        convert the specified value in meters to pixels using the configured scale. The scale is given as s, where 100 pixels = s meters
        """
        if self.refscale == 0.:
            return 0.

        return 100. * (val / self.refscale)

    # ---------------------------------------------------------------------------------------------
    def setrefgeo(self, lat, lon, alt):
        """ 
        record the geographical reference point decimal (lat, lon, alt) and convert and store its UTM equivalent for later use
        """
        self.refgeo = (lat, lon, alt)

        # easting, northing, zone
        (e, n, zonen, zonel) = utm.from_latlon(lat, lon)
        self.refutm = ((zonen, zonel), e, n, alt)

    # ---------------------------------------------------------------------------------------------
    def getgeo(self, x, y, z):
        """ 
        given (x, y, z) cartesian coordinates, convert them to latitude, longitude, and altitude based on the configured reference point and scale
        """
        # shift (x, y, z) over to reference point (x, y, z)
        x -= self.refxyz[0]
        y = -(y - self.refxyz[1])

        if z is None:
            z = self.refxyz[2]

        else:
            z -= self.refxyz[2]

        # use UTM coordinates since unit is meters
        zone = self.refutm[0]

        if zone == "":
            raise ValueError, "reference point not configured"

        e = self.refutm[1] + self.px2m(x)
        n = self.refutm[2] + self.px2m(y)
        alt = self.refutm[3] + self.px2m(z)

        (e, n, zone) = self.getutmzoneshift(e, n)

        try:
            lat, lon = utm.to_latlon(e, n, zone[0], zone[1])

        except utm.OutOfRangeError:
            M_LOG.warning("UTM out of range error for e=%s n=%s zone=%s xyz=(%s,%s,%s)" % (e, n, zone, x, y, z))
            lat, lon = self.refgeo[:2]

        # return
        return (lat, lon, alt)

    # ---------------------------------------------------------------------------------------------
    def getxyz(self, lat, lon, alt):
        """ 
        given latitude, longitude, and altitude location data, convert them to (x, y, z) Cartesian coordinates based on the configured
        reference point and scale. Lat/lon is converted to UTM meter coordinates, UTM zones are accounted for, and the scale turns meters to pixels
        """
        # convert lat/lon to UTM coordinates in meters
        (e, n, zonen, zonel) = utm.from_latlon(lat, lon)
        (rlat, rlon, ralt) = self.refgeo
        xshift = self.geteastingshift(zonen, zonel)

        if xshift is None:
            xm = e - self.refutm[1]

        else:
            xm = e + xshift

        yshift = self.getnorthingshift(zonen, zonel)

        if yshift is None:
            ym = n - self.refutm[2]

        else:
            ym = n + yshift

        zm = alt - ralt
        
        # shift (x,y,z) over to reference point (x,y,z)
        x = self.m2px(xm) + self.refxyz[0]
        y = -(self.m2px(ym) + self.refxyz[1])
        z = self.m2px(zm) + self.refxyz[2]

        # return
        return (x, y, z)

    # ---------------------------------------------------------------------------------------------
    def geteastingshift(self, zonen, zonel):
        """ 
        If the lat, lon coordinates being converted are located in a different UTM zone than the canvas reference point, the UTM meters
        may need to be shifted. This picks a reference point in the same longitudinal band (UTM zone number) as the provided zone, to calculate the shift in meters for the x coordinate.
        """
        rzonen = int(self.refutm[0][0])

        if zonen == rzonen:
            return None # same zone number, no x shift required

        z = (zonen, zonel)

        if z in self.zoneshifts and self.zoneshifts[z][0] is not None:
            return self.zoneshifts[z][0] # x shift already calculated, cached
            
        (rlat, rlon, ralt) = self.refgeo
        lon2 = rlon + 6*(zonen - rzonen) # ea. zone is 6deg band
        (e2, n2, zonen2, zonel2) = utm.from_latlon(rlat, lon2) # ignore northing

        # NOTE: great circle distance used here, not reference ellipsoid!
        xshift = utm.haversine(rlon, rlat, lon2, rlat) - e2

        # cache the return value
        yshift = None

        if z in self.zoneshifts:
            yshift = self.zoneshifts[z][1]

        self.zoneshifts[z] = (xshift, yshift)
        return xshift
    
    # ---------------------------------------------------------------------------------------------
    def getnorthingshift(self, zonen, zonel):
        """ 
        If the lat, lon coordinates being converted are located in a different UTM zone than the canvas reference point, the UTM meters
        may need to be shifted. This picks a reference point in the same latitude band (UTM zone letter) as the provided zone, to calculate the shift in meters for the y coordinate.
        """
        rzonel = self.refutm[0][1]

        if zonel == rzonel:
            return None # same zone letter, no y shift required

        z = (zonen, zonel)

        if z in self.zoneshifts and self.zoneshifts[z][1] is not None:
            return self.zoneshifts[z][1] # y shift already calculated, cached
        
        (rlat, rlon, ralt) = self.refgeo

        # zonemap is used to calculate degrees difference between zone letters
        latshift = self.zonemap[zonel] - self.zonemap[rzonel]
        lat2 = rlat + latshift # ea. latitude band is 8deg high
        (e2, n2, zonen2, zonel2) = utm.from_latlon(lat2, rlon)

        # NOTE: great circle distance used here, not reference ellipsoid
        yshift = -(utm.haversine(rlon, rlat, rlon, lat2) + n2)

        # cache the return value
        xshift = None

        if z in self.zoneshifts:
            xshift = self.zoneshifts[z][0]

        self.zoneshifts[z] = (xshift, yshift)
        return yshift

    # ---------------------------------------------------------------------------------------------
    def getutmzoneshift(self, e, n):
        """ 
        given UTM easting and northing values, check if they fall outside the reference point's zone boundary. Return the UTM coordinates in a 
        different zone and the new zone if they do. Zone lettering is only changed when the reference point is in the opposite hemisphere.
        """
        zone = self.refutm[0]
        (rlat, rlon, ralt) = self.refgeo

        if e > 834000 or e < 166000:
            num_zones = (int(e) - 166000) / (utm.R/10)
            # estimate number of zones to shift, E (positive) or W (negative)
            rlon2 = self.refgeo[1] + (num_zones * 6)
            (e2, n2, zonen2, zonel2) = utm.from_latlon(rlat, rlon2)
            xshift = utm.haversine(rlon, rlat, rlon2, rlat)
            # after >3 zones away from refpt, the above estimate won't work
            # (the above estimate could be improved)
            if not 100000 <= (e - xshift) < 1000000:
                # move one more zone away
                num_zones = (abs(num_zones)+1) * (abs(num_zones)/num_zones)
                rlon2 = self.refgeo[1] + (num_zones * 6)
                (e2, n2, zonen2, zonel2) = utm.from_latlon(rlat, rlon2)
                xshift = utm.haversine(rlon, rlat, rlon2, rlat)
            e = e - xshift
            zone = (zonen2, zonel2)

        if n < 0:
            # refpt in northern hemisphere and we crossed south of equator
            n += 10000000
            zone = (zone[0], 'M')

        elif n > 10000000:
            # refpt in southern hemisphere and we crossed north of equator
            n -= 10000000
            zone = (zone[0], 'N')

        return (e, n, zone)

# <the end>----------------------------------------------------------------------------------------
