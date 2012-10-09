# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id: lbx_gtk_widgets.py 58 2010-02-11 12:51:34Z nicolas $
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

"""Linbox's custom GTK widgets

Classes:
    LbxComboBox(gtk.ComboBox): a simple combo box
    LbxNavButton             : nav buttons for a wizard
    LbxBook                  : a GTK VBox containing some LbxPages
    LbxPage                  : a GTK Frame
    LbxImgButton             : a GTK Button with an image inside
    LbxImgToggleButton       : a GTK Toggle Button with an image inside
    LbxImgCheckButton        : a GTK Check Button with an image inside
    LbxErrorDialog           : an error dialog

Functions:
    get_widget_r(widget, name) => the "name" child of the GTK widget
    lbx_error(label, message)  => display a nice error
"""

__author__    = "Nicolas Rueff <nicolas.rueff@linbox.com>"
__version__   = "$Rev: 58 $"
__date__      = "$Date: 2007-05-31 16:57:13 +0200 (jeu, 31 mai 2007) $"
__licence__   = "GPL"
__copyright__ = "© 2007 Nicolas Rueff - Linbox F&AS"

import pygtk
pygtk.require('2.0')
import gtk
import gobject

class LbxComboBox(gtk.ComboBox):
    """ Simple GTK ComboBox using a fullfilled GtkTree, with 2 columns
    - first columns is used to display the human-readable value,
    - second to stock the non-readable value.
    Methods:
        LbxComboBox(self, list): instantiate a ComboBox using the given list
        set_items(self, list): display list in the ComboBox
    """

    def __init__(self, items=None, width=200, heigth=30, margin=10):
        """ Instantiate a new LbxComboBox
        Returns a new LbxComboBox pre-filled with list
        ComboBox geometry default to 200x30 + 10 margin
        list should be a list of tuples
        """
        gtk.ComboBox.__init__(
            self,
            gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        )
        cell = gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)
        self.set_size_request(width, heigth)
        self.set_border_width(margin)
        self.set_items(items)

    def set_items(self, items):
        """ Fill a LbxComboBox
        list should be a list of tuples
        """
        p_tree_model = self.get_model()
        p_tree_model.clear()
        if items:
            for i in items:
                p_tree_model.append(i)

class LbxNavButton(gtk.HButtonBox):
    """ Simple GTK HButtonBox containing 2 buttons, to be used in a wizard
    - first button, namely "button_prev", on the left,
    - second button, namely "button_next", on the right,

    Methods:
        LbxComboBox(self): instantiate a HButtonBox
        get_button_prev(self): return the leftmost button
        get_button_next(self): return the rightmost button
    """

    def __init__(self, buttons=(
            ("Previous", 'gtk-go-back'),
            ("Next", 'gtk-go-forward')
            )):
        """ Instantiate a new LbxNavButton
        buttons is an array of (label, image) (one per button)
        Returns a new LbxNavButton
        FIXME: i18n
        """
        gtk.HButtonBox.__init__(self)

        count = 0
        for i in buttons:
            button = LbxImgButton(i[0], i[1])
            button.set_name("navbutton_%d" % count)
            self.add(button)
            count += 1
        self.connect("show", self._cb_show)

    def get_button_prev(self):
        """ Return the "previous" button
        """
        return get_widget_r(self, "button_prev")

    def get_button_next(self):
        """ Return the "next" button
        """
        return get_widget_r(self, "button_next")

    def _cb_show(self, widget):
        """ Used to override the "show" event
        """
        #button_next = get_widget_r(widget, "navbutton_1")
        #button_next.set_flags(gtk.CAN_DEFAULT)
        #button_next.grab_default()
        #button_next.grab_focus()
        pass

