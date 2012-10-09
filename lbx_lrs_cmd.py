# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id: lbx_lrs_cmd.py 52 2010-02-11 09:08:24Z nicolas $
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

"""Class to handle LRS backups

Classes:
    LrsThread: to handle LRS binary

"""
__author__    = "Nicolas Rueff <nicolas.rueff@linbox.com>"
__version__   = "$Rev: 52 $"
__date__      = "$Date: 2007-05-31 16:57:13 +0200 (jeu, 31 mai 2007) $"
__licence__   = "GPL"
__copyright__ = "© 2007 Nicolas Rueff - Linbox F&AS"

import os
import gtk
import logging

from beam_consts import *

def halt_backup(pid):
    """ Halt a backup using it's pid (using SIGKILL)
    """
    if pid != None and pid != 0:
        logging.info("LRS Process %d killed" % pid)
        os.killpg(os.getpgid(pid), 9)
    return False

def run_backup(savepath, binpath, exclude, name, desc, mainwindow):
    """ run a backup using LRS binaries

    Return the LRS pid
    """
    # FIXME: autosave is hardcoded
    autosavepath = os.path.join(binpath, BEAM_LRS_AUTOSAVE_NAME)

    try: # attempt to create our save dir
        os.mkdir(savepath)
        logging.info("Creating savepath: |%s|" % savepath)
    except OSError, (errno, strerror): # hum, something happen
        if errno == 17: # dir exists: don't do anything ? (FIXME: should empty)
            pass
        else:
            # FIXME: should exit ?
            logging.error(
                "Creation of savepath |%s| failed: %s" %
                (savepath, strerror)
            )

    infopath = os.path.join(savepath, BEAM_LRS_MISC_FOLDER)
    realsavepath = os.path.join(savepath, BEAM_LRS_SAVE_FOLDER)
    realrestorepath = os.path.join(savepath, BEAM_LRS_RESTORE_FOLDER)

    for i in (realsavepath, realrestorepath, infopath):
        try: # attempt to create our real save dir
            os.mkdir(i)
            logging.info("Creating savepath: |%s|" % i)
        except OSError, (errno, strerror): # hum, something happen
            if errno == 17: # dir exists: clean it
                # clean dir (should only contain files)
                logging.info("Cleaning savepath |%s|" % i)
                for file_in_i in os.listdir(i):
                    os.unlink(os.path.join(i, file_in_i))
            else:
                # FIXME: should exit ?
                logging.error(
                    "Creation of |%s| failed: %s" %
                    (i, strerror)
                )

    file_exclude = open(os.path.join(infopath, BEAM_LRS_EXCLUDE_NAME), 'w')
    logging.info("Creating exclude: |%s|" % infopath)
    try:
        logging.debug("Exclude contains: %s" % exclude)
        file_exclude.write(exclude)
        file_exclude.close()
    except IOError, (errno, strerror):
        logging.error("Creation of exclude failed: %s" %
            (savepath, strerror)
        )

    file_name = open(os.path.join(savepath, BEAM_LRS_NAME_NAME), 'w')
    try:
        logging.debug("Name contains: %s" % name)
        file_name.write(name)
        file_name.close()
    except IOError, (errno, strerror):
        logging.error("Creation of name failed: %s" %
            (savepath, strerror)
        )

    file_desc = open(os.path.join(savepath, BEAM_LRS_DESC_NAME), 'w')
    try:
        logging.debug("Name contains: %s" % desc)
        file_desc.write(desc)
        file_desc.close()
    except IOError, (errno, strerror):
        logging.error("Creation of name failed: %s" %
            (savepath, strerror)
        )

    # run the LRS binaries in a separated fork
    try:
        pid = os.fork()
        if pid > 0: # exit first parent
            logging.debug("Fork succeded, LRS PID is: %d" % pid)
            return pid
    except OSError, (errno, strerror):
        logging.info("Fork failed: %s" % strerror)
        return False
    # decouple from parent environment
    mainwindow.socket.close()
    mainwindow.destroy()
    gtk.main_quit()
    os.chdir("/")
    os.setsid()
    os.umask(0)
    args = [autosavepath,
            '--nolrs',
            '--info', infopath,
            '--save', realsavepath,
            '--bin', binpath
    ]
    logging.debug("Exec LRS: %s" % args)
    os.execvpe(autosavepath, args, os.environ)

def run_restore(savepath, binpath, mainwindow):
    """ run a restore using LRS binaries

    Return the LRS pid
    """
    autorestorepath = os.path.join(binpath, BEAM_LRS_AUTORESTORE_NAME)
    realsavepath = os.path.join(savepath, BEAM_LRS_SAVE_FOLDER)
    realrestorepath = os.path.join(savepath, BEAM_LRS_RESTORE_FOLDER)

    try: # attempt to create our real save dir
        os.mkdir(realrestorepath)
        logging.info("Creating savepath: |%s|" % realrestorepath)
    except OSError, (errno, strerror): # hum, something happen
        if errno == 17: # dir exists: do not touch it
            pass
        else:
            # FIXME: should exit ?
            logging.error(
                "Creation of |%s| failed: %s" %
                (realrestorepath, strerror)
            )

    # run the LRS binaries in a separated fork
    try:
        pid = os.fork()
        if pid > 0: # exit first parent
            logging.debug("Fork succeded, LRS PID is: %d" % pid)
            return pid
    except OSError, (errno, strerror):
        logging.info("Fork failed: %s" % strerror)
        return False
    # decouple from parent environment
    mainwindow.socket.close()
    mainwindow.destroy()
    gtk.main_quit()
    os.chdir("/")
    os.setsid()
    os.umask(0)
    args = [autorestorepath,
            '--nolrs',
            '--info', realrestorepath,
            '--save', realsavepath,
            '--bin', binpath
    ]
    logging.debug("Exec LRS: %s" % args)
    os.execvpe(autorestorepath, args, os.environ)
