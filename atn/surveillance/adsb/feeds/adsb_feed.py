from abc import ABCMeta, abstractmethod


class AdsbFeed(object):
    """Abstract class that provides information for ADS-B Out transponders.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_ssr(self):
        """Informs current squawk code of the given aircraft.

        Examples:
            - 7500: Hi-Jacking
            - 7600: Radio Failure
            - 7700: Emergency

        The complete list can be found in http://www.flightradars.eu/lsquawkcodes.html
        """
        raise NotImplementedError()

    @abstractmethod
    def get_spi(self):
        """Informs if SPI is activated.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_callsign(self):
        """Provides the callsign of the given aircraft.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_position(self):
        """Provides latitude, longitude, and altitude in meters.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_velocity(self):
        """Provides azimuth, climb_rate, and speed in meters per second.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_icao24(self):
        raise NotImplementedError()

    @abstractmethod
    def get_capabilities(self):
        raise NotImplementedError()

    @abstractmethod
    def get_type(self):
        raise NotImplementedError()