class LbxBook(gtk.VBox):
    """ Simple GTK VBox containing a handful of LbxPages
    Methods:
        LbxBook(self, list): instantiate a VBox
        add_page(self, page,): add (and show) a LbxPage
    """
    def __init__(self):
        """ Instantiate a new LbxBook
        """
        gtk.VBox.__init__(self)
        self.pages = []
        self.accel_group = gtk.AccelGroup()

    def add_page(self, page):
        """ Add a LbxPage to the book
            Add to "page" to self
        """
        self.pages.append(page)
        page.set_book(self)
        self.pack_start(page, True, True)

    def hide_all_pages(self):
        """ Hide all pages
        """
        for i in self.pages:
            i.hide_all()

    def hide_page(self, page):
        """ Hide given page
        Hide the page'th page of the book
        """
        self.book[page].hide_all()

    def show_page(self, pagename):
        """ Show given page
        Show the "pagename" page of the book, hide others
        """
        self.hide_all_pages()
        for page in self.pages:
            if (page.get_name() == pagename):
                page.set_no_show_all(False)
                page.show_all()

    def get_page(self, pagename):
        """ Get given page
        Returns the "pagename" page of the book
        """
        for page in self.pages:
            if (page.get_name() == pagename):
                return page
        return None

class LbxPage(gtk.Frame):
    """ Simple GTK Frame
        A page for a LbxBook
    """
    def __init__(self, name=None, label=None, resume=None, book=None):
        """ Instantiate a new LbxPage
        The frame label contant will be "label"
        The page will belong to the LbxBook "book"

        The label is using a markup (aka HTML) language
        """
        gtk.Frame.__init__(
            self,
            "<span weight='bold' size='x-large'>%s</span>" % label
        )
        self.book = None
        self.set_book(book)
        self.set_name(name)

        # main box
        mainbox = gtk.VBox()

        # customize frame
        self.set_label_align(0, 1)
        self.set_shadow_type(gtk.SHADOW_NONE)
        self.get_label_widget().set_padding(5, 5)
        self.get_label_widget().set_use_markup(True)

        self.accel_group = gtk.AccelGroup()

        # customize top label
        img = gtk.Image()
        img.set_from_file('media/mandriva.png')
        label = self.get_label_widget()
        topbox = gtk.HBox()
        topbox.add(img)
        self.set_label_widget(topbox)
        topbox.add(label)

        # first item: a horiz line
        hbar1 = gtk.HSeparator()

        # second item: a viewport containing a label
        # this label will contain the page help
        summary = gtk.Label()
        summary.set_line_wrap(True)
        summary.set_use_markup(True)
        summary.set_size_request(-1, -1)
        summary.set_padding(5, 5)
        # FIXME: to handle label realtime resize
        summary.connect("event", self._test)
        summary.set_text(resume)
        gtk.Misc.set_alignment(summary, 0, 0)
        summary.set_use_markup(True)

        viewport1 = gtk.ScrolledWindow()
        viewport1.set_size_request(-1, 140)
        viewport1.set_shadow_type(gtk.SHADOW_NONE)
        viewport1.add_with_viewport(summary)
        viewport1.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        # third item: a horiz line
        hbar2 = gtk.HSeparator()

        # fourth item: a veiwport containing our box
        self.contentbox = gtk.VBox()
        viewport2 = gtk.ScrolledWindow()
        viewport2.set_size_request(-1, -1)
        viewport2.set_shadow_type(gtk.SHADOW_NONE)
        viewport2.add_with_viewport(self.contentbox)
        viewport2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        # fifth item: a veiwport containing our button box
        self.buttonbox = gtk.VBox()

        mainbox.pack_start(hbar1, False, True, 0)
        mainbox.pack_start(viewport1, False, True, 5)
        mainbox.pack_start(hbar2, False, True, 0)
        mainbox.pack_start(viewport2, True, True, 0)
        mainbox.pack_start(self.buttonbox, False, True, 0)
        self.add(mainbox)

        label.show()
        img.show()
        topbox.show()
        self.connect("show", self._cb_show)
        self.connect("hide", self._cb_hide)

    def get_contentbox(self):
        """ return the containing box
        """
        return self.contentbox

    def get_buttonbox(self):
        """ return the containing box
        """
        return self.buttonbox

    def set_book(self, book):
        """ Set the book whose the page belong to
        """
        self.book = book

    def get_book(self):
        """ Get the book whose the page belong to
        """
        return self.book

    def _cb_show(self, widget=None):
        """ Used to override the "show" event
        """
        #self.get_toplevel().add_accel_group(accel_group)

    def _cb_hide(self, widget=None):
        """ Used to override the "hide" event
        """
        #self.get_toplevel().remove_accel_group(accel_group)

    def _test(self, event, widget=None, data=None):
        """ Simple test function
        """
        pass


