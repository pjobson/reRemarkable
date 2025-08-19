# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

import optparse, sys
from locale import gettext as _

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk # pylint: disable=E0611

from reremarkable import reRemarkableWindow

from reremarkable_lib import set_up_logging, get_version

def parse_options():
    """Support for command line options"""
    parser = optparse.OptionParser(version="%%prog %s" % get_version())
    parser.add_option(
        "-v", "--verbose", action="count", dest="verbose",
        help=_("Show debug messages (-vv debugs reremarkable_lib also)"))
    (options, args) = parser.parse_args()

    set_up_logging(options)

def main():
    'constructor for your class instances'
    parse_options()

    # Run the application.    
    window = reRemarkableWindow.RemarkableWindow()

    window.show_all()
    Gtk.main()
