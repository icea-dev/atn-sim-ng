import ipcalc
import logging
import math
import netifaces as ni
import random
import sys
import socket
import threading
import time

import adsb_utils

from .feeds.coreemu_feed import CoreFeed


class AdsbOut:

    net_port = 30001
    net_iface = "eth0"

    log_file = "adsbout.log"
    log_level = logging.DEBUG

    # Constants
    EW_DIRECTION = 0
    NS_DIRECTION = 1
    VERTICAL_RATE_UP = 0
    VERTICAL_RATE_DOWN = 1
    MSG_SUBTYPE_1 = 1
    MSG_SUBTYPE_2 = 2

    def __init__(self, feed=None, nodename=None):

        self.nodename = nodename
        self.nemid = None

        self.last_position_msg = "ODD"

        self.net_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.net_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        if feed is None:
            self.feed = CoreFeed()

            # Initiate readings from gps device (latitude, longitude, altitude)
            # self.feed.gps_start()
            self.feed.tracksrv_start()

        else:
            self.feed = feed

        # Resolving broadcast address of primary interface
        ipaddr = ni.ifaddresses(self.net_iface)[2][0]['addr']
        netmask = ni.ifaddresses(self.net_iface)[2][0]['netmask']
        subnet = ipcalc.Network(ipaddr + "/" + netmask)

        self.net_dest = str(subnet.broadcast())

        # Logging
        logging.basicConfig(filename=self.log_file, level=self.log_level, filemode='w',
                            format='%(asctime)s %(levelname)s: %(message)s')
        self.logger = logging.getLogger("adsb.log")

    def start(self):
        print " > Initiating ADS-B Out transmission"
        t1 = threading.Thread(target=self._start_airborne_position, args=())
        t2 = threading.Thread(target=self._start_airborne_velocity, args=())
        t3 = threading.Thread(target=self._start_aircraft_id, args=())

        # Start broadcasting
        t1.start()  # Airborne position
        t2.start()  # Airborne velocity
        t3.start()  # Aircraft identification

    def _start_aircraft_id(self, rate=5):
        # Startup time
        time.sleep(random.randint(0, 5))

        while True:
            t0 = time.time()
            msg = self.generate_aircraft_id()
            self.broadcast(msg)
            self.logger.debug("AIRCRAFT ID:\t%s" % msg)

            dt = time.time() - t0
            time.sleep(rate - dt)

    def _start_airborne_position(self, rate=1.0):
        # Startup time
        time.sleep(random.randint(0, 5))

        while True:
            t0 = time.time()
            msg = self.generate_airborne_position()
            self.broadcast(msg)
            self.logger.debug("AIR POSITION:\t%s" % msg)

            dt = time.time() - t0
            time.sleep(rate - dt)

    def _start_airborne_velocity(self, rate=1.0):
        # Startup time
        time.sleep(random.randint(0, 5))

        while True:
            t0 = time.time()
            msg = self.generate_airborne_velocity()
            self.broadcast(msg)
            self.logger.debug("AIR VELOCITY:\t%s" % msg)

            dt = time.time() - t0
            time.sleep(rate - dt)

    def stop(self):
        pass

    def broadcast(self, message):
        if self.nodename is None:
            self.net_sock.sendto(message, (self.net_dest, self.net_port))
        else:
            self.net_sock.sendto(message + " " + self.nodename, (self.net_dest, self.net_port))

    def generate_aircraft_id(self):

        ca = self.feed.get_capabilities()
        callsign = self.feed.get_callsign()
        air_type = self.feed.get_type()
        icao24 = self.feed.get_icao24()

        if callsign is None:
            return None

        # Binary
        msg = adsb_utils.encode_aircraft_id(ca, icao24, air_type, callsign)

        # Hex
        hex_msg = hex(int(msg, 2)).rstrip("L").lstrip("0x")

        return hex_msg

    def generate_airborne_position(self):

        # Capabilities
        ca = self.feed.get_capabilities()

        # ME field = 9-18, 20-22 : airborne position
        me = 11

        # "Surveillance Status"
        #
        # Encode information from the aircraft's Mode-A transponder code as follows:
        #
        # 0 : No condition information
        # 1 : Permanent alert condition (emergency)
        # 2 : Temporary alert condition (change in Mode A Identity Code other than emergency condition)
        # 3 : Special position identification (SPI) condition
        #
        # Note: When not implemented in a Mode-S Transponder-Based system, the ADS-B function shall set
        # the "Surveillance Status" subfield to ZERO.
        sv = 0

        # SSR
        ssr = self.feed.get_ssr()

        # SPI
        spi = self.feed.get_spi()

        # ICAO 24
        icao24 = self.feed.get_icao24()

        # implementation of SSR
        # Emergency Codes (7500-hijack; 7600-failure on the radio; 7700 - emergency)
        if (ssr == "7500") or (ssr == "7600") or (ssr == "7700"):
            sv = 1

        # implementation of SPI
        if spi:
            sv = 3

        # NIC Supplement-B
        nicsb = 0

        # "TIME" (T)
        #
        # Indicates whether or not the epoch of validity for horizontal position data in an airborne position message is
        # an exact 0.2 UTC epoc. If the time of applicability of the position data is synchronized to an exact 0.2
        # second UTC epoch, the "TIME" (T) subfield shall be set to "1"; otherwise, the "TIME" (T) subfield shall be set
        # to ZERO (0).
        t_flag = 0

        lat, lon, alt_m = self.feed.get_position()

        if lat is None and lon is None and alt_m is None:
            lat = 0
            lon = 0
            alt_m = 0
            me = 0  # ME=0 : signalling error

        alt = alt_m * 3.28084  # meters to feet

        '''Altitude encoding'''

        # Encode altitude
        if alt < 50175:  # (2^11 -1)*25 - 1000 : 25 feet increment
            qbit = "1"
            enc_alt_int = int(round((alt+1000)/25.0))
        else:  # 100 feet increment
            qbit = "0"
            enc_alt_int = int(round((alt+1000)/100.0))

        enc_alt_bin = bin(enc_alt_int)[2:].zfill(11)               # binary string:
        enc_alt = int(enc_alt_bin[0:7]+qbit+enc_alt_bin[7:11], 2)  # Inserting qbit

        '''Lat/Lon CPR Encoding'''
        even_lat = lat
        even_lon = lon
        odd_lat = even_lat
        odd_lon = min(even_lon, 180)

        (evenenclat, evenenclon) = adsb_utils.cpr_encode(even_lat, even_lon, False, False)
        (oddenclat, oddenclon) = adsb_utils.cpr_encode(odd_lat, odd_lon, True, False)

        msg_even = adsb_utils.encode_airborne_position(ca, icao24, evenenclat, evenenclon, sv, nicsb, enc_alt, t_flag, 0, me)
        msg_odd = adsb_utils.encode_airborne_position(ca, icao24, oddenclat, oddenclon, sv, nicsb, enc_alt, t_flag, 1, me)

        # Alternating between even and odd messages
        if self.last_position_msg == "ODD":
            # Encoding EVEN message

            hex_msg_even = hex(int(msg_even, 2)).rstrip("L").lstrip("0x")
            message = hex_msg_even
            self.last_position_msg = "EVEN"
        else:
            # Encoding ODD message
            hex_msg_odd = hex(int(msg_odd, 2)).rstrip("L").lstrip("0x")
            message = hex_msg_odd
            self.last_position_msg = "ODD"

        return message

    def generate_airborne_velocity(self):
        """
        This method encodes the ADS-B Airbone Velocity Message and sends it to
        the network. There are two different types of message for velocities,
        determined by 3-bit subtype in the message. Only subtype 1 and 2,
        surface velocity (ground speed) is reported.

        Returns:
            A string with ADS-B Airbone Velocity Message encodes in hexadecimal.
        """

        (heading, vertical_rate, ground_speed) = self.feed.get_velocity()
        (heading_radians, vertical_rate, ground_speed) = adsb_utils.to_unit_adsb(heading, vertical_rate, ground_speed)

        # Intent Change Flag = 0, No Change in Intent
        ic_flag = 0

        # Reserved-A ZEROS
        reserved_a = 0

        # NACv (Navigate Accuracy Category for Velocity), determining NACv
        # based on position source declared horizontal velocity Error
        # 0 : Unknown or >= 10 m/s
        # 1 : < 10 m/s
        # 2 : < 3 m/s
        # 3 : < 1 m/s
        # 4 : < 0.3 m/s
        nacv = 0

        # East/West Velocity in knots
        # East/West Direction Bit: indicate the direction of the East/West
        # Velocity Vector
        # 0 : flying West to East
        # 1 : flying East to West
        (ew_dir, ewv) = self._calculate_velocity(heading_radians, AdsbOut.EW_DIRECTION, ground_speed)

        # North/South Velocity in knots
        # North/South Direction Bit: indicate the direction of the North/South
        # Velocity Error
        # 0 : flying South to North
        # 1 : flying North to South
        (ns_dir, nsv) = self._calculate_velocity(heading_radians, AdsbOut.NS_DIRECTION, ground_speed)

        # Vertical Rate Source: indicate the source of Vertical Rate information
        # as specified:
        # 0 : Vertical Rate information from Geometric Source (GNSS or INS)
        # 1 : Vertical Rate information from Barometric Source
        vrate_src = 1

        # Vertical rate Sign: indicate the direction of the Vertical rate as
        # specified:
        # 0 : Up
        # 1 : Down
        # If vrate < 0 the aircraift is going DOWN otherwise is going UP
        (vertical_rate_sign, vertical_rate) = self._calculate_vertical_rate(vertical_rate)

        # Reserved-B ZEROS
        reserved_b = 0

        # Difference From barometric Altitude Sign Bit: used to indicate the
        # direction of the GNSS Altitude Source data as specified:
        # 0 : Geometric (GNSS or INS) Altitude Source data is greater than
        #     (above) Barometric
        # 1 : Geometric (GNSS or INS) Altitude Source data is less than
        #     (below) Barometric
        h_sign = 0

        # Difference From Barometric Altitude: is used to report the difference
        # between Geometric (GNSS or INS) Altitude Source data and Barometric
        # Altitude when both types of Altitude Data are available and valid
        # 0 : No GNSS Altitude Source data Difference information available
        h_diff = 0

        # Supersonic Version of the Airborne Velocity Message
        # Subtype = 2 shall be used if either the East/West Velocity or the
        # North/South Velocity exceeds 1022 knots. A switch to the normal
        # velocity message (Subtype 1) shall be made if both the East/West
        # and the North/South Velocities drop below 1000 knots
        # es_subtype = self.get_msg_subtype(ewv, nsv)

        if (ewv - 1) >= 1022 or (nsv - 1) >= 1022:
            es_subtype = self.MSG_SUBTYPE_2
            ewv = int(round(abs(ewv / 2)))
            nsv = int(round(abs(nsv / 2)))
        else:
            es_subtype = self.MSG_SUBTYPE_1

        # Encodes the ADS-B Airborne Velocity Message
        msg = adsb_utils.encode_airborne_velocity(self.feed.get_capabilities(),
                                                  self.feed.get_icao24(), es_subtype, ic_flag, reserved_a, nacv, ew_dir,
                                                  ewv, ns_dir, nsv, vrate_src, vertical_rate_sign, vertical_rate,
                                                  reserved_b, h_sign, h_diff)

        hex_msg = hex(int(msg, 2)).rstrip("L").lstrip("0x")

        return hex_msg

    def _calculate_velocity(self, radians, direction, ground_speed):
        """Calculate the direction and ground speed component

        Args:
            radians (float): The heading of airborne in radians.
            direction (int): Indicate the direction of velocity. 0 or 1.
            ground_speed (float): The ground speed of airbone in knots (kt).

        Returns:
            Returns the direction of velocity vector and velocity.

        """
        RAD_360 = 2 * math.pi
        RAD_90 = math.pi / 2.0
        RAD_180 = math.pi
        RAD_270 = 3.0 * math.pi / 2.0

        direction_velocity = 0

        # Check the direction of the ground speed module
        if direction == AdsbOut.EW_DIRECTION:
            velocity = math.sin(radians) * ground_speed
            # Calculate the e/w direction
            if radians > RAD_180 and radians <= RAD_360:
                direction_velocity = 1
        elif direction == AdsbOut.NS_DIRECTION:
            velocity = math.cos(radians) * ground_speed
            # Calculate the n/s direction
            if radians > RAD_90 and radians <= RAD_270:
                direction_velocity = 1
        else:
            return None

        # Velocity to be sent
        velocity_module = int(round(abs(math.fabs(velocity) + 1.0)))

        return direction_velocity, velocity_module

    def _calculate_vertical_rate(self, vertical_rate):
        """Calculate the direction of the vertical rate and your module.

        Args:
            vertical_rate (float) : The vertical rate in ft/min.

        Returns:
            The direction of the vertical rate (0 : UP, 1 :DOWN) and vertical
            rate module.

        """
        sign = AdsbOut.VERTICAL_RATE_UP
        if vertical_rate < 0.0:
            sign = AdsbOut.VERTICAL_RATE_DOWN

        return sign, int(round(abs(math.fabs(vertical_rate))))

if __name__ == '__main__':

    time.sleep(3)

    name = None
    if len(sys.argv) > 1:
        name = sys.argv[1]

    transponder = AdsbOut(nodename=name)
    transponder.start()
