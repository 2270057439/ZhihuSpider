import re
import sys
import time
import os.path as osp


def escape_file_path(path):
    def stg(r):
        return {'?': '？'}.get(r.group(0), '#')

    return re.sub(r'[\\/:*?"<>|]', stg, path)


def timestamp_to_date(time_stamp: int = None, ft: str = None):
    if ft is None:
        ft = '%Y-%m-%d'
    # if time_stamp is None, time.localtime() will use time.time() as time_stamp
    return time.strftime(ft, time.localtime(time_stamp))


def timestamp():
    return str(int(time.time()))


def format_style_sheet(css):
    def stg(r):
        if '{' in r.group():
            return '{'
        elif '}' in r.group():
            return '}'
        else:
            return ''

    return re.sub(
        r'(/\*[\s\S]*?\*/)|(\n)|(\s{2,})|(\s*{\s*)|(\s*}\s*)', stg, css)


def yes_or_no(msg):
    msg = f'{msg}(y/N):'
    inp = input(msg)
    if inp.lower() == 'y':
        return True
    else:
        return False


def print_resp_headers(resp):
    for key, value in resp.headers.items():
        print('{:>20}: {}'.format(key, value))

    print('*' * 30)


def str_length(stg):
    stg_len = len(stg)
    asc_len = len(re.findall('[%s-%s]' % (chr(32), chr(126)), stg))
    return (stg_len - asc_len) * 2 + asc_len


def getvalue(data, key):
    """
    用以/分隔的字符串来获取嵌套的字典（值）
    如：'a/b/c' get 0 in {'a':{'b': {'c': 0}, 'f': 456}, 'g': 123}
    :param data: data, dict type
    :param key: path, string type
    :return: any, include None.
    """
    ptk = key.split('/')
    a = data
    try:
        for k in ptk:
            a = a.get(k)
            assert a is not None
        return a
    except AssertionError:
        raise KeyError('Key Error: "%s"' % key)


def search_image(text):
    """
    # 正则表达式搜索html文本中的图片链接
    # 结果构成：(image_link, image_file_name, image_name, resolution, format)
    # for example:
    # ('https://pic3.zhimg.com/v2-6ee2f3d3ba6fac2deabc5ee6c2ed2b42_b.jpg',
    # '6ee2f3d3ba6fac2deabc5ee6c2ed2b42_b.jpg', '6ee2f3d3ba6fac2deabc5ee6c2ed2b42', 'b', 'jpg')
    :param text: html text
    :return: list, which compose of (image_link, image_file_name, image_name, hvga, format)
    """

    search_regular_expression = re.compile(
        r'(https://pic\d.zhimg.com/(?:\d+/)?v\d-((\w+)_([brl]).(jpg|gif|webp|png|jpeg))(?:[?&=a-zA-z0-9]+)?)'
    )
    image_search_result_list = search_regular_expression.findall(text)

    # 去重，挑选特定格式、分辨率高的图片
    # 优先选gif图片，再依据分辨率挑选图片
    images_dict = dict()
    # 权重定义，分辨率、格式
    resolution3 = {'r': 3, 'b': 2, 'l': 1}
    format4 = {'gif': 5, 'png': 3, 'jpg': 2, 'jpeg': 2, 'webp': 1}
    for image_msg in image_search_result_list:
        image_name = image_msg[2]
        if images_dict.get(image_name, None) is not None:
            r_weight = resolution3.get(image_msg[3]) * format4.get(image_msg[4])
            i_weight = resolution3.get(images_dict[image_name][3]) * format4.get(images_dict[image_name][4])
            if r_weight > i_weight:
                images_dict[image_name] = image_msg
        else:
            images_dict[image_name] = image_msg

    return list(images_dict.values())


class ProcessBar:
    def __init__(self, length, totals, /,
                 *,
                 count=0,
                 msg: str = '',
                 style: str = '#',
                 fill: str = '',
                 wrap: str = '[]',
                 percent: bool = True,
                 ):
        """
        @param length: 进度条总长度
        @param totals: 进度总量
        @param count: 当前累计进度总量
        @param style: 进度填充字符，'#'
        @param fill: 未完成段填充字符，''
        @param wrap: 包裹进度条的字符，[], {}, (), ect.只提供一个字符将在始末短使用相同的字符，
        2及个以上字符将在起始段使用第一个字符，其余字符用在末尾端
        @param percent: 进度条末尾添加百分比进度，整数值，50%
        """
        self.totals = totals
        self.length = length
        self.count = count

        self.style = style
        self.fill = fill
        self.wrap = wrap
        self.percent = percent
        self.msg = msg

    def process(self, size):
        """
        在file中刷新进度条，file: StringIO, 默认sys.stdout
        """
        self.count += size
        sys.stdout.write(self.msg)
        sys.stdout.write(self.__format())
        sys.stdout.write('\r')

        if self.is_finish():
            self.done()

    def __format(self):
        percent_str = ''
        length = self.length
        if self.percent:
            percent_str = ' {:<4.0%}'.format(self.count / self.totals)
            length = length - len(percent_str)

        start = end = ''
        if len(self.wrap) == 1:
            start = end = self.wrap
        elif len(self.wrap) >= 2:
            start = self.wrap[0]
            end = self.wrap[1:]

        length = length - len(self.wrap)
        process = int(length / self.totals * self.count)

        return start + self.style * process + self.fill * (length - process) + end + percent_str

    def done(self):
        sys.stdout.write(self.msg)
        sys.stdout.write(self.__format())
        sys.stdout.write('\n')

    def is_finish(self):
        return self.count >= self.totals