class LbxImgButton(gtk.Button):
    """ Simple GTK Button with an image inside
    Methods:
        LbxImgButton(self, label, img): instantiate a VBox
    """
    def __init__(self, label=None, img=None):
        """ Instantiate a new LbxImgButton
        The Button label will be "label"
        The Button image will be the stock image "img"
        """
        gtk.Button.__init__(self)
        image = gtk.Image()
        image.set_from_stock(img, gtk.ICON_SIZE_BUTTON)

        label = gtk.Label(label)
        label.set_use_markup(True)
        label.set_padding(10, 0)

        box = gtk.HBox()
        box.add(image)
        box.add(label)

        align = gtk.Alignment(0.5, 0.5)
        align.add(box)

        self.add(align)

class LbxImgToggleButton(gtk.ToggleButton):
    """ Simple GTK Toggle Button with an image inside
    Methods:
        LbxImgToggleButton(self, label, img): instantiate a VBox
    """
    def __init__(self, label='', img=''):
        """ Instantiate a new LbxImgToggleButton
        The Button label will be "label"
        The Button image will be the stock image "img"
        """
        gtk.ToggleButton.__init__(self)
        image = gtk.Image()
        image.set_from_stock(img, gtk.ICON_SIZE_BUTTON)

        label = gtk.Label(label)
        label.set_use_markup(True)

        box = gtk.HBox()
        box.add(image)
        box.add(label)

        align = gtk.Alignment(0.5, 0.5)
        align.add(box)

        self.add(align)

class LbxImgCheckButton(gtk.CheckButton):
    """ Simple GTK Check Button with an image inside
    Methods:
        LbxImgCheckButton(self, label, img): instantiate a VBox
    """
    def __init__(self, label=''):
        """ Instantiate a new LbxImgCheckButton
        The Button label will be "label"
        The Button image will be the stock image "img"
        """
        gtk.CheckButton.__init__(self)

        label = gtk.Label(label)
        label.set_use_markup(True)

        box = gtk.HBox()
        box.add(label)

        align = gtk.Alignment(0, 0)
        align.add(box)

        self.add(align)

class LbxErrorDialog(gtk.MessageDialog):
    """ An error dialog

    Message will be shown in a nice modal window
    Methods:
        LbxErrorDialog(self, label, message): instantiate a message
    """
    def __init__(self, label=None, message=None):
        gtk.MessageDialog.__init__(
            self,
            None,
            gtk.DIALOG_MODAL,
            gtk.MESSAGE_ERROR,
            gtk.BUTTONS_CLOSE,
            message
        )
        self.set_title(label)
        # TODO: lambda ?
        self.connect("response", lambda self, response: self.destroy())

def lbx_error(label, message):
    """ Display an error message using given label and message
    """
    errordlg = LbxErrorDialog(label, message)
    errordlg.run()

def get_widget_r(widget, name):
    """ Return the "name" child of thewidget
        Using a recursive algo, found and return the first child whose name
        matches "name"
    """
    try:
        for child in widget.get_children():
            if child.get_name() == name:
                return child
            else:
                result = get_widget_r(child, name)
                if result != None:
                    return result
        return None
    except AttributeError:
        return None
