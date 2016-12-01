
import binascii
import ConfigParser
import math
import MySQLdb
import os
import time
import socket

from ..icea.icea_protocol import Icea
from ..asterix import asterix_utils

from ... import core_utils
from ... import emane_utils
from ... import geo_utils


# -----------------------------------------------------------------------------
# class Radar
# -----------------------------------------------------------------------------
class Radar:

    """
    This class emulates the functionality of the radar
    """

    M_TO_FT = 3.28084
    M_TO_NM = 0.000539957
    MPS_TO_KT = 1.94384
    DEG_SETOR = 11.25

    # PSR default values
    sweep_time = 4.0

    # Default values
    net_ip = "172.18.104.255"
    net_port = 65000
    net_mode = "broadcast"
    net_proto = "ICEA"

    db_name = 'atn_sim'
    db_user = 'atn_sim'
    db_pass = 'atn_sim'
    db_host = '172.17.255.254'

    net = "172.16.0.255"
    port = 20004


    # -------------------------------------------------------------------------
    # method constructor
    # -------------------------------------------------------------------------
    def __init__(self, config="radar.cfg"):
        """
        Initialize attributes of class
        """

        # Node name of radar in simulation
        self.nodename = core_utils.get_node_name()

        # Node number of radar in simulation
        self.nodenumber = core_utils.get_node_number()

        # Simulation ID
        self.session_id = core_utils.get_session_id()

        # NEM ID
        self.nemid = core_utils.get_nem_id(node_name=self.nodename, session_id=self.session_id)

        self.nodenames = {}
        self.nodenumbers = {}

        # Reading configuration file
        if os.path.exists(config):
            print "Configuration file %s found." % config
            conf = ConfigParser.ConfigParser()
            conf.read(config)

            self.latitude  = conf.getfloat("Location", "latitude")
            self.longitude = conf.getfloat("Location", "longitude")
            self.altitude  = conf.getfloat("Location", "altitude")

            # Radar parameters
            self.sweep_time = conf.getfloat("PSR", "sweep_time")

            # Network parameters
            self.net_ip    = conf.get("Network", "destination")
            self.net_port  = conf.getint("Network", "port")
            self.net_mode  = conf.get("Network", "mode")
            self.net_proto = conf.get("Network", "protocol")

            # Placing radar on the proper location
            # set_location(nemid, lat, lon, alt, heading, speed, climb)
            emane_utils.set_location(nemid=self.nemid, lat=self.latitude, lon=self.longitude, alt=self.altitude,
                                     heading=0.0, speed=0.0, climb=0.0)
        else:
            location = emane_utils.get_nem_location(nem_id=self.nemid)

            self.latitude = location["latitude"]
            self.longitude = location["longitude"]
            self.altitude = location["altitude"]

        if self.net_proto == "ICEA":
            self.encoder = Icea()

            # Pre-calculating for speed
            self.empty_msg = {}
            for sector in range(0, 32):
                self.empty_msg[sector] = self.encoder.get_empty_sector_msg(sector)
        elif self.net_proto == "ASTERIX":
            pass
        else:
            print "Radar protocol %s is not supported." % self.net_proto
            self.encoder = None

        # DB connection with general purposes
        self.db = MySQLdb.connect(self.db_host, self.db_user, self.db_pass, self.db_name)

        # DB connection specific for thread _process_msg()
        self.db_process = MySQLdb.connect(self.db_host, self.db_user, self.db_pass, self.db_name)

        print "Location of Radar:"
        print "  Latitude:  %f" % self.latitude
        print "  Longitude: %f" % self.longitude
        print "  Altitude:  %f m" % self.altitude
        print "Network settings:"
        print "  Destination:  %s" % self.net_ip
        print "  Port:         %s" % self.net_port
        print "  Mode:         %s" % self.net_mode
        print "  Radar Proto.: %s" % self.net_proto

        # sock (socket):  The end point to send ASTERIX CAT 21.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


    # -------------------------------------------------------------------------
    # method start
    # -------------------------------------------------------------------------
    def start(self):
        """method start

        This method has the cyclic function 4/2 for aircraft that are within
        the radar coverage and send in broadcast mode (UDP) network
        """

        while True:

            t0 = time.time()

            if self.net_proto == "ASTERIX":

                # ToDo: must call detect for each sector, otherwise there will be delays on detected track
                tracks = self.detect()
                tp = time.time()

                for s in range(0, 32):

                    send_n = False
                    if s == 25:
                        send_n = True

                    self.broadcast_asterix(tracks, s, send_n)

                dtp = time.time() - tp

                time.sleep(4.0 - dtp)
            elif self.net_proto == "ICEA":
                tracks = self.detect()
                self.broadcast_icea(tracks)

                time.sleep(self.sweep_time - (time.time() - t0))

            print "Objects detected: %d" % len(tracks)
            for t in tracks:
                print "  > %s: %f %f %f %f %f %s" % (t[7], t[1], t[2], t[3], t[4], t[5], t[8])

            dt = time.time() - t0
            print "Complete rotation in %f sec" % dt





    # -------------------------------------------------------------------------
    # method detect - aircraft(s) on the sector actual
    # -------------------------------------------------------------------------
    def detect(self):
        """method detect

        This method  has the function of detecting  moving objects within CORE,
        apply detection filters (horizontal and vertical) and finally generate
        a list of targets that are within the radar coverage.
        """

        detected_tracks = []

        for i in emane_utils.get_all_locations():

            nemid = i["nem"]
            lat = i["latitude"]
            lon = i["longitude"]
            alt = i["altitude"]

            if nemid not in self.nodenames:
                self.nodenames[nemid] = core_utils.get_node_name(nem_id=nemid, session_id=self.session_id)
                self.nodenumbers[nemid] = core_utils.get_node_number(node_name=self.nodenames[nemid],
                                                                     session_id=self.session_id)

            nodenum = self.nodenumbers[nemid]

            # Prevent radar to detect itself
            if nodenum == self.nodenumber:
                continue

            x, y = self.calc_distance_from(lat, lon, alt)

            z = float(alt)

            # (azimuth, elevation, magnitude) = core_utils.get_node_velocity(nemid)

            azimuth = i["azimuth"]
            elevation = i["elevation"]
            magnitude = i["magnitude"]

            # Climb rate (in m/s)
            climb_rate = float(magnitude) * math.sin(math.radians(float(elevation)))

            # Speed (in m/s)
            speed = float(magnitude) * math.cos(math.radians(float(elevation)))

            # SSR and Callsign
            callsign, ssr = self.read_transponder(nemid)

            # Sector
            h_angle = RadarUtils.calc_horizontal_angle(x, y, z)

            sector = int(h_angle / self.DEG_SETOR)

            # ToDo: how to encode primary radar plots?
            if callsign is not None and ssr is not None:
                detected_tracks.append([nodenum,
                                        x * self.M_TO_NM,
                                        y * self.M_TO_NM,
                                        z * self.M_TO_FT,
                                        azimuth,
                                        speed * self.MPS_TO_KT,
                                        ssr,
                                        callsign,
                                        sector,
                                        h_angle,
                                        ])

        return detected_tracks

    def read_transponder(self, nemid):
        #
        # Read transponder's parameters using database shared memory
        #
        # ToDo: read this information from aircraft transponder
        try:
            cursor = self.db_process.cursor()
            cursor.execute("SELECT callsign, performance_type, ssr_squawk FROM transponder WHERE nem_id=%d" % nemid)
            result = cursor.fetchone()

            if result is not None:

                db_callsign = result[0]
                db_perftype = result[1]
                db_squawk = result[2]

                cursor.close()

                return db_callsign, db_squawk

        except MySQLdb.Error, e:
            print "read_transponder(): MySQL Error [%d]: %s" % (e.args[0], e.args[1])

        return None, None

    def broadcast_asterix(self, tracks, sector, north_flag=False):

        sac = 232
        sic = 10
        tod = time.time()

        sector_record = {
            444: {'MsgTyp': 2},
            10: {'SAC': sac, 'SIC': sic},
            20: {'Azi': (sector * 11.25)},
            30: {'ToD': tod}
        }

        north_record = {
            444: {'MsgTyp': 2},
            10: {'SAC': sac, 'SIC': sic},
            30: {'ToD': (tod+0.867)},
            41: {'RotS': 4},
            # 50: {'COM_presence': 1, 'PSR_presence': 1, 'MDS_presence': 1, 'fx': 0,
            #      # COM
            #      'NOGO': 0, 'RDPC': 0, 'RDPR': 0, 'OVL RDP COM': 0, 'OVL XMT': 0, 'MSC COM': 0, 'TSV': 0,
            #      # PSR
            #      'ANT PSR': 0, 'CHAB PSR': 3, 'OVL': 0, 'OVL RDP': 0, 'MSC PSR': 0,
            #      # MDS
            #      'ANT': 0, 'CHAB': 1, 'OVL_SUR': 0, 'MSC': 0, 'SCF': 0, 'DLF': 0, 'OVL SCF': 0, 'OVL DLF': 0,
            #      }

        }

        # 0: nodenum,
        # 1: x * self.M_TO_NM,
        # 2: y * self.M_TO_NM,
        # 3: z * self.M_TO_FT,
        # 4: azimuth,
        # 5: speed * self.MPS_TO_KT,
        # 6: ssr,
        # 7: callsign,
        # 8: sector
        # 9: theta (h_angle)

        detected_tracks = []

        for t in tracks:

            if t[8] != sector:
                continue

            dist = math.sqrt(t[1]*t[1] + t[2]*t[2] + t[3]*t[3])  # Distance from radar (3D)
            dist2d = math.sqrt(t[1]*t[1] + t[2]*t[2])  # Distance from radar (2D)

            track_record = {
                10: {'SAC': sac, 'SIC': sic},
                140: {'ToD': tod},
                20: {'TYP': 3, 'SIM': 0, 'RDP': 0, 'SPI': 0, 'RAB': 0, 'FX': 1, 'TST': 0, 'ME': 0, 'MI': 0, 'FOEFRI': 0, 'FX2': 0},
                40: {'RHO': dist2d, 'THETA': t[9]},
                70: {'V': 0, 'G': 0, 'L': 0, 'Mode3A': int(t[6], 8)},
                90: {'V': 0, 'G': 0, 'FL': (t[3]/100)},
                161: {'Tn': t[0]},
                200: {'CGS': t[5], 'CHdg': t[4]},
                170: {'CNF': 0, 'RAD': 0, 'DOU': 0, 'MAH': 0, 'CDM': 0, 'FX': 1, 'TRE': 0, 'GHO': 0, 'SUP': 0, 'TCC': 0, 'FX2': 0}
            }

            detected_tracks.append(track_record)

        if len(detected_tracks) > 0:
            sector_record = {48: detected_tracks, 34: [sector_record]}
        else:
            sector_record = {34: [sector_record]}

        north_record = {34: [north_record]}

        # encoded_sector = self.asterix_encode(sector_record)
        # encoded_north = self.asterix_encode(north_record)

        # self.net_send(encoded_sector)
        self.transmit(sector_record)

        if north_flag:
            # self.net_send(encoded_north)
            # self.transmit(encoded_north)
            self.transmit(north_record)

    def asterix_encode(self, asterix_record):
        # Encoding data to ASTERIX format
        data_bin = asterix_utils.encode(asterix_record)
        return hex(data_bin).rstrip("L").lstrip("0x")

    def transmit(self, asterix_record):
        # Encoding data to ASTERIX format
        data_bin = asterix_utils.encode(asterix_record)
        # print ("%x" % data_bin)
        msg = hex(data_bin).rstrip("L").lstrip("0x")
        self.sock.sendto(binascii.unhexlify(msg), (self.net, self.port))
        print msg


    # -------------------------------------------------------------------------
    # method broadcast
    # -------------------------------------------------------------------------
    def broadcast_icea(self, tracks):
        """method broadcast

        This method sends first message empty sector network and seeks to identify
        the aircraft that are within the current sector, formats the messages from
        the aircraft to the icea protocol to be sent on the network.
        """

        # get aircraft(s) of sector actual
        messages = self.encoder.encode_icea(tracks)

        if messages is None:
            return

        for sector in range(0, 32):

            # send message empty sector
            self.net_send(self.empty_msg[sector])

            for i in range(0, len(messages)):

                # sectors iquals
                if tracks[i][-1] == sector:

                   # send message track
                   self.net_send(messages[i])


    # -------------------------------------------------------------------------
    # method calc_distance_from
    # -------------------------------------------------------------------------
    def calc_distance_from(self, lat, lon, alt):
        """method calc_distance_from

        This method calculates the distance of the aircraft on radar
        """

        x, y, z = geo_utils.geog2enu(float(lat), float(lon), float(alt), self.latitude, self.longitude, self.altitude)

        return x, y


    # -------------------------------------------------------------------------
    # method net_send
    # -------------------------------------------------------------------------
    def net_send(self, msg):
        """method net_send

        This method performs the post on the network in broadcast mode and udp
        """

        hex_msg = binascii.unhexlify(msg)

        # UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if self.net_mode == "broadcast":
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # send msg
        try:
            sock.sendto(hex_msg, (self.net_ip, self.net_port))
        except IOError, e:
            if e.errno == 101:
                #print "Network unreachable"
                pass
        finally:
            sock.close()


