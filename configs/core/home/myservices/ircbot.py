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


class IrcBot(CoreService):
    ''' This is a sample user-defined service. 
    '''
    # a unique name is required, without spaces
    _name = "IRCbot"
    # you can create your own group here
    _group = "Aviation"
    # list of other services this service depends on
    _depends = ()
    # per-node directories
    _dirs = ()
    # generated files (without a full path this file goes in the node's dir,
    #  e.g. /tmp/pycore.12345/n1.conf/)
    _configs = ('ircbot.cfg', 'ircbot.sh',)
    # this controls the starting order vs other enabled services
    _startindex = 70
    # list of startup commands, also may be generated during startup
    _startup = ('sh ircbot.sh',)
    # list of shutdown commands
    _shutdown = ()

    @classmethod
    def generateconfig(cls, node, filename, services):
        ''' Return a string that will be written to filename, or sent to the
            GUI for user customization.
        '''
        cfg = ""

        if filename == "ircbot.cfg":
            cfg += "[IRC]\n"
            cfg += "server = 10.0.0.1\n"
            cfg += "channel = #atc\n"
            cfg += "nick = %s\n" % node.name

        if filename == "ircbot.sh":
            cfg += "#!/bin/sh\n"
            cfg += "sleep 30\n"
            cfg += "python -m adsb.ircbot\n"

        return cfg


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
addservice(IrcBot)

