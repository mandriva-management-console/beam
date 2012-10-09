# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id: lbx_lrs_image.py 60 2010-02-11 13:45:42Z nicolas $
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
    is_lrs_image(dir): return true if dir contains an LRS image
    get_image_stats(dir) : return Image stats (from conf.txt and others)
"""

__author__    = "Nicolas Rueff <nicolas.rueff@linbox.com>"
__version__   = "$Rev: 60 $"
__date__      = "$Date: 2007-05-15 18:42:26 +0200 (mar, 15 mai 2007) $"
__licence__   = "GPL"
__copyright__ = "© 2007 Nicolas Rueff - Linbox F&AS"

import os
import re
from beam_consts import *

def is_lrs_image(directory):
    """ Return true if directory is an LRS image

    """

    realdir = os.path.join(directory, BEAM_LRS_SAVE_FOLDER)
    if os.path.isdir(realdir):
        should_contain = [
            'log.txt',
            'progress.txt',
            'CONF',
            'conf.txt',
            'size.txt'
        ]
        intersect = []
        try:
            for item in os.listdir(realdir):
                if item in should_contain:
                    intersect.append(item)
            if len(intersect) == len(should_contain):
                return True
        except OSError:
            return False
    return False

def get_image_stats(directory):
    """ Return Image stats (from conf.txt and others)
    """
    image_stats = {}
    image_stats['disks'] = {}
    if is_lrs_image(directory):
        fd_grub_file = open(os.path.join(
            directory,
            BEAM_LRS_SAVE_FOLDER,
            BEAM_LRS_IMG_GRUBFILE
        ))
        for line_grub_file in fd_grub_file:
            for word in ['title', 'desc']:
                line_grub_file_part = re.search(
                    "^%s (.*)$" % word,
                    line_grub_file
                )
                if line_grub_file_part != None:
                    image_stats[word] = line_grub_file_part.group(1)

            line_grub_file_part = re.search(
                "^#?ptabs \(hd([0-9]+)\) ",
                line_grub_file
            )
            if line_grub_file_part != None: # got one disk
                hd_number = int(line_grub_file_part.group(1))
                image_stats['disks'][hd_number] = {}
                image_stats['disks'][hd_number]['line'] = \
                    line_grub_file.rstrip("\n").lstrip("#")

            line_grub_file_part = \
                re.search(
                    "^ # \(hd([0-9]+),([0-9]+)\) ([0-9]+) ([0-9]+) ([0-9]+)$",
                    line_grub_file
                )
            if line_grub_file_part != None: # got one part (first line ?)
                hd_number = int(line_grub_file_part.group(1))
                part_number = int(line_grub_file_part.group(2))
                start = int(line_grub_file_part.group(3)) * 512
                end = int(line_grub_file_part.group(4)) * 512
                len = end - start
                kind = line_grub_file_part.group(5)
                try:
                    image_stats['disks'][hd_number][part_number] = {}
                except KeyError:
                    image_stats['disks'][hd_number] = {}
                    image_stats['disks'][hd_number][part_number] = {}
                image_stats['disks'][hd_number][part_number]['start'] = start
                image_stats['disks'][hd_number][part_number]['size'] = len
                image_stats['disks'][hd_number][part_number]['kind'] = kind

            line_grub_file_part = \
                re.search(
                    "^#? partcopy \(hd([0-9]+),([0-9]+)\) ([0-9]+) PATH/",
                    line_grub_file
                )
            if line_grub_file_part != None: # got one part (second line)
                hd_number = int(line_grub_file_part.group(1))
                part_number = int(line_grub_file_part.group(2))
                image_stats['disks'][hd_number][part_number]['line'] = \
                    line_grub_file.rstrip("\n").lstrip("#")
        fd_grub_file.close()

        fd_size_file = open(os.path.join(
            directory,
            BEAM_LRS_SAVE_FOLDER,
            BEAM_LRS_IMG_SIZEFILE)
        )
        for line_size_file in fd_size_file:
            line_size_file_part = re.search("^([0-9]+)", line_size_file)
            if not line_size_file_part == None:
                image_stats['size'] = int(line_size_file_part.group(1)) * 512
        fd_size_file.close()

        try:
            fb_name_file = open(os.path.join(
                directory,
                BEAM_LRS_NAME_NAME
            ))
            image_stats['name'] = fb_name_file.read()
            fb_name_file.close()
        except IOError:
            image_stats['name'] = image_stats['title']

        try:
            fb_name_file = open(os.path.join(
                directory,
                BEAM_LRS_DESC_NAME
            ))
            image_stats['desc'] = fb_name_file.read()
            fb_name_file.close()
        except IOError:
            pass # use previous desc

    return image_stats
