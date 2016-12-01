"""@package aircraft_data
"""
__author__ = "Ivan Matias"
__date__ = "2016/03"


class AircraftData(object):
    """
    This class provides position, identity and potentially additional information for a aircraft.
    """

    ## NACp [int]: Navigational Uncertainty Categories for Position. 8 = EPU < 92.6 m.
    NACp = 8

    ## NACv [int]: Navigational Uncertainty Categories fo Velocity, 1 = HFOMR < 10 m/s.
    NACv = 1
    ## SAC [int]: The System Code Area for Brazil.
    SAC = 232


    def __init__(self, sic):
        """The constructor.

        Args:
            sic (int): The system code identification of surveillance sensor.

        """
        ## sic [int]: The System Identification Code of surveillance sensor.
        self.sic = sic

        ## spi [int]: The Special Position Identificon (1 Presence, 0 Absence).
        self.spi = 0

        ## altitude [int]: The altitude from barometric measurements, not QNH corrected.
        self.altitude = 0

        ## latitude [int]: The latitude in WGS-84.
        self.latitude = 0

        ## longitude [int]: The longitude in WGS-84.
        self.longitude = 0

        ## callsign [string]: The aircraft identification in 8 characters.
        self.callsign = ''

        ## ground_speed [int]: The ground speed in knots.
        self.ground_speed = 0

        ## heading [int]: The heading of the aircraft in degrees.
        self.heading = 0

        ## vertical_rate [int]: The barometric vertical rate in feet/minute.
        self.vertical_rate = 0

        ## time_of_day [int]: Time of applicability in seconds, in the form of elapsed time since last midnight.
        self.time_of_day = 0

        ## even_msg [string]: The ADS-B even message.
        self.even_msg = None

        ## odd_msg [string]: The ADS-B odd message.
        self.odd_msg = None

        ## oldUpdateTime [int]: The update time.
        self.oldUpdateTime = 0


    def set_callsign(self, callsign):
        """Sets callsign of the aircraft.

        Args:
            callsign (string): The aircraft identification.

        """
        self.callsign = callsign


    def callsign_to_bcd(self):
        """Transform the callsign in BCD code.

        Returns:
            int: BCD code.

        """
        ais_charcode = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9, "J": 10, "K": 11,
                    "L": 12, "M": 13, "N": 14, "O": 15, "P": 16, "Q": 17, "R": 18, "S": 19, "T": 20, "U": 21,
                    "V": 22, "W": 23, "X": 24, "Y": 25, "Z": 26, " ": 32, "0": 48, "1": 49, "2": 50, "3": 51,
                    "4": 52, "5": 53, "6": 54, "7": 55, "8": 56, "9": 57}

        n = len(self.callsign)

        # Putting all to uppercase, just in case
        callsign = str(self.callsign).upper()

        msg = ""

        for i in range(0, n):
            # Callsign Character (6 bits) BDS code
            msg += bin(ais_charcode[callsign[i]])[2:].zfill(6)

        # Complete with blank spaces tha remaining bits
        if 8 - n > 0:
            for i in range(n, 8):
                msg += bin(ais_charcode[" "])[2:].zfill(6)

        return int(msg, 2)


    def set_altitude(self, altitude):
        """Sets the altitude of aircraft in feet.

        Args:
            altitude (int): The altitude in feet.

        """
        self.altitude = altitude


    def set_position(self, latitude, longitude):
        """Sets the geographic coordinate of aircraft.

        Args:
            latitude (int): The latitude value in degrees.
            longitude (int): The longitude value in degrees.
        @return:
        """
        self.latitude = latitude
        self.longitude = longitude


    def set_time_of_day(self, time_of_day):
        """Sets the time of applicability.

        Sets the time of applicability (measurement) of the reported position.
        In the form elapsed time since last midnight, expressed as UTC.

        Args:
            time_of_day (int): The time of applicability in seconds.

        """
        self.oldUpdateTime = self.time_of_day
        self.time_of_day = time_of_day


    def set_velocity(self, ground_speed, heading, vertical_rate):
        """Sets the velocity information of aircraft.

        Args:
        ground_speed (int): The ground speed in knots.
        heading (int): The heading in degrees.
        vertical_rate (int): The barometric vertical rate in feet/minute.

        """
        self.ground_speed = ground_speed
        self.heading = heading
        self.vertical_rate = vertical_rate


    def get_odd_msg(self):
        """Returns the ADS-B odd message of aircraft.

        Returns:
            string: The ADS-B odd message.
        """
        return self.odd_msg


    def set_odd_msg(self, adsb_data):
        """Sets the ADS-B odd message of aircraft.

        Args:
            adsb_data (string): The ADS-B message.

        """
        self.odd_msg = adsb_data


    def get_even_msg(self):
        """Returns the ADS-B even message of aircraft.

        Returns:
            string: The ADS-B even message.

        """
        return self.even_msg


    def set_even_msg(self, adsb_data):
        """Sets the ADS-B even message of aircraft.

        Args:
            adsb_data (string): The ADS-B message.

        """
        self.even_msg = adsb_data


    def was_update(self):
        """ Check if the data of the aircraft have been updated.

        Returns:
            bool: True if the data of the aircarft have been updated;
            otherwise False.

        """
        return self.time_of_day > self.oldUpdateTime


    def decode_position(self):
        """Check if is possible to decode the airbone position message.

        Returns:
            bool: True if it is possible decode the ADS-B message; otherwise False.

        """
        if self.odd_msg and self.even_msg:
            return True

        return False


    def to_asterix_record(self, icao24, category=21):
        """Converts the aircraft data to a dictionary.

        This dicitionary represents a record ASTERIX CAT 21

        Args:
            icao24 (string): The ICAO 24-bit aircraft address.

        Returns:
            string: A record ASTERIX CAT 21 of aircraft.

        """
        # If no update does not send the ASTERIX record
        if self.was_update() is False:
            return None

        # TODO: implementar radar (cat 34/48)
        if category != 21:
            print "Category %d not supported" % category
            return None

        flight_level = self.altitude / 100

        # Grouns speed in NM/s
        gs = self.ground_speed / 3600.0

        record = {10: {'SAC': self.SAC, 'SIC': self.sic},
                  40: {'DCR': 0, 'GBS': 0, 'SIM': 0, 'TST': 0, 'RAB': 0, 'SAA': 1, 'SPI': self.spi, 'ATP': 1, 'ARC': 1},
                  30: {'ToD': self.time_of_day},
                  130:{'Lat': self.latitude, 'Lon': self.longitude},
                  80: {'TAddr': int(icao24, 16)},
                  90: {'AC': 0, 'MN': 0, 'DC': 0, 'PA': self.NACp},
                  210: {'DTI': 0, 'MDS': 1, 'UAT': 0, 'VDL': 0, 'OTR': 0},
                  145: {'FL': flight_level},
                  155: {'BVR': self.vertical_rate},
                  160: {'GS': gs, 'TA': self.heading},
                  170: {'TId': self.callsign_to_bcd()},
                  95: {'VA': self.NACv},
                  200: {'PS': 0}}

        # if callsign is empty remove Data Item I021/170, Target Identification
        if (not self.callsign):
            del record[170]

        asterix_record = {21: [record]}

        return asterix_record


    def __str__(self):
        """Returns the object informationas as string.

        Returns:
            string: The object information.

        """
        return self.callsign + " " + str(self.altitude) + " " + str(self.ground_speed) + " " \
               + str(self.heading) + " " + str(self.vertical_rate) + " " + str(self.latitude) + " " \
               + str(self.longitude)