# -----------------------------------------------------------------------------
# class RadarUtils
# -----------------------------------------------------------------------------
class RadarUtils:

    DEG_PI_3 = 60.0           # PI / 3
    DEG_PI_2 = 90.0           # PI / 2
    DEG_PI = 180.0          # PI
    DEG_3PI_2 = 270.0          # 3 PI / 2
    DEG_2PI = 360.0          # 2 PI
    RAD_DEG = 57.29577951    # Converte RAD para DEG
    DEG_RAD = 0.017453292    # Converte DEG para RAD
    DEG_SETOR = 11.25

    @staticmethod
    def calc_horizontal_angle(x_pos, y_pos, z_pos = None):

        # calcula a nova radial (proa de demanda)
        if x_pos > 0:
            return 90.0 - math.degrees(math.atan(y_pos / x_pos))

        if x_pos < 0:
            angle_tmp = 270.0 - math.degrees(math.atan(y_pos / x_pos))

            if angle_tmp >= 360.0:
                return angle_tmp - 360.0
            else:
                return angle_tmp

        if y_pos >= 0:
            return 0
        else:
            return RadarUtils.DEG_PI

    @staticmethod
    def calc_vertical_angle(x_pos, y_pos, z_pos):
        if z_pos == 0.0:
            return 0.0

        if x_pos == 0.0:
            return 90.0

        v_angle = math.atan(z_pos / abs(x_pos))

        if z_pos < 0:
            return -v_angle

        return v_angle


if __name__ == '__main__':

    # session_id = core_utils.get_session_id()

    radar = Radar()
    radar.start()
