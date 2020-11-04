import re

from zhihu.document.html import Parsing
from io import StringIO


class Markdown:
    functions = {
        'div': 'code',
        'figure': 'figure',
        'a': 'url',
        'img': 'math',
        'br': 'newline',
        'hr': 'horizontal',
        'sup': 'superscript',
        'blockquote': 'quote',
        'p': 'paragraph',
        'ol': 'table',
        'ul': 'table',
        'hx': 'font_style',
        'em': 'font_style',
        'strong': 'font_style',
        'b': 'font_style',
        'i': 'font_style',
        'u': 'font_style',
        'li': 'font_style'
    }

    warp = (None, 'sup', 'img', 'a', 'div', 'figure', 'br', 'hr', 'blockquote', 'ol', 'ul')
    emphasize = ('em', 'strong', 'b', 'i')
    split = ('p' 'br', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6')

    def __init__(self, content, meta, remove_media):
        self.tags = Parsing().parse_tag(content)
        self.reference_list = list()
        self.remove_media = remove_media
        self.meta = meta
        self.content = content

    def write_down(self, outfile):

        if bool(self.meta.background):
            background = '![背景大图](%s)\n\n' % self.meta.background
            outfile.write(background)

        title = '# [%s](%s)\n\n' % (self.meta.title, self.meta.source_url)
        outfile.write(title)

        split_line = '-' * len(title) + '\n\n'
        outfile.write(split_line)

        if bool(self.meta.author_avatar_url):
            head_img = '![%s](%s "%s")&emsp;' % (
                self.meta.author, self.meta.author_avatar_url, self.meta.author)
            outfile.write(head_img)

        if bool(self.meta.created_date):
            author = '**[%s](%s) / %s**\n\n' % (
                self.meta.author, self.meta.author_homepage, self.meta.created_date)
        else:
            author = '**[%s](%s)\n\n' % (self.meta.author, self.meta.author_homepage)

        outfile.write(author)

        formatter = self.format(
            self.tags,
            self.reference_list,
            remove_media=self.remove_media
        )

        outfile.write(formatter)

        if len(self.reference_list) != 0:
            for ref in self.reference_list:
                reference = '[%s] [%s](%s)\n\n' % (ref.get('index'), ref.get('text'), ref.get('url'))
                outfile.write(reference)

    @classmethod
    def format(cls, tags, reference_list, remove_media=False, level=1):
        content = StringIO()
        for tag in tags:
            if tag.name == 'figure' and remove_media:
                continue

            warp = cls.format_tag(
                tag=tag,
                reference_list=reference_list,
                level=level
            )

            if tag.name not in cls.warp:
                inner = cls.format(tag.contents, reference_list, remove_media, level + 1)
                warp = warp.format(inner=inner)
            content.write(warp)

        string_content = content.getvalue()
        content.close()
        return string_content

    @classmethod
    def format_tag(cls, **kwargs):

        tag_name = kwargs.get('tag').name

        if tag_name is None:
            return cls.string(**kwargs)

        if re.match(r'h\d', tag_name):
            tag_name = 'hx'

        handle_function = getattr(cls, cls.functions.get(tag_name, 'unsupported'))

        return handle_function(**kwargs)

    @classmethod
    def string(cls, **kwargs):
        return kwargs.get('tag').string

    @classmethod
    def superscript(cls, **kwargs):
        """处理sup标签，知乎标准的文献引用样式"""

        data_url = kwargs.get('tag').get_attrs('data-url')
        index = kwargs.get('tag').get_attrs('data-numero')
        data_text = kwargs.get('tag').get_attrs('data-text')

        kwargs.get('reference_list').append(
            {'text': data_text or data_url, 'url': data_url, 'index': index})

        return ' ^[%s]^ ' % index

    @classmethod
    def math(cls, **kwargs):
        if kwargs.get('level') == 1:
            return '$$\n%s\n$$\n\n' % kwargs.get('tag').get_attrs('alt')
        else:
            return ' $%s$ ' % kwargs.get('tag').get_attrs('alt')

    @classmethod
    def link(cls, **kwargs):
        url = kwargs.get('tag').get_attrs('href')
        try:
            assert isinstance(url, str)
        except AssertionError:
            print(kwargs.get('tag'))
            raise AssertionError
        if not bool(re.match(r'http', url)):
            url = 'https://www.zhihu.com' + url
        link_title = kwargs.get('tag').string

        if kwargs.get('tag').find('a', **{'type': 'link-card'}) is not None:
            length = 85

            ascii_reg = '[{ascii32}-{ascii126}]'.format(ascii32=chr(32), ascii126=chr(126))
            one_grid = len(re.findall(ascii_reg, link_title))
            two_grid = 2 * (len(link_title) - one_grid)

            if one_grid + two_grid < length:
                line = '-' * ((length - one_grid - two_grid) // 2)
                return f'***\n+%s+|%s|+%s+\n***\n\n' % (line, link_title, line)

        return '[%s](%s)' % (link_title, url)

    @classmethod
    def code(cls, **kwargs):
        if kwargs.get('tag').get_attrs('class', None) != 'highlight':
            return ''
        try:
            lang = re.sub(
                r'[+\d\s]+', '',
                re.search(r'"language-([^()]+)">', kwargs.get('tag').string).group(1)
            )
        except AttributeError:
            lang = 'text'

        def stg(r):
            return {'&quot;': '"', '&#39;': "'", '&lt;': '<', '&gt;': '>'}.get(r.group(0), '')

        code = re.sub(r'(</?(\w+)[^<>]*>)|(&quot;)|(&[\w#]+;)', stg, kwargs.get('tag').string)

        return '```%s\n%s\n```\n\n' % (lang, code)

    @classmethod
    def figure(cls, **kwargs):
        img = kwargs.get('tag').find('img')
        url = img.get_attrs('data-original') or img.get_attrs('src')

        try:
            title = kwargs.get('tag').find('figcaption').string
        except AttributeError:
            title = ''

        return '![%s](%s)%s\n***\n\n' % (title, url, title)

    @classmethod
    def url(cls, **kwargs):
        """处理a标签，视频、卡片链接、广告、普通链接"""
        if kwargs.get('tag').find('a', _class='video-box') is not None:
            return cls.video(**kwargs)
        elif kwargs.get('tag').find('a', attrs={'data-draft-type': 'mcn-link-card'}) is not None:
            # 广告，tag自动过滤None
            return ''
        else:
            return cls.link(**kwargs)

    @classmethod
    def video(cls, **kwargs):
        video_link = kwargs.get('tag').find('span', _class='url').string
        cover_link = kwargs.get('tag').find('img').get_attrs('src')
        video_title = kwargs.get('tag').find('span', _class='title').string or '视频'

        return '![](%s)\n[%s](%s): %s\n\n' % (cover_link, video_title, video_link, video_link)

    @classmethod
    def newline(cls, **kwargs):
        return '\n'

    @classmethod
    def horizontal(cls, **kwargs):
        return '***\n\n'

    @classmethod
    def quote(cls, **kwargs):
        quote_tag = kwargs.pop('tag')
        content = list()
        quote_span = '> '
        content.append(quote_span)
        for tag in quote_tag.contents:
            warp = cls.format_tag(tag=tag, **kwargs)

            if tag.name not in cls.warp:
                inner = cls.format(tag.contents, **kwargs)
                content.append(warp.format(inner=inner))

            if tag.name in cls.split:
                content.append(quote_span)

        if content[-1] == quote_span:
            content.pop()
        return ''.join(content) + '\n\n'

    @classmethod
    def table(cls, **kwargs):
        def index(t):
            if t == 'ul':
                while True:
                    yield '- '
            else:
                i = 1
                while True:
                    yield str(i) + '. '
                    i += 1

        table_tag = kwargs.pop('tag')
        content = list()
        ind = index(table_tag.name)
        for tag in table_tag.contents:
            content.append(next(ind) + cls.format(tag.contents, **kwargs) + '\n')

        return ''.join(content) + '\n\n'

    @classmethod
    def font_style(cls, **kwargs):
        if re.match(r'h\d', kwargs.get('tag').name):
            return '%s {inner}\n\n' % ('#' * int(re.search(r'\d', kwargs.get('tag').name).group()))
        elif kwargs.get('tag').name in cls.emphasize:
            return ' **{inner}** '
        else:
            return ' *{inner}* '

    @classmethod
    def unsupported(cls, **kwargs):
        return '[unsupported, %s: {inner}]' % kwargs.get('tag').name

    @classmethod
    def paragraph(cls, **kwargs):
        if kwargs.get('tag').get_attrs('class') == 'ztext-empty-paragraph':
            return '{inner}'
        else:
            return '{inner}\n\n'
