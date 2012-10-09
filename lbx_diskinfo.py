# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id: lbx_diskinfo.py 64 2010-02-12 08:35:22Z nicolas $
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

"""Utilities to handle mount points

Functions:
    get_parts() => {}

Needs /usr/bin/file, /bin/df, /proc and /sys to work
"""
__author__    = "Nicolas Rueff <nicolas.rueff@linbox.com>"
__version__   = "$Rev: 64 $"
__date__      = "$Date: 2007-05-31 17:01:40 +0200 (jeu, 31 mai 2007) $"
__licence__   = "GPL"
__copyright__ = "© 2007 Nicolas Rueff - Linbox F&AS"

import re
import commands
import os
import logging
import copy

import lbx_logging

def get_parts():
    """ Get stats about partitions and mounted partitions

    Try to return something like this:
    {
    1:{                                      Disk number
      'desc': 'Hard Drive',                  Printable kind
      'kind': 'localdisk',                   Kind of disk (removable, net, ...)
      'name': 'hda',                         Disk name (ir srv for net shares)
      'size': 40007761920L}}                 Disk size
      'parts': {
        1: {                                 Partition number (or share for
                                             network drive)
          'desc': 'Linux Ext3'               Printable kind
          'dirs': ['lost+found', 'grub'],    Firts level dirs
          'display': 1,                      0: special part (extended f.e.)
          'free': 50365440,                  Part free space
          'include': 1,                      Show part as « backupable »
          'kind': 'ext3',                    Part kind
          'mountpoint': '/boot',             Part mount point
          'name': 'hda1',                    Part name (or share for net. drive)
          'size': 98670592,                  Part Size
        },
    .......

    using /proc/partitions (with /usr/bin/file to handle partition type)
    """

    result = {}

    fd_proc_part = open("/proc/partitions")
    df_output = commands.getoutput("/bin/df -P -k -T")
    mounted_fs = df_output.split('\n')
    disk_index = 0

    for lignes_proc_part in fd_proc_part:
        parts = lignes_proc_part.split() # match /proc/partition output
                                         # parts[0] => major
                                         # parts[1] => minor
                                         # parts[2] => # blocks
                                         # parts[3] => dev name
                                         # (/dev/... without /dev/)
                                         # others not used
        part_result = {} # will contain part info
        try: # skip bad lines
            part_result['size'] = int(parts[2]) * 1024
        except (ValueError, IndexError):
            continue
        part_dev = parts[3]

        if ( int(parts[1]) & 15 == 0 and int(parts[0]) != 254 ): # that's a disk ( parts[0] == 254 => device mapper)
            for (key, val) in _analyse_disk(part_dev).items():
                part_result[key] = val
            disk_index += 1
            result[disk_index] = part_result
        else: # that's a partition

            # create a fake disk if we did found the first devmapper ever
            if ( int(parts[0]) == 254 and int(parts[1]) == 0):
                part_result['kind'] = 'devmapper'
                part_result['desc'] = 'Device Mapper'
                part_result['parts'] = {}
                part_result['name'] = 'dm'
                part_result['major'] = 254
                disk_index += 1
                result[disk_index] = copy.copy(part_result)

            # get part kind
            part_result['num'] = int(parts[1]) & 15
            for (key, val) in _analyse_part(part_dev).items():
                part_result[key] = val
            for mount in mounted_fs: # get mount point and  free space
                for (key, val) in _analyse_mount(part_dev, mount).items():
                    part_result[key] = val
            result[disk_index]['parts'][int(parts[1]) & 15] \
                  = part_result

    fd_proc_part.close()
    logging.debug(result)
    return result

