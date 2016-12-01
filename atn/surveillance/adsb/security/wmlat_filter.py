import ConfigParser
import math
import MySQLdb
import numpy
import os
import time

from scipy import linalg

import atn.surveillance.adsb.decoder as decoder
import atn.geo_utils as geoutils

from ..forwarders import dump1090_fwrd
from ..forwarders import database_fwrd

class MlatServer:

    EVEN_MSG = 0
    ODD_MSG = 1
    FT_TO_M = 0.3048
    KT_TO_MPS = 0.514444
    FTPM_TO_MPS = 0.00508

    def __init__(self, config="aimod.cfg"):
        self.dbname = "atn_sim"
        self.dbpass = "atn_sim"
        self.dbuser = "atn_sim"
        self.dbhost = "127.0.0.1"

        self.debug = False

        # Variables used for decoding ADS-B position messages
        # The key is the icao24 address
        self.lastEvenMsg = {}
        self.lastOddMsg = {}
        self.lastLatitude = {}
        self.lastLongitude = {}
        self.lastAltitude = {}

        self.sensors = {}
        self.forwarders = []

        # Reference point for Lat,Long to X,Y
        self.lat0 = None
        self.lon0 = None
        self.alt0 = None

        # Reading configuration file
        if os.path.exists(config):
            conf = ConfigParser.ConfigParser()
            conf.read(config)

            self.name = conf.get("General", "id")
            self.dbhost = conf.get("General", "dbhost")
            self.dbuser = conf.get("General", "dbuser")
            self.dbpass = conf.get("General", "dbpass")
            self.dbname = conf.get("General", "dbname")

            # Reading destinations to forward reliable messages
            for dst in conf.get("General", "destinations").split():
                items = conf.items(dst)
                d = {}

                for i in items:
                    d[i[0]] = i[1]

                if d["type"] == "dump1090":
                    f = dump1090_fwrd.Dump1090Forwarder(items=d)
                    f.set_timeout(0.5)
                    self.forwarders.append(f)

                elif d["type"] == "database":
                    f = database_fwrd.DatabseForwarder(sensor_id=self.name, items=d)
                    self.forwarders.append(f)

        # Connecting to database in order to read unprocessed messages
        self.db = MySQLdb.connect(self.dbhost, self.dbuser, self.dbpass, self.dbname)

        # Creating sensors objects
        cursor = self.db.cursor()

        # Checking the declared sensors on database
        self.nsensors = cursor.execute("SELECT id FROM %s" % Sensor.SENSOR_TABLE)

        rows = cursor.fetchall()

        print "Num. Sensors: %s" % self.nsensors
        print "DB Name:      %s" % self.dbname
        print "DB Server:    %s" % self.dbhost

        for row in rows:
            sensor_id = row[0]

            # Creating new sensor object
            sensor = Sensor(sensor_id, dbname=self.dbname, dbuser=self.dbuser, dbpass=self.dbpass, dbhost=self.dbhost)

            if self.lat0 is None and self.lon0 is None:
                self.lat0 = sensor.latitude
                self.lon0 = sensor.longitude
                self.alt0 = sensor.altitude

            # Converts lat, lon to x, y
            sensor.update(self.lat0, self.lon0, self.alt0)

            # Add sensor to dictionary
            self.sensors[sensor_id] = sensor

        # Remove old messages
        rows = cursor.execute("DELETE FROM adsb_messages WHERE created < now()")
        self.db.commit()

        print "%d old message(s) deleted" % rows

        cursor.close()

    def start(self):

        while True:
            cursor = self.db.cursor()

            # Counting number of unprocessed messages
            cursor.execute("SELECT COUNT(*) FROM adsb_messages")
            result = cursor.fetchone()
            t0 = time.time()
            nmsgs = int(result[0])

            # Select next message
            nrows = cursor.execute("SELECT id, message, sensor_id, toa, created FROM adsb_messages ORDER BY created ASC LIMIT 1")
            if nrows > 0:
                id, message, sensor_id, toa, created = cursor.fetchone()
                ntries = 0

                for i in range(0, 4):
                    if self.process_msg(message):
                        break
                    else:
                        ntries += 1
                        time.sleep(0.100)

                if ntries > 0:
                    self.process_msg(message, True)

                t1 = time.time()
                # print "%s in %s s: %s" % (nmsgs, t1-t0, nmsgs/(t1-t0))

            cursor.close()

    def process_msg(self, message, delete=False):

        icao24 = decoder.get_icao_addr(message)

        cursor = self.db.cursor()

        # Checking which sensors have received the same message
        query1 = "SELECT id, sensor_id, toa, created FROM adsb_messages WHERE message='%s' ORDER BY created ASC LIMIT %s" % (message, self.nsensors)
        nrows = cursor.execute(query1)

        rows = cursor.fetchall()

        if nrows == 0:
            if delete:
                cursor.execute("DELETE FROM adsb_messages WHERE message='%s'" % message)
                self.db.commit()
            return False

        # Message ID
        msg_id = [0]*nrows

        # Sensor ID
        sensor_id = [0]*nrows

        # Time of arrival
        toa = [0]*nrows

        # Position of sensor
        xpos = [0]*nrows
        ypos = [0]*nrows
        zpos = [0]*nrows

        # Position of object (relative to sensor)
        # tx_xpos = [0]*nrows
        # tx_ypos = [0]*nrows
        # tx_zpos = [0]*nrows

        i = 0
        for row in rows:
            # Time of arrival
            toa[i] = row[2]

            # Sensor ID
            sensor_id[i] = row[1]

            # Message ID
            msg_id[i] = row[0]

            # Location of sensor
            xpos[i] = self.sensors[sensor_id[i]].xpos
            ypos[i] = self.sensors[sensor_id[i]].ypos
            zpos[i] = self.sensors[sensor_id[i]].altitude

            i += 1

        # Do not process it with insufficient data
        if nrows < self.nsensors:
            # Deleting messages from database
            if delete:
                for i in msg_id:
                    cursor.execute("DELETE FROM adsb_messages WHERE id=%s" % i)

            return False

        # Verifying declared position (in X, Y)
        x, y = self.get_declared_xy(message)

        # Determining source of transmission using mulilateration
        _x, _y = self.get_estimated_xy(xpos, ypos, zpos, toa)

        # Determining reliability of message
        if x is not None and y is not None and _x is not None and _y is not None:

            # 2D distance between reported and estimated positions
            distance = math.sqrt((x - _x)**2 + (y - _y)**2)

            if distance <= 1000:
                print "'%s'\t%d\t%s[PASS]%s" % (message, distance, bcolors.OKBLUE, bcolors.ENDC)

                # Forward received ADS-B message to all configured forwarders
                for f in self.forwarders:
                    f.forward(message, None)
            else:
                print "'%s'\t%d\t%s[DROP]%s" % (message, distance, bcolors.FAIL, bcolors.ENDC)

        # Deleting processed messages from database
        for i in msg_id:
            cursor.execute("DELETE FROM adsb_messages WHERE id=%s" % i)

        self.db.commit()

        cursor.close()

        return True

    def get_declared_xy(self, message):

        icao24 = decoder.get_icao_addr(message)

        # Checks for airborne position msg type
        if decoder.get_tc(message) in range(9,19):
            lat, lon, alt = self.decode_position(message)

            if lat is not None and lon is not None:
                # x, y = self.latlon2xy(lat,lon)
                x, y, z = geoutils.geog2enu(lat, lon, alt, self.lat0, self.lon0, self.alt0)
            else:
                x = None
                y = None

            return x, y

        else:
            # Using last reported position as reference

            if icao24 in self.lastLatitude:
                lat = self.lastLatitude[icao24]
                lon = self.lastLongitude[icao24]
                alt = self.lastAltitude[icao24]

                x, y, z = geoutils.geog2enu(lat, lon, alt, self.lat0, self.lon0, self. alt0)
            else:
                x = None
                y = None

            return x, y

    def get_estimated_xy(self, xpos, ypos, zpos, toa):

        # Number of measurements
        nmeas = len(toa)

        # Sorting by time of arrival, where the last sensor to receive is always the reference
        # This keeps the MLAT error low.
        _t = numpy.array(toa)
        _i = numpy.argsort(_t)[::-1]

        _xpos = [0]*nmeas
        _ypos = [0]*nmeas
        _zpos = [0]*nmeas
        _toa = [0]*nmeas

        for i in range(0, nmeas):
            _xpos[i] = xpos[_i[i]]
            _ypos[i] = ypos[_i[i]]
            _zpos[i] = zpos[_i[i]]
            _toa[i] = toa[_i[i]]

        # Speed of light (in meters per second)
        vel = 299792458

        # Time difference of arrival
        dt = [0]*nmeas
        for i in range(0, nmeas):
            dt[i] = _toa[i] - _toa[0]
            if i > 0 and dt[i] == 0:
                return None, None

        A = [0]*nmeas
        B = [0]*nmeas
        C = [0]*nmeas
        D = [0]*nmeas

        #
        for m in range(2, nmeas):
            A[m] = 2*_xpos[m]/(vel*dt[m]) - 2*_xpos[1]/(vel*dt[1])
            B[m] = 2*_ypos[m]/(vel*dt[m]) - 2*_ypos[1]/(vel*dt[1])
            C[m] = 2*_zpos[m]/(vel*dt[m]) - 2*_zpos[1]/(vel*dt[1])
            D[m] = vel*dt[m] - vel*dt[1] - (_xpos[m]**2 + _ypos[m]**2 + _zpos[m]**2) / (vel*dt[m]) + (_xpos[1]**2 + _ypos[1]**2 + _zpos[1]**2) / (vel*dt[1])

        X = numpy.matrix([[A[2], B[2], C[2]], [A[3], B[3], C[3]], [A[4], B[4], C[4]]])
        b = numpy.array([-D[2], -D[3], -D[4]])
        b.shape = (3, 1)

        try:
            location = linalg.inv(X).dot(b)

            x_est = location[0][0]
            y_est = location[1][0]
            z_est = location[2][0]

            return x_est, y_est

        except numpy.linalg.linalg.LinAlgError:
            return None, None

    def decode_position(self, message):

        # Aircraft (ICAO24 address)
        icaoaddr = decoder.get_icao_addr(message)

        # Check if message is even or odd
        if int(decoder.get_oe_flag(message)) == MlatServer.ODD_MSG:
            self.lastOddMsg[icaoaddr] = message
            t0 = 0
            t1 = 1
        else:
            self.lastEvenMsg[icaoaddr] = message
            t0 = 1
            t1 = 0

        if icaoaddr in self.lastOddMsg and icaoaddr in self.lastEvenMsg:

            # If CPR cannot be decoded, the method returns (None, None)
            _lat, _lon = decoder.get_position(self.lastEvenMsg[icaoaddr], self.lastOddMsg[icaoaddr], t0, t1)

            if _lat and _lon:
                lat = _lat
                lon = _lon
                alt = decoder.get_alt(message) * self.FT_TO_M

                self.lastLatitude[icaoaddr] = lat
                self.lastLongitude[icaoaddr] = lon
                self.lastAltitude[icaoaddr] = alt

                return lat, lon, alt
            else:
                print bcolors.WARNING + "Warning: cannot decode position message" + bcolors.ENDC
                return None, None, None

        return None, None, None

