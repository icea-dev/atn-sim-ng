import time

from atn import core_utils

node_name = core_utils.get_node_name()
session_id = core_utils.get_session_id()

t = time.time()
print "NEM ID (1): %d (%f s)" % (core_utils.get_nem_id(), time.time() - t)
t = time.time()
print "NEM ID (2): %d (%f s)" % (core_utils.get_nem_id(node_name=node_name), time.time() - t)
t = time.time()
print "NEM ID (3): %d (%f s)" % (core_utils.get_nem_id(session_id=session_id), time.time() - t)
t = time.time()
print "NEM ID (4): %d (%f s)" % (core_utils.get_nem_id(node_name=node_name, session_id=session_id), time.time() - t)

t = time.time()
print "NODE ID (1): %d (%f s)" % (core_utils.get_node_number(), time.time() - t)
t = time.time()
print "NODE ID (2): %d (%f s)" % (core_utils.get_node_number(node_name=node_name), time.time() - t)
t = time.time()
print "NODE ID (3): %d (%f s)" % (core_utils.get_node_number(session_id=session_id), time.time() - t)
t = time.time()
print "NODE ID (4): %d (%f s)" % (core_utils.get_node_number(node_name=node_name, session_id=session_id), time.time() - t)

t = time.time()
x, y = core_utils.get_xy()
print "NODE XY (1): (%f, %f) (%f s)" % (x, y, time.time() - t)

t = time.time()
x, y = core_utils.get_xy(node_name=node_name)
print "NODE XY (2): (%f, %f) (%f s)" % (x, y, time.time() - t)

t = time.time()
x, y = core_utils.get_xy(session_id=session_id)
print "NODE XY (3): (%f, %f) (%f s)" % (x, y, time.time() - t)

t = time.time()
x, y = core_utils.get_xy(node_name=node_name, session_id=session_id)
print "NODE XY (4): (%f, %f) (%f s)" % (x, y, time.time() - t)