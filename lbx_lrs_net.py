# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id: lbx_lrs_net.py 52 2010-02-11 09:08:24Z nicolas $
#
# This file is part of BeaM
#
# BeaM is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# BeaM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2. If not, see <http://www.gnu.org/licenses/>.
#

"""Utilities to NET comm. with the LRS binaries

LRS comm is based on PMRPC (Poor man's RPC). See the LRS code for the draft.

Basically:
    - GUI is listing and CLI is sending, based on tockens exchange.
    - CLI send command (one keyword, several args).
    - GUI send back acks (one keyword)
    - keywords and args are encoded as "tockens"

    One tocken is:
        - one ui32 (4 bytes, Little Endian) giving the length of the tocken,
        - (lenght) bytes containing the tocken (formerly a string)

    One command is:
        - one tocken containing the keyword,
        - one ui32 (4 bytes, Little Endian) giving the number of args,
        - several tockens, one per arg.

    Exemple (from the GUI ppoint of view):
        RC: |init_backup|
        RA: |/dev/hda1|/home/LRS/noiraude_2007-07-05_18:19:44/P1|192712|84706|
/home/nicolas/Devs/GhostKiller/lrs-bin/revobin/image_e2fs|
        S:  |OK|
        RC: |refresh_backup_progress|
        RA: |0|
        S:  |OK|
        RC: |refresh_backup_progress|
        RA: |818176|
        RC: |close|
        S:  |OK|
TODO: document differents commands
Functions:
    lrs_net_init() => socket object
    lrs_get_next_tocken(arrival) => return string in pipe
    lrs_get_next_counter(arrival) => return int in pipe
    lrs_get_next_tockens(arrival) => return messages in pipe
    lrs_send_tocken(arrival, tocken) => send tocken in pipe
    lrs_send_ack(arrival) => send an ack in pipe (i.e. "OK")
"""
__author__    = "Nicolas Rueff <nicolas.rueff@linbox.com>"
__version__   = "$Rev: 52 $"
__date__      = "$Date: 2007-05-31 17:01:40 +0200 (jeu, 31 mai 2007) $"
__licence__   = "GPL"
__copyright__ = "© 2007 Nicolas Rueff - Linbox F&AS"

from socket import socket, AF_INET, SOCK_STREAM
from struct import pack, unpack
import logging

import lbx_logging

def lrs_net_init():
    """ Listen on 127.0.0.1:7001/TCP for incoming connections

    Only one connection for now
    """
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", 7001))
    except OSError: # FIXME: error handling
        print "can't bind"
    sock.listen(1)

    return sock

def lrs_get_next_tocken(arrival):
    """ Return next available tocken in pipe

    Used to get a command
    """
    tockenlen = unpack("=L", arrival.recv(4))[0]
    tockenval = arrival.recv(tockenlen)
    logging.debug("RECEIVED: %s" % tockenval)
    return tockenval

def lrs_get_next_counter(arrival):
    """ Return next available ui32 in pipe

    Used to get a tocken lenght
    """
    return unpack("=L", arrival.recv(4))[0]

def lrs_get_next_tockens(arrival):
    """ Return next tockens in pipe

    Used to get a handful of args after a command
    """
    tockens = []
    for i in range(lrs_get_next_counter(arrival)):
        i += 0 # dirty fix for pylint :D
        tockens.append(lrs_get_next_tocken(arrival))
    return tockens

def lrs_send_tocken(arrival, tocken):
    """ Put a tocken in pipe
    """
    arrival.send("%s%s" % (pack("=L", len(tocken)), tocken))
    logging.debug("SEND: %s" % tocken)

def lrs_send_ack(arrival):
    """ Send "OK" (i.e. an ack) to the client
    """
    lrs_send_tocken(arrival, "OK")
