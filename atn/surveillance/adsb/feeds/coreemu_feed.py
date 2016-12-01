import binascii
import logging
import MySQLdb
import os
import random
import time
import threading

from gps3 import gps3

from .adsb_feed import AdsbFeed

from atn import core_utils
from atn import emane_utils


class CoreFeed(AdsbFeed):

    log_file = "core_feed.log"
    log_level = logging.DEBUG

    gps_latitude = 0
    gps_longitude = 0
    gps_altitude = 0
    gps_track = 0
    gps_speed = 0
    gps_climb = 0
    gps_time = 0

    emane_latitude = 0
    emane_longitude = 0
    emane_altitude = 0
    emane_track = 0
    emane_speed = 0
    emane_climb = 0

    tracksrv_latitude = 0
    tracksrv_longitude = 0
    tracksrv_altitude = 0
    tracksrv_track = 0
    tracksrv_speed = 0
    tracksrv_climb = 0

    tracksrv_dbname = "atn_sim"
    tracksrv_dbuser = "atn_sim"
    tracksrv_dbpass = "atn_sim"
    tracksrv_dbhost = "172.17.255.254"

    nem_id = None
    node_name = None
    node_number = None
    session_id = None

    callsign = None
    icao24 = None

    def __init__(self):
        # Logging
        logging.basicConfig(filename=self.log_file, level=self.log_level, filemode='w',
                            format='%(asctime)s %(levelname)s: %(message)s')

        self.logger = logging.getLogger("coreemu_feed")

        self.session_id = core_utils.get_session_id()
        self.node_name = core_utils.get_node_name()
        self.nem_id = core_utils.get_nem_id(node_name=self.node_name, session_id=self.session_id)
        self.node_number = core_utils.get_node_number(node_name=self.node_name, session_id=self.session_id)

        self.db = MySQLdb.connect(self.tracksrv_dbhost, self.tracksrv_dbuser, self.tracksrv_dbpass, self.tracksrv_dbname)

        self._init_transponder()

    def _init_transponder(self):
        # ssr_beacon
        # ssr_squawk
        ssr_ident = False
        self.callsign = 'TAM%04d' % random.randint(0, 9999)
        self.icao24 = binascii.b2a_hex(os.urandom(3))

        cursor = self.db.cursor()
        cursor.execute("DELETE FROM transponder WHERE nem_id=%d" % self.nem_id)
        sql = "INSERT INTO transponder (nem_id, ssr_ident, callsign, icao24) VALUES (%d, %s, '%s', '%s')" % (self.nem_id, ssr_ident, self.callsign, self.icao24)
        cursor.execute(sql)

        self.db.commit()
        cursor.close()

    def get_position(self):
        # return self.gps_latitude, self.gps_longitude, self.gps_altitude
        return self.tracksrv_latitude, self.tracksrv_longitude, self.tracksrv_altitude

    def get_velocity(self):
        # return 45, 0, 100
        # azimuth, climb_rate, and speed
        return self.tracksrv_track, self.tracksrv_climb, self.tracksrv_speed

    def get_spi(self):
        return 0

    def get_ssr(self):
        return 0

    def get_callsign(self):
        return self.callsign

    def get_icao24(self):
        return self.icao24

    def get_capabilities(self):
        return 5

    def get_type(self):
        return 0

    def gps_start(self):
        t1 = threading.Thread(target=self.gps_read, args=())
        t1.start()

    def tracksrv_start(self):
        t1 = threading.Thread(target=self.tracksrv_read, args=())
        t1.start()

    def gps_read(self):
        gps_socket = gps3.GPSDSocket()
        data_stream = gps3.DataStream()
        gps_socket.connect()
        gps_socket.watch()

        for new_data in gps_socket:
            if new_data:
                data_stream.unpack(new_data)

                # Reading data from GPS stream
                lat = data_stream.TPV['lat']
                lon = data_stream.TPV['lon']
                alt = data_stream.TPV['alt']
                track = data_stream.TPV['track']
                speed = data_stream.TPV['speed']
                climb = data_stream.TPV['climb']
                time = data_stream.TPV['time']

                # Sanitizing location
                if lat == 'n/a' and lon == 'n/a' and alt == 'n/a':
                    self.gps_latitude = None
                    self.gps_longitude = None
                    self.gps_altitude = None
                else:
                    self.gps_latitude = lat
                    self.gps_longitude = lon
                    self.gps_altitude = alt

                # Sanitizing velocity
                if track == 'n/a' and speed == 'n/a' and climb == 'n/a':
                    self.gps_track = None
                    self.gps_speed = None
                    self.gps_climb = None
                else:
                    self.gps_track = track
                    self.gps_speed = speed
                    self.gps_climb = climb

                if time == 'n/a':
                    gps_time = None
                else:
                    gps_time = time

    def tracksrv_read(self):

        while True:

            cursor = self.db.cursor()
            query = "SELECT A.latitude, A.longitude, A.altitude, A.azimuth, A.magnitude, A.elevation, B.callsign," \
                    " B.icao24 FROM nem A, transponder B WHERE A.id=%d and A.id = B.nem_id" % self.nem_id
            try:
                cursor.execute(query)

                result = cursor.fetchone()

                lat = result[0]
                lon = result[1]
                alt = result[2]
                track = result[3]
                speed = result[4]
                climb = result[5]
                callsign = result[6]
                icao24 = result[7]

                self.tracksrv_latitude = lat
                self.tracksrv_longitude = lon
                self.tracksrv_altitude = alt
                self.tracksrv_track = track
                self.tracksrv_speed = speed
                self.tracksrv_climb = climb
                self.callsign = callsign
                self.icao24 = icao24

                cursor.close()
            except MySQLdb.Error as e:
                self.logger.error("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
            finally:
                cursor.close()

            time.sleep(0.5)
