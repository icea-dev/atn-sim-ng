import time

from atn.surveillance.adsb import adsb_out
from atn.surveillance.adsb.feeds import coreemu_feed

feed = coreemu_feed.CoreFeed()

#feed.gps_start()
#feed.emane_start()
feed.tracksrv_start()

time.sleep(1)

print (feed.gps_latitude, feed.emane_latitude, feed.tracksrv_latitude)
print (feed.gps_longitude, feed.emane_longitude, feed.tracksrv_longitude)
print (feed.gps_altitude, feed.emane_altitude, feed.tracksrv_altitude)

tx = adsb_out.AdsbOut(feed)
tx.start()

# while True:
#     time.sleep(0.4)
#     airborne_msg = tx.generate_airborne_position()
#     tx.broadcast(airborne_msg)
#
#     time.sleep(0.1)
#     id_msg = tx.generate_aircraft_id()
#     tx.broadcast(id_msg)


