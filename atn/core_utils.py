import os
import subprocess


def get_node_name(nem_id=None, session_id=None):

    # No arguments: returns the hostname of the caller
    if nem_id is None and session_id is None:
        out = subprocess.check_output(["/bin/hostname"])
        return out.rstrip('\n')

    if session_id is None:
        session_id = get_session_id()

    if nem_id is not None:
        fname = "/tmp/pycore.%s/emane_nems" % session_id
        f = open(fname, "r")
        for i in f.readlines():
            j = i.split()

            if int(j[2]) == int(nem_id):
                return j[0]

    return None


def get_node_list(session_id=None):
    if os.path.exists("../nodes"):
        fname = "../nodes"
    else:
        if session_id is None:
            session_id = get_session_id()

        if os.path.exists("/tmp/pycore."+session_id):
            fname = "/tmp/pycore."+session_id+"/nodes"
        else:
            return None

    node_name = []
    node_number = []
    with open(fname) as f:
        for line in f:
            l = line.split()

            node_number.append(int(l[0]))
            node_name.append(l[1])

    return node_number, node_name


def get_node_number(node_name=None, session_id=None):
    if os.path.exists("../nodes"):
        fname = "../nodes"
    else:
        if session_id is None:
            session_id = get_session_id()

        if os.path.exists("/tmp/pycore."+session_id):
            fname = "/tmp/pycore."+session_id+"/nodes"
        else:
            return None

    if node_name is None:
        node_name = get_node_name()

    with open(fname) as f:
        for line in f:
            l = line.split()
            if l[1] == node_name:
                return int(l[0])

    return None


def get_session_id():

    # Finding for CORE running sessions at /tmp
    dirs_tmp = os.listdir("/tmp")

    # Return first session found
    for dir_tmp in dirs_tmp:
        if dir_tmp.startswith("pycore."):
            return dir_tmp[7:]

    return None


def get_nem_id(node_name=None, session_id=None):

    if os.path.exists("../emane_nems"):
        fname = "../emane_nems"
    else:
        if session_id is None:
            session_id = get_session_id()

        if os.path.exists("/tmp/pycore."+session_id):
            fname = "/tmp/pycore."+session_id+"/emane_nems"
        else:
            return None

    if node_name is None:
        node_name = get_node_name()

    with open(fname) as f:
        for line in f:
            (name, dev, nemid) = line.split()
            if node_name == name:
                return int(nemid)
        return None


def get_nem_list(session_id=None):

    if os.path.exists("../emane_nems"):
        fname = "../emane_nems"
    else:
        if session_id is None:
            session_id = get_session_id()

        if os.path.exists("/tmp/pycore."+session_id):
            fname = "/tmp/pycore."+session_id+"/emane_nems"
        else:
            return None

    names = []
    devs = []
    nemids = []
    with open(fname) as f:
        for line in f:
            (name, dev, nemid) = line.split()

            names.append(name)
            devs.append(dev)
            nemids.append(int(nemid))

        return names, devs, nemids


def get_xy(node_name=None, session_id=None):
    if node_name is None:
        node_name = get_node_name()

    if os.path.exists("../%s.xy" % node_name):
        fname = "../%s.xy" % node_name
    else:
        if session_id is None:
            session_id = get_session_id()

        if os.path.exists("/tmp/pycore."+session_id):
            fname = "/tmp/pycore.%s/%s.xy" % (session_id, node_name)
        else:
            return None

    with open(fname) as f:
        for line in f:
            (xpos, ypos) = line.split()
            return float(xpos), float(ypos)
