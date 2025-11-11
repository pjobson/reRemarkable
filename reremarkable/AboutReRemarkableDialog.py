

import logging

logger = logging.getLogger('reremarkable')

from reremarkable_lib.AboutDialog import AboutDialog


# See reremarkable_lib.AboutDialog.py for more details about how this class works.
class AboutReRemarkableDialog(AboutDialog):
    __gtype_name__ = "AboutReRemarkableDialog"

    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the about dialog"""
        super().finish_initializing(builder)

        # Code for other initialization actions should be added here.

