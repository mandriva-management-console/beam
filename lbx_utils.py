# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id: lbx_utils.py 52 2010-02-11 09:08:24Z nicolas $
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

"""misc functions missing in Python

Funtions:
    human_readable(num, unit, base): return an human readable version of
        an integer
    get_local_parts(): fill a struct with available mountpoints
    get_part_mountpoint(device): return where the device is mounted
Require: /bin/mount
"""

__author__    = "Nicolas Rueff <nicolas.rueff@linbox.com>"
__version__   = "$Rev: 52 $"
__date__      = "$Date: 2007-05-31 16:57:13 +0200 (jeu, 31 mai 2007) $"
__licence__   = "GPL"
__copyright__ = "© 2007 Nicolas Rueff - Linbox F&AS"

import commands
import re
import os

def human_readable(num, unit='B', base=1024):
    """ Return an human readable version of an integer

        Supported units are from nothing to Tera (T)
        use 1000 as base for decimal units, 1024 for binaries units
    """
    for i in ['', 'K', 'M', 'G', 'T']:
        if num < base:
            return "%3.1f %s%s" % (num, i, unit)
        num /= base

def get_local_parts():
    """ Fill a struct with available mountpoints

        Using /bin/mount, return an array in wich each item is a dict:
          + 'device' => device name (f.e. "/dev/hda")
          + 'mountpoint' => mount point (f.e. "/home")
    """
    result = []
    out = commands.getoutput("/bin/mount")
    mounts = out.split('\n')
    for mount in mounts:
        match = re.search("^(/dev/.*) on (/.*) type ", mount)
        if ( match != None):
            mountpoint = {}
            mountpoint['device'] = match.group(1)
            mountpoint['mountpoint'] = match.group(2)
            result.append(mountpoint)
    return result

def get_part_mountpoint(device):
    """ Return where the device is mounted

    """
    parts = get_local_parts()
    for part in parts:
        if part['device'] == '/dev/%s' % device:
            return part['mountpoint']
    return None

