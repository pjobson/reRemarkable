# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

from locale import gettext as _

import logging
logger = logging.getLogger('reremarkable')

from reremarkable_lib.AboutDialog import AboutDialog

# See reremarkable_lib.AboutDialog.py for more details about how this class works.
class AboutReRemarkableDialog(AboutDialog):
    __gtype_name__ = "AboutReRemarkableDialog"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the about dialog"""
        super(AboutReRemarkableDialog, self).finish_initializing(builder)

        # Code for other initialization actions should be added here.

