
from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagPattern

reg_pattern =r'(~{2})([^\?]+?)(~{2})'

class Strikethrough(Extension):
    def extendMarkdown(self, md, md_globals):
        """Modifies inline patterns."""
        mark_tag = SimpleTagPattern(reg_pattern, 'del')
        md.inlinePatterns.add('del', mark_tag, '_begin')

def makeExtension(configs=None):
    if configs is None:
        configs = []
    return Strikethrough(configs)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
