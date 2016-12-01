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

class Gpsd(CoreService):
    ''' This is a sample user-defined service.
    '''
    # a unique name is required, without spaces
    _name = "GPSd"
    # you can create your own group here
    _group = "Aviation"
    # list of other services this service depends on
    _depends = ()
    # per-node directories
    _dirs = ()
    # generated files (without a full path this file goes in the node's dir,
    #  e.g. /tmp/pycore.12345/n1.conf/)
    _configs = ('gpsd.sh', 'eventdaemon.xml', 'gpsdlocationagent.xml')
    # this controls the starting order vs other enabled services
    _startindex = 50
    # list of startup commands, also may be generated during startup
    _startup = ('sh gpsd.sh',)
    # list of shutdown commands
    _shutdown = ()

    @classmethod
    def generateconfig(cls, node, filename, services):
        ''' Return a string that will be written to filename, or sent to the
            GUI for user customization.
        '''

        # Required packages (Ubuntu 14.04): mgen fping gpsd gpsd-clients cgps
        # iperf multitail olsrd openssh-server python-tk python-pmw python-lxml \
        # python-stdeb build-essential
        if filename == 'gpsd.sh':
            cfg  = "#!/bin/sh\n"
            cfg += 'emaneeventd eventdaemon.xml -r -d -l 3 -f var.log/emaneeventd.log\n'
            cfg += 'sleep 5\n'
            cfg += 'gpsd -G -n -b $(cat var.run/gps.pty)\n'

        # Emane configuration file for GPS event
        elif filename ==  'eventdaemon.xml':
            cfg = '<?xml version="1.0" encoding="UTF-8"?>\n'
            cfg += '<!DOCTYPE eventdaemon SYSTEM "file:///usr/share/emane/dtd/eventdaemon.dtd">\n'
            cfg += '<eventdaemon nemid="%s">\n' % node.objid
            cfg += '  <param name="eventservicegroup" value="224.1.2.8:45703"/>\n'
            cfg += '  <param name="eventservicedevice" value="ctrl0"/>\n'
            cfg += '  <agent definition="gpsdlocationagent.xml"/>\n'
            cfg += '</eventdaemon>\n'

        # Emane configuration for GPS agent
        elif filename == "gpsdlocationagent.xml":
            cfg  = '<?xml version="1.0" encoding="UTF-8"?>\n'
            cfg += '<!DOCTYPE eventagent SYSTEM "file:///usr/share/emane/dtd/eventagent.dtd">\n'
            cfg += '<eventagent library="gpsdlocationagent">\n'
            # cfg += '  <param name="gpsdconnectionenabled" value="no"/>\n'
            cfg += '  <param name="pseudoterminalfile"\n'
            cfg += '         value="var.run/gps.pty"/>\n'
            cfg += '</eventagent>\n'

        else:
            cfg = "#!/bin/sh\n"
            cfg += "# auto-generated: %s\n" % filename

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
addservice(Gpsd)
