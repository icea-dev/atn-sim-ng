import time

from atn.surveillance.adsb import adsb_in

rx = adsb_in.AdsbIn("test_adsb_in.cfg")

rx.start()

