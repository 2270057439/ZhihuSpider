import os

from zhihu.auxiliary import work_dir, data
from zhihu.document import markdown, html
from zhihu.util import format_style_sheet


class Meta:
    __slots__ = (
        'title', 'voteup', 'author', 'content', 'author',
        'identity', 'background', 'source_url',
        'created_date', 'author_homepage', 'author_avatar_url'
    )

    def __init__(
            self,
            title: str = None,
            voteup: int = None,
            author: str = None,
            content: str = None,
            identity: str = None,
            background: str = None,
            source_url: str = None,
            created_date: str = None,
            author_homepage: str = None,
            author_avatar_url: str = None,
    ):
        self.title = title
        self.voteup = voteup
        self.author = author
        self.content = content
        self.identity = identity
        self.background = background
        self.source_url = source_url
        self.created_date = created_date
        self.author_homepage = author_homepage
        self.author_avatar_url = author_avatar_url

    def __str__(self):
        return '\n'.join(
            ['{}: {}'.format(k, v) for k, v in
             sorted(
                 [(k, getattr(self, k)) for k in self.__slots__],
                 key=lambda x: len(x[0]))]
        )

    def __setattr__(self, key, value):
        if value is not None:
            if key == 'voteup':
                value = int(value)
            else:
                value = str(value)

        super(Meta, self).__setattr__(key, value)


class Document:
    @classmethod
    def item2html(cls, meta, css_output, remove_media):
        mushroom = html.Mushroom(meta)

        formatter = html.Formatter(meta.content, remove_media)
        formatter.formatter(meta, mushroom)

        styles = mushroom.style_meta

        if css_output:
            for s in styles:
                file = work_dir.get_file_name(s + '.css')
                mushroom.link_css_file(file)
                if not os.path.exists(file):
                    with open(file, 'w', encoding='utf8') as foo:
                        foo.write(data.template(s))
        else:
            for s in styles:
                css = format_style_sheet(data.template(s))
                mushroom.insert_css_code(css)

        htm_file = work_dir.generate_file_name(
            (meta.title, meta.identity, str(meta.voteup), meta.author),
            'html'
        )

        with open(htm_file, 'w', encoding='utf8') as foo:
            mushroom.write_down(foo)

        return mushroom

    @classmethod
    def item2md(cls, meta, remove_media):
        md = markdown.Markdown(meta.content, meta, remove_media)

        md_file = work_dir.generate_file_name(
            (meta.title, meta.identity, str(meta.voteup), meta.author),
            'md'
        )

        with open(md_file, 'w', encoding='utf8') as foo:
            md.write_down(foo)

        return md
