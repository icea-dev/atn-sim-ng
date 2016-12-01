#
# CORE
# Copyright (c)2010-2012 the Boeing Company.
# See the LICENSE file included in this distribution.
#
''' Sample user-defined service.
'''

import os

from core.service import CoreService, addservice
from core.misc.ipaddr import IPv4Prefix, IPv6Prefix

class TrackServer(CoreService):
    ''' This is a sample user-defined service. 
    '''
    # a unique name is required, without spaces
    _name = "TrackServer"
    # you can create your own group here
    _group = "Aviation"
    # list of other services this service depends on
    _depends = ()
    # per-node directories
    _dirs = ()
    # generated files (without a full path this file goes in the node's dir,
    #  e.g. /tmp/pycore.12345/n1.conf/)
    _configs = ('track_server.cfg',)
    # this controls the starting order vs other enabled services
    _startindex = 50
    # list of startup commands, also may be generated during startup
    _startup = ('python -m atn.track_server', 'python -m atn.track_cmd restart',)
    # list of shutdown commands
    _shutdown = ('python -m atn.track_cmd stop',)

    @classmethod
    def generateconfig(cls, node, filename, services):
        ''' Return a string that will be written to filename, or sent to the
            GUI for user customization.
        '''
        if filename == "track_server.cfg":
            cfg = "[Database]\n"
            cfg += "; db_host = 172.17.255.254\n"
            cfg += "; db_name = atn_sim\n"
            cfg += "; db_user = atn_sim\n"
            cfg += "; db_pass = atn_sim\n"
            cfg += "\n"
            cfg += "[Tracks]\n"
            cfg += "; server = 172.17.255.254\n"
            cfg += "; port = 5006\n"
            cfg += "; exercise = SPRINT5\n"
            cfg += "; n1 = 1\n"

            return cfg
        return None

    @staticmethod
    def subnetentry(x):
        ''' Generate a subnet declaration block given an IPv4 prefix string
            for inclusion in the config file.
        '''
        if x.find(":") >= 0:
            # this is an IPv6 address
            return ""
        else:
            net = IPv4Prefix(x)
            return 'echo "  network %s"' % (net)

# this line is required to add the above class to the list of available services
addservice(TrackServer)

