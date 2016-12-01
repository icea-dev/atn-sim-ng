import math
import MySQLdb
import time

from adsb_fwrd import AdsbForwarder

import atn.geo_utils
import atn.emane_utils
import atn.core_utils


class DatabseForwarder(AdsbForwarder):

    LIGHT_SPEED = 299792458  # meters per second

    def __init__(self, sensor_id, verbose=False, items=None):

        self.debug = True
        self.id = sensor_id

        if items is not None:
            self.dbname = items["dbname"]
            self.dbpass = items["dbpass"]
            self.dbuser = items["dbuser"]
            self.dbhost = items["server"]
        else:
            self.dbname = "atn_sim"
            self.dbpass = "atn_sim"
            self.dbuser = "atn_sim"
            self.dbhost = "172.17.255.254"

        self.db = MySQLdb.connect(self.dbhost, self.dbuser, self.dbpass, self.dbname)
        self.cursor = self.db.cursor()

        # Update sensor's information on database
        self.nem = atn.core_utils.get_nem_id()
        currpos = atn.emane_utils.get_nem_location(self.nem)
        lat = currpos['latitude']
        lon = currpos['longitude']
        alt = currpos['altitude']

        self.cursor.execute("DELETE FROM adsb_sensors WHERE id='%s'" % self.id)
        self.cursor.execute("INSERT INTO adsb_sensors(id,latitude,longitude, altitude, last_update) VALUES('%s',%s,%s,%s,now() )" % (self.id, lat, lon, alt))
        self.db.commit()
        '''
        (lat, lon, alt) = coreutils.get_node_location(nem_id=self.nemid)

        self.cursor.execute("DELETE FROM sensors WHERE id='%s'" % self.sensor_id)
        self.cursor.execute("INSERT INTO sensors(id,latitude,longitude, altitude, last_update) VALUES('%s',%s,%s,%s,now() )" % (self.sensor_id, lat, lon, alt))
        self.db.commit()
        '''

    def __str__(self):
        return "MYSQL IP...: " + self.dbhost + ":" + self.dbname

    def forward(self, message, time_of_arrival, tx_id=None, rx_id=None):

        if tx_id is None and rx_id is None:
            t = time_of_arrival
            rx_id = self.id
        else:
            # Calculate accurate propagation time
            t = self.toa(tx_id, rx_id)

        if t is not None:
            sql1 = "INSERT INTO adsb_messages(id, message, sensor_id, toa, created) VALUES (0, '%s', '%s', %.20f, now())" % (message, rx_id, t)

            self.cursor.execute(sql1)
            self.db.commit()

    def toa(self, tx_id, rx_id):
        t0 = time.time()

        try:
            cursor = self.db.cursor()

            # Location of transmitter
            query = "SELECT latitude, longitude, altitude FROM nem WHERE node_id=(SELECT id FROM node WHERE name='%s')" % tx_id
            cursor.execute(query)
            result_tx = cursor.fetchone()

            if result_tx is None:
                print query
                return -1

            lat_tx, lon_tx, alt_tx = result_tx

            # Location of receiver
            query = "SELECT latitude, longitude, altitude FROM nem WHERE node_id=(SELECT id FROM node WHERE name='%s')" % rx_id
            cursor.execute(query)
            result_rx = cursor.fetchone()

            if result_rx is None:
                print query
                return -1

            lat_rx, lon_rx, alt_rx = result_rx

            cursor.close()

            # propagation time
            pt = self.calc_propagation_time(lat_tx, lon_tx, alt_tx, lat_rx, lon_rx, alt_rx)

            # print lat_tx, lat_rx
            dt = time.time() - t0

            return pt
        except MySQLdb.Error, e:
            print "listen(): MySQL Error [%d]: %s" % (e.args[0], e.args[1])

        return None

    def calc_propagation_time(self, lat_tx, lon_tx, alt_tx, lat_rx, lon_rx, alt_rx):
        """ Calculates the propagation time of a signal from nemid to current receiver.
        """
        (x, y, z) = atn.geo_utils.geog2enu(lat_tx, lon_tx, alt_tx, lat_rx, lon_rx, alt_rx)

        # Distance (in meters)
        dist_3d = math.sqrt(x * x + y * y + z * z)

        # Time of arrival calculation (seconds)
        t = dist_3d / self.LIGHT_SPEED

        # return t, x, y, z
        return t

