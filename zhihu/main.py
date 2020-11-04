import argparse
import re
import sys
import zhihu
from zhihu.spider import LaunchTask
from zhihu.auxiliary import work_dir, config
from zhihu.util import BeautifulTable
from zhihu.spider.modules import get_module_instance_by_task_feature


def get_parser():
    parser = argparse.ArgumentParser(description='Zhihu Favorite', add_help=False)

    parser.add_argument('-u', action='store', help='收藏对象链接')
    parser.add_argument('-r', action='store', help='从文本读取收藏对象链接（每行一个）')
    parser.add_argument('-w', action='store', default=None, help='文件保存位置')
    parser.add_argument('-f', action='store', default='html', help='文件输出类型(html/md/all)')
    parser.add_argument('-dg', action='store_true', help='附带下载图片')
    parser.add_argument('-log', '--login', action='store_true', help='临时登录知乎')
    parser.add_argument('-log2', '--login-long', action='store_true', help='长期登录知乎')
    parser.add_argument('--remove-media', action='store_true', help='移除多媒体，仅保留文案文本')
    parser.add_argument('--image-only', action='store_true', help='只下载图片不收藏文案')

    parser.add_argument('-cd', action='store_true', help='缓存原始数据')
    parser.add_argument('-cso', action='store_true', help='输出css文件')
    parser.add_argument('-v', '--version', action='store_true', help='版本信息')
    parser.add_argument('-h', '--help', action='store_true', help='帮助')

    return parser


def get_urls(args):
    urls = list()

    if args.u is not None:
        urls.extend(args.u.split('#'))

    def read_file(file):
        if file is None:
            return None

        try:
            with open(file, 'rb') as foo:
                string = foo.read()
        except OSError:
            print('文件不存在！')
            sys.exit(0)

        for decode in ('utf8', 'gbk'):
            try:
                return string.decode(decode)
            except UnicodeError:
                pass
        print('无法读取文件，应使用UTF-8或GBK编码的文件！')
        sys.exit(0)

    if stg := read_file(args.r):
        urls.extend(re.split(r'[\s]+', stg))

    urls = set(urls)
    try:
        urls.remove('')
    except KeyError:
        pass
    return urls


def setting(args):
    if args.w:
        work_dir.set_path(args.w)

    file_type = {
        'html': (True, False), 'md': (False, True),
        'all': (True, True), '-': (False, False)
    }

    output_file_type = file_type.get('-' if args.image_only else args.f)
    config.set('output_html', output_file_type[0])
    config.set('output_md', output_file_type[1])

    config.set('remove_media', args.remove_media)
    config.set('cached', args.cd)
    config.set('css_output', args.cso)
    config.set('download_image', args.dg or args.image_only)


def main():
    args_parser = get_parser()

    args = args_parser.parse_args()

    if args.version:
        print('\n%s %s 本地化收藏知乎优质内容\n' % (zhihu.__name__, zhihu.__version__), end='\n')
        sys.exit(0)

    if args.help or (args.u is None and args.r is None) and not (args.login or args.login_long):
        args_parser.print_help()
        print('提示：长期登录知乎后，如需退出知乎，可临时登录知乎一次。(zhihu -log)')
        sys.exit(0)

    setting(args)

    beginning = LaunchTask(sign_in=args.login or args.login_long, sign_for_long=args.login_long)

    urls = get_urls(args)
    for url in urls:
        management = get_module_instance_by_task_feature(task=url)
        if management is None:
            print(
                '不支持的链接或链接错误，请使用完整的链接。',
                '目前支持——答案、文章、问题、视频、专栏、收藏夹”。',
                f'ERROR: {url}',
                sep='\n',
                end='\n\n'
            )
            sys.exit(0)

        table = BeautifulTable(management.name)
        try:
            beginning.start(management=management, table=table)
        except KeyboardInterrupt:
            table.show_msg('正在退出...')
            table.close(show_path=False)
        except Exception:
            table.show_msg('程序发生错误！')
            table.close(show_path=False)
        else:
            table.close()