class DoubleProcessBar:
    A = (chr(92), chr(124), chr(47), chr(45))

    def __init__(self, length):
        self.length = length

        self.first = 0
        self.second = 0

    def process_first(self, totals):
        self.first += 1
        self.__refresh()

    def process_second(self, totals):
        self.second += 1
        self.__refresh()

    def __refresh(self):
        sys.stdout.write(
            '收藏 {} <{}> 图片 {} <{}>\r'.format(
                self.A[self.first % len(self.A)],
                self.first,
                self.A[self.second % len(self.A)],
                self.second
            )
        )

    def done(self):
        sys.stdout.write(
            '收藏 - <{}> 图片 - <{}>\n'.format(
                self.first, self.second
            )
        )


class BeautifulTable:
    __BASE_LEN = 11
    __MINI_BAR_LEN = 50
    MIN_LEN = __BASE_LEN + __MINI_BAR_LEN

    def __init__(self, bar_name: str):
        self.bars = dict()
        self.name = bar_name.title()
        self.title = None
        self.save_to = None

        self.__use_double_process_bar = False

        self.__line_len = 0
        self.__bar_len = 0

        self.__finished = True
        self.__is_close = False
        self.__have_show = False

    @property
    def double_process_bar(self):
        return self.__use_double_process_bar

    def show_interface(self, management):
        self.__have_show = True
        self.title = management.title
        self.save_to = management.work_dir

        dir_name = osp.basename(management.work_dir)
        root = osp.dirname(management.work_dir)
        dl = str_length(dir_name)
        rl = str_length(root)

        if dl + rl + self.__BASE_LEN > 100:
            if dl > 14:
                dir_name = dir_name[:4] + '...' + dir_name[-4:]
                self.save_to = root + '\\' + dir_name
            else:
                self.save_to = self.save_to[:100 - self.__BASE_LEN - 3] + '...'

        self.__line_len = max([
            str_length(management.title),
            str_length(self.save_to), self.__BASE_LEN,
            self.MIN_LEN
        ])

        self.__bar_len = self.__line_len - self.__BASE_LEN

        # vote_up = "Answer_Article_Video_点赞"
        collection = ["Question", "Column", "Collection", "User"]

        # 批量型(Question ect)任务输出收藏数，单一型(Answer ect)任务输出点赞数
        num = management.vote_up if management.totals == 1 else management.totals
        clo_upv = ('收藏：%s' if self.name in collection else '点赞：%s') % num

        table_head = f':: {self.name} :: | {clo_upv} | {self.title}'
        if not (str_length(table_head) + 3 <= self.__line_len):
            table_head = f':: {self.name} :: | {clo_upv}\n{self.title}'

        print(
            '=' * self.__line_len,
            table_head,
            '*' * self.__line_len,
            sep='\n'
        )

    def close(self, show_path=True):
        if not self.__have_show:
            return

        if not self.__is_close:
            if self.double_process_bar:
                self.bars.get('double_process_bar').done()

            if not self.__finished:
                print('')

            if show_path:
                print(f':: 保存至：[{self.save_to}]')

            print(
                '=' * self.__line_len, sep='\n',
                end='\n\n'
            )
            self.__is_close = True

    @double_process_bar.setter
    def double_process_bar(self, value):
        assert isinstance(value, bool)
        if value:
            self.bars['double_process_bar'] = DoubleProcessBar(self.__line_len)

        else:
            try:
                self.bars.pop('double_process_bar')
            except KeyError:
                pass
        self.__use_double_process_bar = value

    def text_process(self, totals, /, size=1):
        if self.double_process_bar:
            self.bars.get('double_process_bar').process_first(totals)
        else:
            self.__refresh('text_process_bar', totals=totals, size=size, msg=':: 已收藏：')

    def image_process(self, totals, /, size=1):
        if self.double_process_bar:
            self.bars.get('double_process_bar').process_second(totals)
        else:
            self.__refresh('image_process_bar', totals=totals, size=size, msg=':: 图\u3000片：')

    def download_process(self, totals, size):
        self.__refresh('download', totals=totals, size=size, msg=':: 下\u3000载：')

    def show_msg(self, msg, new_line=True):
        if not self.__finished:
            print('')
        if new_line:
            print(msg, end='\n')
        else:
            print(msg, end='')

    def __refresh(self, name, totals, size, msg):
        if not self.bars.get(name, None):
            self.bars[name] = ProcessBar(self.__bar_len, totals, msg=msg)
        process_bar = self.bars[name]
        process_bar.process(size)
        self.__finished = process_bar.is_finish()
