import ConfigParser
import logging
import MySQLdb
import netifaces as ni
import os
import threading
import time

import core_utils
import emane_utils

from .network import mcast_socket

from emanesh.events import EventService
from emanesh.events import LocationEvent

from collections import deque


class TrackServer:

    update_interval = 1.0

    log_file = "track_server.log"
    log_level = logging.DEBUG

    net_tracks = "235.12.2.4"
    net_iface = "ctrl0"

    db_name = 'atn_sim'
    db_user = 'atn_sim'
    db_pass = 'atn_sim'
    db_host = '172.17.255.254'

    tracks = {}

    def __init__(self, config="track_server.cfg"):

        # Logging
        logging.basicConfig(filename=self.log_file, level=self.log_level, filemode='w',
                            format='%(asctime)s %(levelname)s: %(message)s')

        self.logger = logging.getLogger("trackserver")

        # Configuration file
        self.config = None

        if os.path.exists(config):
            self.config = ConfigParser.ConfigParser()
            self.config.read(config)

            if self.config.has_option("Database", "db_user"):
                self.db_user = self.config.get("Database", "db_user")

            if self.config.has_option("Database", "db_pass"):
                self.db_pass = self.config.get("Database", "db_pass")

            if self.config.has_option("Database", "db_host"):
                self.db_host = self.config.get("Database", "db_host")

            if self.config.has_option("Database", "db_name"):
                self.db_name = self.config.get("Database", "db_name")

        # DB connection with general purposes
        self.db = MySQLdb.connect(self.db_host, self.db_user, self.db_pass, self.db_name)

        # DB connection specific for thread _process_msg()
        self.db_process = MySQLdb.connect(self.db_host, self.db_user, self.db_pass, self.db_name)

        # DB connection specific for thread _update()
        self.db_update = MySQLdb.connect(self.db_host, self.db_user, self.db_pass, self.db_name)

        # Emane service
        self.service = EventService(('224.1.2.8', 45703, self.net_iface))

        # Queue of unprocessed messages from track generator
        self.msg_queue = deque([])

        # List of NEMs available in the simulation
        self.nems = []

    def start(self):

        self.logger.info("Initiating server")

        self._init_nodes_table()
        self._init_nems_table()
        self._init_mapings()

        # t1 = threading.Thread(target=self._update_from_emane, args=())
        t1 = threading.Thread(target=self._update_from_tracks, args=())
        t2 = threading.Thread(target=self.listen, args=())
        t3 = threading.Thread(target=self._process_queue, args=())

        t1.start()
        t2.start()
        t3.start()

        self.db.close()

    def stop(self):
        pass

    def listen(self):

        # Retrieving list of nodes
        nodes = emane_utils.get_all_locations()

        for n in nodes:
            self.nems.append(n["nem"])

        if len(nodes) == 0:
            self.logger.error("Cannot read nodes' positions from Emane")

        # IP address of incoming messages
        ip = ni.ifaddresses(self.net_iface)[2][0]['addr']

        sock = mcast_socket.McastSocket(local_port=1970, reuse=True)
        sock.mcast_add(self.net_tracks, ip)

        self.logger.info("Waiting for track messages on %s:%d" % (self.net_tracks, 1970))

        while True:
            data, sender_addr = sock.recvfrom(1024)

            # Inserting received messages in the queue
            self.msg_queue.append(data)

    def _process_queue(self):

        while True:
            if len(self.msg_queue) == 0:
                time.sleep(0.5)
                continue
            else:
                self._process_msg(self.msg_queue.popleft())

    def _process_msg(self, data):

        FT_TO_M = 0.3048
        KT_TO_MPS = 0.51444444444

        message = data.split("#")

        # ex: 101#114#1#7003#-1#4656.1#-16.48614#-47.947058#210.8#9.7#353.9#TAM6543#B737#21653.3006492
        msg_ver = int(message[0])
        msg_typ = int(message[1])

        if msg_typ != 114:
            return

        msg_num = int(message[2])  # node id
        msg_ssr = message[3]
        msg_spi = int(message[4])  # if spi > 0, SPI=ON, otherwise SPI=OFF
        msg_alt = float(message[5])  # altitude (feet)
        msg_lat = float(message[6])  # latitude (degrees)
        msg_lon = float(message[7])  # longitude (degrees)
        msg_vel = float(message[8])  # velocity (knots)
        msg_cbr = float(message[9])  # climb rate (m/s)
        msg_azm = float(message[10])  # azimuth (degrees)
        msg_csg = message[11]  # callsign
        msg_per = message[12]  # aircraft performance type
        msg_tim = float(message[13])  # timestamp (see "hora de inicio")

        if msg_num in self.track2nem:
            nemid = self.track2nem[msg_num]
        else:
            nemid = msg_num

        if nemid not in self.nems:
            # Current track does not exists in the simulation
            return

        #
        # Update node's physical parameters using Emane API
        #
        event = LocationEvent()
        event.append(nemid, latitude=msg_lat, longitude=msg_lon, altitude=msg_alt * FT_TO_M, azimuth=msg_azm,
                     magnitude=msg_vel * KT_TO_MPS, elevation=0.0)

        self.service.publish(0, event)

        #
        # Update local variables
        #
        obj = {
            'latitude': msg_lat,
            'longitude': msg_lon,
            'altitude': msg_alt * FT_TO_M,
            'pitch': 0.0,
            'roll': 0.0,
            'yaw': 0.0,
            'azimuth': msg_azm,
            'elevation': 0.0,
            'magnitude': msg_vel * KT_TO_MPS,
        }

        self.tracks[nemid] = obj

        #
        # Update transponder's parameters using database shared memory
        #

        try:
            cursor = self.db_process.cursor()
            cursor.execute("SELECT callsign, performance_type, ssr_squawk FROM transponder WHERE nem_id=%d" % nemid)
            result = cursor.fetchone()

            if result is None:
                print "SELECT callsign, performance_type, ssr_squawk FROM transponder WHERE nem_id=%d" % nemid
                return

            db_callsign = result[0]
            db_perftype = result[1]
            db_squawk = result[2]

            if db_callsign[0] != msg_csg or db_perftype != msg_per or db_squawk != msg_ssr:
                sql = "UPDATE transponder SET callsign='%s', performance_type='%s', ssr_squawk='%s' " \
                      "WHERE nem_id=%d" % (msg_csg, msg_per, msg_ssr, nemid)

                cursor.execute(sql)
                self.db_process.commit()

            cursor.close()

        except MySQLdb.Error, e:
            print "listen(): MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            logging.warn("listen(): MySQL Error [%d]: %s" % (e.args[0], e.args[1]))

    def _update_from_emane(self):

        self.logger.info("Initializing EMANE readings...")

        while True:
            t0 = time.time()

            # Trecho com problemas
            self.logger.debug("Requesting locations from EMANE")

            nodes = emane_utils.get_all_locations()

            self.logger.debug("EMANE responded in %f secs " % (time.time() - t0) )

            for n in nodes:
                cursor = self.db_update.cursor()

                try:
                    sql = "UPDATE nem set latitude=%f, longitude=%f, altitude=%f, pitch=%f, roll=%f, yaw=%f, " \
                          "azimuth=%f, elevation=%f, magnitude=%f,  last_update=now() WHERE id=%d" \
                          % (n['latitude'], n['longitude'], n['altitude'], n['pitch'], n['roll'], n['yaw'],
                             n['azimuth'], n['elevation'], n['magnitude'], n['nem'])

                    cursor.execute(sql)

                    self.db_update.commit()

                    cursor.close()

                    dt = time.time() - t0

                    # Logging
                    # self.logger.info("Tables updated successfully. Processing time: %f s" % dt)
                    if dt > self.update_interval:
                        self.logger.warning("Position updates is taking longer than %f s" % self.update_interval)
                except MySQLdb.Error, e:

                    self.logger.error("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))

                    time.sleep(0.5)
                    continue

            dt = time.time() - t0

            if self.update_interval - dt > 0:
                time.sleep(self.update_interval - dt)

    def _update_from_tracks(self):

        self.logger.info("Initializing PTRACKS readings...")

        while True:
            t0 = time.time()

            self.logger.debug("Reading cached locations from PTRACKS")

            for nem in self.nems:
                cursor = self.db_update.cursor()

                # Checks if
                if nem not in self.tracks:
                    continue

                try:
                    sql = "UPDATE nem set latitude=%f, longitude=%f, altitude=%f, pitch=%f, roll=%f, yaw=%f, " \
                          "azimuth=%f, elevation=%f, magnitude=%f,  last_update=now() WHERE id=%d" \
                          % (self.tracks[nem]['latitude'], self.tracks[nem]['longitude'], self.tracks[nem]['altitude'],
                             self.tracks[nem]['pitch'], self.tracks[nem]['roll'], self.tracks[nem]['yaw'],
                             self.tracks[nem]['azimuth'], self.tracks[nem]['elevation'], self.tracks[nem]['magnitude'],
                             nem)

                    print sql
                    cursor.execute(sql)

                    self.db_update.commit()

                    cursor.close()

                    dt = time.time() - t0

                    # Logging
                    # self.logger.info("Tables updated successfully. Processing time: %f s" % dt)
                    if dt > self.update_interval:
                        self.logger.warning("Position updates is taking longer than %f s" % self.update_interval)
                except MySQLdb.Error, e:

                    self.logger.error("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))

                    time.sleep(0.5)
                    continue

            dt = time.time() - t0

            if self.update_interval - dt > 0:
                time.sleep(self.update_interval - dt)

    def _init_nodes_table(self):

        logging.info("Initiating table NODE")

        session = int(core_utils.get_session_id())
        node_number, node_name = core_utils.get_node_list()

        cursor = self.db.cursor()

        # Clean table
        cursor.execute("DELETE FROM node")

        for n in range(0, len(node_number)):
            sql = "INSERT INTO node (id, name, session) VALUES (%d, '%s', %d)" % (node_number[n], node_name[n], session)
            cursor.execute(sql)

        self.db.commit()

        cursor.close()

    def _init_nems_table(self):

        logging.info("Initiating table NEM")

        node_names, node_devs, nemids = core_utils.get_nem_list()

        cursor = self.db.cursor()

        sql = "DELETE FROM nem"
        cursor.execute(sql)
        logging.debug(sql)

        for n in range(0, len(node_names)):
            sql = "INSERT INTO nem (id, node_id, iface) VALUES (%d, (SELECT id FROM node WHERE name='%s'), '%s' )" % (nemids[n], node_names[n], node_devs[n])
            cursor.execute(sql)
            logging.debug(sql)

        self.db.commit()
        cursor.close()

    def _init_mapings(self):

        self.track2nem = {}
        self.nem2track = {}

        if self.config is None:
            return

        data = self.config.items("Tracks")

        for i in range(0, len(data)):
            nodename = data[i][0]
            tracknumber = data[i][1]

            # node number
            sql = "SELECT a.id, b.id FROM node a, nem b WHERE a.name='%s' and a.id=b.node_id" % nodename
            cursor = self.db.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()

            if result is not None:
                nodenumber = result[0]
                nemid = result[1]

                self.track2nem[int(tracknumber)] = nemid
                self.nem2track[nemid] = int(tracknumber)

if __name__ == '__main__':
    t = TrackServer()
    t.start()
