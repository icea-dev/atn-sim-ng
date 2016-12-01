"""@package ground_station
"""
__author__ = "Ivan Matias"
__date__ = "2016/11/01"


class GroundStation(object):
    """
    This class provide service messages from a CNS/ATM Ground Station.
    """
    ## GROUND_STATION_STATUS_MESSAGE [int]:
    GROUND_STATION_STATUS_MESSAGE = 1
    ## SERVICE_STATUS_MESSAGE [int]:
    SERVICE_STATUS_MESSAGE = 2
    ## SERVICE_STATISTICS_MESSAGE [int]:
    SERVICE_STATISTICS_MESSAGE = 3


    def __init__(self, sic, sac=232):
        """ The constructor

        Args:

            sic (int): The system code identification of surveillance sensor.
            sac (int): The system area code of surveillance sensor.
        """

        ## sic [int]: The system code identification
        self.sic = sic

        ## sac [int]: The system code area
        self.sac = sac


    def to_asterix_record(self, message_type, time_of_day):
        """
        Convert  the service message of Ground Station to a dictionary.

        Args:
            message_type (int): Type of message, the following set of Message Types are standardised for
            Category 023 records:
                001 - Ground Station Status message
                002 - Service Status message
                003 - Service Statistics message
            time_of_day (int): Time of applicability in seconds, in the form of elapsed time since last midnight

        Returns:
            dictionary : A record ASTERIX CAT 023 of CNS/ATM Ground Station
        """

        record = {}

        if self.SERVICE_STATUS_MESSAGE == message_type:
            record = {0: {'message_type': message_type},
                      10: {'SAC': self.sac, 'SIC': self.sic},
                      15: {'SID': 2 }, # ADS-B Ext Squitter
                      70: {'ToD': time_of_day},
                      110: {'STAT': 8}}
        elif self.GROUND_STATION_STATUS_MESSAGE == message_type:
            record = {0: {'message_type': message_type},
                      10: {'SAC': self.sac, 'SIC': self.sic},
                      70: {'ToD': time_of_day},
                      100: {'OP': 0, 'ODP': 0, 'OXT': 0, 'MSC': 1, 'TSV': 0}}
        else:
            return None

        asterix_record = {23: [record]}

        return asterix_record
