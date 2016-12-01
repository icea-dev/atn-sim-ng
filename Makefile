deps:
	sudo apt-get install -y --force-yes librtlsdr-dev librtlsdr0 rtl-sdr libusb-1.0-0-dev libusb-1.0-0 bash bridge-utils ebtables iproute libev-dev python tcl8.5 tk8.5 libtk-img autoconf automake gcc make python-dev libreadline-dev pkg-config imagemagick help2man python-sphinx gcc g++ autoconf automake libtool libxml2-dev libprotobuf-dev python-protobuf libpcap-dev libpcre3-dev uuid-dev libace-dev python-stdeb debhelper pkg-config python-lxml python-setuptools protobuf-compiler python-mpi4py python-qt4 git ssh iperf tshark tcpdump nmap traceroute gpsd gpsd-clients ircd-irc2 xchat python-geopy python-numpy python-pip python-mysqldb python-mysql.connector mysql-server python-matplotlib python-scipy python-netifaces python-ipcalc libnl1 quagga mysql-proxy ;\
	sudo pip install gps3 ;\
	wget http://downloads.pf.itd.nrl.navy.mil/ospf-manet/quagga-0.99.21mr2.2/quagga-mr_0.99.21mr2.2_amd64.deb ;\
	sudo dpkg -i quagga-mr_0.99.21mr2.2_amd64.deb ;\

dump1090:
	git clone https://github.com/MalcolmRobb/dump1090.git   ;\
	cd dump1090                                             ;\
	make

core:
	git clone https://github.com/coreemu/core.git   ;\
	cd core                                         ;\
	./bootstrap.sh                                  ;\
	./configure                                     ;\
	make -j8

emane:
	git clone https://github.com/adjacentlink/emane.git ;\
	cd emane                                            ;\
#	git checkout v1.0.1                                 ;\
	./autogen.sh                                        ;\
	./configure                                         ;\
	make deb

ptracks:
	git clone https://github.com/contemmcm/ptracks.git

all: dump1090 core emane ptracks

install: dump1090 core emane ptracks
	# CORE
	cd core ; sudo make install; cd ..

	# EMANE
	cd emane/.debbuild ; sudo dpkg -i *.deb ; cd ../..

	# DUMP 1090
	sudo cp -r dump1090 /opt

	# PTRACKS
	cd ptracks; sudo ./install ; cd ..
	sudo update-rc.d ptracks-net defaults

	# ATN-SIM

	sudo rm -f /usr/local/lib/python2.7/dist-packages/atn
	sudo ln -s `pwd`/atn/ /usr/local/lib/python2.7/dist-packages/atn
	sudo ln -s `pwd` /opt/atn-sim

	sudo rm -rf /etc/core
	rm -rf ~/.core
	sudo ln -s `pwd`/configs/core/etc/ /etc/core
	ln -s `pwd`/configs/core/home ~/.core

	# Database
	cd configs/db ; sudo /bin/sh setup.sh ; cd ../..

	# Start CORE-DAEMON
	sudo service core-daemon stop
	sudo service core-daemon start
	
	# Start PTRACKS-NET
	sudo service ptracks-net start

clean:
	rm -rf core
	rm -rf emane
	rm -rf dump1090
	rm -rf ptracks
	rm -f quagga-mr_0.99.21mr2.2_amd64.deb

uninstall:
	sudo rm /opt/atn-sim
	sudo rm /usr/local/lib/python2.7/dist-packages/atn
	sudo rm -rf /opt/dump1090
	sudo rm /usr/local/lib/python2.7/dist-packages/ptracks
	sudo rm -rf /etc/ptracks
	sudo rm /etc/init.d/ptracks
