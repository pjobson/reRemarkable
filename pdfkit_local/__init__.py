"""
Wkhtmltopdf python wrapper to convert html to pdf using the webkit rendering engine and qt
"""

__author__ = 'Golovanov Stanislav'
__version__ = '0.4.1'
__license__ = 'MIT'

from .api import configuration, from_file, from_string, from_url
from .pdfkit import PDFKit