def _analyse_mount(part_dev, mount):
    """ Identify given mount point

    Input:
        part_dev: device name *inside* /dev
        mount: output line from df

    uses df to handle mount kind

    """
    result = {}
    # match df output
    # df_fields[1] => dev name
    # df_fields[2] => fs kind
    # df_fields[4] => used space
    # df_fields[5] => free space
    # df_fields[7] => mount point
    df_fields = re.search(
        "^(/dev/%s) +([^ ]*) +([0-9]+) +([0-9]+) +([0-9]+) +(.*) +(/.*)"
        % part_dev, mount)
    if ( df_fields != None): # seem to be a worthy line
        result['mountpoint'] = df_fields.group(7)
        result['free'] = int(df_fields.group(5)) * 1024
        result['kind'] = df_fields.group(2)
        result['dirs'] = []
        for directory in os.listdir(
            result['mountpoint']):
            if (os.path.isdir(
                os.path.join(result['mountpoint']
                , directory)
            )):
                result['dirs'].append(directory)
    return result

def _analyse_disk(part_dev):
    """ Identify given disk

    Input:
        part_dev: device name *inside* /dev

    uses sys to handle disk kind

    """

    result = {}
    try:
        fd_sys = open('/sys/block/%s/removable' % part_dev)
        for lines_sys in fd_sys: # attempt to guess if disk is removable
        # FIXME: i18n kind + desc
            if (lines_sys == "0\n"):
                result['kind'] = "localdisk"
                result['desc'] = "Hard Drive"
            else:
                result ['kind'] = "removabledisk"
                result['desc'] = "Removable Media"
        fd_sys.close
    except IOError:
        result['kind'] = "specialdisk"
        result['desc'] = "Special Drive"

    try:
        fd_sys = open('/sys/block/%s/dev' % part_dev)
        major = 0
        minor = 0
        for lines_sys in fd_sys: # guess major:minor
            (major, minor) = lines_sys.split(':')
        fd_sys.close
    except IOError:
        result['kind'] = "specialdisk"
        result['desc'] = "Special Drive"

    result['parts'] = {}
    result['name'] = part_dev
    result['major'] = major
    result['minor'] = minor
    return result

def _analyse_part(part_dev):
    """ Identify given part

    Input:
        part_dev: part name *inside* /dev
    uses /bin/df to handle mounted fs
    """
    result = {}
    # FIXME: check access rights
    # FIXME: i18n descs

    part_info = commands.getoutput(
        "env POSIXLY_CORRECT=1 /usr/bin/file -s /dev/%s" % part_dev
    )
    if re.search('SGI XFS', part_info):
        part_desc = 'SGI XFS'
        display = 1
        include = 1
    elif re.search('ext2 filesystem', part_info):
        part_desc = 'Linux Ext2'
        display = 1
        include = 1
    elif re.search('ext3 filesystem', part_info):
        part_desc = 'Linux Ext3'
        display = 1
        include = 1
    elif re.search('FAT \(16 bit\)', part_info):
        part_desc = 'MS Fat16'
        display = 1
        include = 1
    elif re.search('FAT \(32 bit\)', part_info):
        part_desc = 'MS Fat32'
        display = 1
        include = 1
    elif re.search('NTFS', part_info):
        part_desc = 'MS NTFS'
        display = 1
        include = 1
    elif re.search('Reiser FS', part_info):
        part_desc = 'ReiserFS'
        display = 1
        include = 1
    elif re.search('ReiserFS', part_info):
        part_desc = 'ReiserFS'
        display = 1
        include = 1
    elif re.search('Linux/i386 swap file', part_info):
        part_desc = 'Linux Swap'
        display = 1
        include = 1
    elif re.search('Minix', part_info):
        part_desc = 'Minix'
        display = 1
        include = 0
    elif re.search('LUKS encrypted file, ver 1 ', part_info):
        part_desc = 'Encrypted Partition'
        display = 1
        include = 0
    elif re.search('extended partition table', part_info):
        part_desc = 'Extended Partition'
        display = 0
        include = 0
    else:
        part_desc = 'Unknown (%s)' % part_info
        display = 1
        include = 0
    result['kind'] = "partition"
    result['desc'] = part_desc
    result['name'] = part_dev
    result['display'] = display
    result['include'] = include

    return result

