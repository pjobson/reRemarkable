
from markdown.inlinepatterns import SimpleTagPattern
from markdown.extensions import Extension

reg_pattern =r'(={2})([^\?]+?)(={2})'  

class Highlighting(Extension): 
    def extendMarkdown(self, md, md_globals):
        """Modifies inline patterns."""
        mark_tag = SimpleTagPattern(reg_pattern, 'mark')
        md.inlinePatterns.add('mark', mark_tag, '_begin')
        
def makeExtension(configs=[]):
    return Highlighting(configs)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
