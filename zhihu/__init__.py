__version__ = '1.8'
__name__ = 'Zhihu Favorite'


class Document:
    def __init__(self, meta, content):
        self.meta = meta
        self.content = content
        self.images = list()

    def convert2(self, converter, file):
        file.write(converter(self).tostring())


class DocBuilder:
    def __init__(self, doc: Document):
        self.doc = doc


class MarkdownBuilder(DocBuilder):
    pass


class HtmlBuilder(DocBuilder):
    pass
