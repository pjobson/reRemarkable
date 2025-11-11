import subprocess
import sys


class Configuration:
    def __init__(self, wkhtmltopdf='', meta_tag_prefix='pdfkit-'):
        self.meta_tag_prefix = meta_tag_prefix

        self.wkhtmltopdf = wkhtmltopdf

        if not self.wkhtmltopdf:
            if sys.platform == 'win32':
                self.wkhtmltopdf = subprocess.Popen(
                    ['where', 'wkhtmltopdf'], stdout=subprocess.PIPE).communicate()[0].strip()
            else:
                self.wkhtmltopdf = subprocess.Popen(
                    ['which', 'wkhtmltopdf'], stdout=subprocess.PIPE).communicate()[0].strip()

        try:
            with open(self.wkhtmltopdf):
                pass
        except OSError:
            raise OSError(f'No wkhtmltopdf executable found: "{self.wkhtmltopdf}"\n'
                          'If this file exists please check that this process can '
                          'read it. Otherwise please install wkhtmltopdf - '
                          'https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf')