#    def latlon2xy(self, lat, lon):
#        return coreutils.calc_distance(self.lat0, self.lon0, lat, lon)


class Sensor:

    SENSOR_TABLE = "adsb_sensors"

    def __init__(self, id, dbhost=None, dbuser=None, dbpass=None, dbname=None):

        self.dbhost = dbhost
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbname = dbname

        if dbname is None:
            self.dbname = "atn_sim"

        if dbpass is None:
            self.dbpass = "atn_sim"

        if dbuser is None:
            self.dbuser = "atn_sim"

        if dbhost is None:
            self.dbhost = "localhost"

        #
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0
        self.id = id

        #
        self.xpos = 0.0
        self.ypos = 0.0
        self.zpos = 0.0

        self.db = MySQLdb.connect(self.dbhost, self.dbuser, self.dbpass, self.dbname)

        self.update()

    def update(self, lat0=None, lon0=None, alt0=None):
        cursor = self.db.cursor()
        nrows = cursor.execute("SELECT latitude, longitude, altitude FROM %s WHERE id='%s'" % (self.SENSOR_TABLE, self.id))

        if nrows > 0:
            self.latitude, self.longitude, self.altitude = cursor.fetchone()

            if lat0 is not None and lon0 is not None and alt0 is not None:
                #self.xpos, self.ypos = self.latlon2xy(lat0, lon0)
                self.xpos, self.ypos, self.zpos = geoutils.geog2enu(self.latitude, self.longitude, self.altitude, lat0, lon0, alt0)
                return True

        return False

#    def latlon2xy(self, lat0, lon0):
#        return coreutils.calc_distance(lat0,lon0,self.latitude, self.longitude)

    def __str__(self):
        return "Sensor %s: (%s, %s, %s) - (%s, %s)" % (self.id, self.latitude, self.longitude, self.altitude, self.xpos, self.ypos)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == "__main__":
    server = MlatServer()
    server.start()