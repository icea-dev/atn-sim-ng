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

class IRCd(CoreService):
    ''' This is a sample user-defined service. 
    '''
    # a unique name is required, without spaces
    _name = "IRC"
    # you can create your own group here
    _group = "Utility"
    # list of other services this service depends on
    _depends = ()
    # per-node directories
    _dirs = ()
    # generated files (without a full path this file goes in the node's dir,
    #  e.g. /tmp/pycore.12345/n1.conf/)
    _configs = ('iauth.conf', 'ircd.conf', 'ircd.motd', 'ircd-irc2', )
    # this controls the starting order vs other enabled services
    _startindex = 50
    # list of startup commands, also may be generated during startup
    _startup = ('sh ircd-irc2 start',)
    # list of shutdown commands
    _shutdown = ('sh ircd-irc2 stop',)

    @classmethod
    def generateconfig(cls, node, filename, services):
        ''' Return a string that will be written to filename, or sent to the
            GUI for user customization.
        '''
        cfg = ""

        if filename == "iauth.conf":
            cfg += '# If iauth timeouts, then reject user\n'
            cfg += 'notimeout\n'
            cfg += '\n'
            cfg += '# This makes the IRC server require that iauth performs the authentication\n'
            cfg += '# in order for a new user connection to be accepted\n'
            cfg += 'required\n'
            cfg += '\n'
            cfg += '# Perform ident lookups\n'
            cfg += 'module rfc931\n'

            return cfg

        if filename == "ircd.conf":
            cfg += "# This is ircd's config-file. Look at\n"
            cfg += '# /usr/share/doc/ircd-irc2/ircd.conf.example.gz and\n'
            cfg += '# and /usr/share/doc/ircd-irc2/INSTALL.* for more detailled information\n'
            cfg += '# and instructions\n'
            cfg += '\n'
            cfg += '# M-Line\n'
            cfg += 'M:irc.localhost::Debian ircd default configuration::000A\n'
            cfg += '\n'
            cfg += '# A-Line\n'
            cfg += "A:This is Debian's default ircd configurations:Please edit your /etc/ircd/ircd.conf file:Contact <root@localhost> for questions::ExampleNet\n"
            cfg += '\n'
            cfg += '# Y-Lines\n'
            cfg += 'Y:1:90::100:512000:5.5:100.100\n'
            cfg += 'Y:2:90::300:512000:5.5:250.250\n'
            cfg += '\n'
            cfg += '# I-Line\n'
            cfg += 'I:*:::0:1\n'
            cfg += 'I:127.0.0.1/32:::0:1\n'
            cfg += '\n'
            cfg += '# P-Line\n'
            cfg += 'P::::6667:\n'

            return cfg

        if filename == "ircd.motd":
            cfg += "                         [ Debian GNU/Linux ]\n"
            cfg += "|------------------------------------------------------------------------|\n"
            cfg += "| This is Debian's default IRCd server configuration for irc2.11. If you |\n"
            cfg += "| see this and if you are the server administrator, just edit ircd.conf  |\n"
            cfg += "| and ircd.motd in /etc/ircd.                                            |\n"
            cfg += "|                                     Martin Loschwitz, 1st January 2005 |\n"
            cfg += "|------------------------------------------------------------------------|\n"

            return cfg

        if filename == "ircd-irc2":
            cfg += '#!/bin/sh\n'
            cfg += '### BEGIN INIT INFO\n'
            cfg += '# Provides:          ircd-irc2\n'
            cfg += '# Required-Start:    $remote_fs\n'
            cfg += '# Required-Stop:     $remote_fs\n'
            cfg += '# Default-Start:     2 3 4 5\n'
            cfg += '# Default-Stop:\n'
            cfg += '# Short-Description: Starts/stops the irc daemon\n'
            cfg += '### END INIT INFO\n'
            cfg += '\n'
            cfg += 'set -e\n'
            cfg += '\n'
            cfg += '# $PATH to go\n'
            cfg += 'PATH=/sbin:/bin:/usr/sbin:/usr/bin\n'
            cfg += '\n'
            cfg += '# where the irc-daemon is\n'
            cfg += 'IRCD=/usr/sbin/ircd\n'
            cfg += 'PIDFILE=var.run/ircd/ircd.pid\n'
            cfg += '\n'
            cfg += 'check_pid_dir() {\n'
            cfg += '	if [ ! -d var.run/ircd ]; then\n'
            cfg += '		mkdir var.run/ircd\n'
            cfg += '		chown irc:irc var.run/ircd\n'
            cfg += '		chmod 775 var.run/ircd\n'
            cfg += '	fi\n'
            cfg += '}\n'
            cfg += '\n'
            cfg += '\n'
            cfg += '# Gracefully exit if the package has been removed.\n'
            cfg += 'test -x $IRCD || exit 0\n'
            cfg += '\n'
            cfg += 'case "$1" in\n'
            cfg += '\n'
            cfg += '       start)\n'
            cfg += '		check_pid_dir\n'
            cfg += '                       echo -n "Starting irc server daemon:"\n'
            cfg += '               echo -n " ircd"\n'
            cfg += '               start-stop-daemon --start --quiet --pidfile ${PIDFILE} \\\n'
            cfg += '                       --chuid irc --exec ${IRCD} --oknodo\n'
            cfg += '               echo "."\n'
            cfg += '               ;;\n'
            cfg += ' \n'
            cfg += '       stop)\n'
            cfg += '               echo -n "Stopping irc server daemon:"\n'
            cfg += '               echo -n " ircd"\n'
            cfg += '               start-stop-daemon --stop --quiet --oknodo \\\n'
            cfg += '                       --pidfile ${PIDFILE} --exec ${IRCD}\n'
            cfg += '               echo "."  \n'
            cfg += '               ;;\n'
            cfg += '\n'
            cfg += '       reload|force-reload)\n'
            cfg += '               echo -n "Reloading irc server daemon:"\n'
            cfg += '               echo -n " ircd"\n'
            cfg += '               start-stop-daemon --stop --signal 1 --quiet \\\n'
            cfg += '                       --pidfile ${PIDFILE} --exec ${IRCD}\n'
            cfg += '               echo "."\n'
            cfg += '               ;;\n'
            cfg += '\n'
            cfg += '       restart)\n'
            cfg += '		check_pid_dir\n'
            cfg += '               echo -n "Restarting irc server daemon:"\n'
            cfg += '               echo -n " ircd"\n'
            cfg += '               start-stop-daemon --stop --quiet --oknodo \\\n'
            cfg += '                       --pidfile ${PIDFILE} --exec ${IRCD}\n'
            cfg += '               sleep 1\n'
            cfg += '               start-stop-daemon --start --quiet --pidfile ${PIDFILE} \\n'
            cfg += '                       --chuid irc --exec ${IRCD}\n'
            cfg += '               echo "."\n'
            cfg += '               ;;\n'
            cfg += '       *)\n'
            cfg += '               echo "Usage: $0 {start|stop|restart|reload|force-reload}"\n'
            cfg += '               exit 1\n'
            cfg += '               ;;\n'
            cfg += 'esac\n'
            cfg += '\n'
            cfg += 'exit 0\n'

            return cfg

        return "# Not available\n"

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
addservice(IRCd)

