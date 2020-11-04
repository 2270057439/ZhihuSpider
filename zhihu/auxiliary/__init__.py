import os
import traceback

from zhihu.util import timestamp_to_date, escape_file_path

__all__ = ['config', 'work_dir', 'data', 'log']

op = os.path
opj = op.join

DEFAULT_DIR = op.normpath(opj(op.expanduser('~'), r'Documents\Zhihu-favorite'))
os.makedirs(DEFAULT_DIR, exist_ok=True)
native = op.dirname(__file__)


def opj_dir(*args, **kwargs):
    p = opj(*args, **kwargs)
    os.makedirs(p, exist_ok=True)
    return op.normpath(p)


class WorkDir:
    """工作目录管理"""

    def __init__(self):
        self.cur_dir = DEFAULT_DIR
        self._path = DEFAULT_DIR
        self.__root_path = DEFAULT_DIR
        self._user_path = None

    def set_path(self, path):
        """设置并更改工作目录"""
        self._user_path = path
        self.__root_path = path
        self.change()

    def change(self, *dirs):
        """变更当前工作目录"""
        root = self._user_path or self.__root_path
        self._path = opj_dir(root, *dirs)
        self.cur_dir = self._path
        return self._path

    def getcwd(self):
        return self.cur_dir

    def append(self, *dirs):
        """添加文件夹（子目录）到当前工作目录"""
        self._path = opj_dir(self._path, *dirs)
        return self._path

    def get_file_name(self, file):
        """给file添加并返回完整的路径"""
        return opj(self._path, file)

    def generate_file_name(self, members, extension, *, cover=False):
        """返回由多个部分构成的文件名和路径
        :param extension:  文件扩展名
        :param members:    文件名的构成部分，一个以上，列表类型
        :param cover: 是否覆盖已存在的文件名
        :return:
        """
        main_name = escape_file_path('_'.join(members))
        name = main_name + '.' + extension
        if cover:
            index = 1
            while op.exists(self.get_file_name(name)):
                name = main_name + '_' + str(index) + '.' + extension
                index += 1
        return self.get_file_name(name)

    def cached_file(self, file):
        """返回缓存文件"""
        return opj(opj_dir(self.__root_path, 'Application', 'cached'), file)

    def cookies_file(self):
        return opj(opj_dir(self.__root_path, 'Application'), 'cookies.txt')

    def log_file(self):
        return opj(
            opj_dir(self.__root_path, 'Application', 'log'),
            timestamp_to_date(ft='%Y%m%d_%H%M%S.txt')
        )

    def image_file(self, file):
        return opj(opj_dir(self._path, 'image'), file)


work_dir: WorkDir = WorkDir()


class Data:

    def __init__(self):
        self.files_map = dict()
        for file in os.listdir(opj(native, 'attachment')):
            self.files_map[file.split('.')[0]] = opj(native, 'attachment', file)

        def init(file_name):
            dt = dict()
            with open(file_name, 'r', encoding='utf8') as foo:
                for line in foo.readlines():
                    line = line.strip()

                    if (not line) or line.startswith('#'):
                        continue

                    key, value = line.split('@')
                    dt[key] = value

            return dt

        self.__api = init(self.files_map.get('api'))
        self.__set = init(self.files_map.get('default'))

    def template(self, name):
        return self._read_file(name)

    def _read_file(self, name):
        if name in self.files_map:
            file_path = self.files_map.get(name)
            with open(file_path, 'r', encoding='utf8') as foo:
                return foo.read()
        else:
            return None

    def api(self, name):
        return self.__api.get(name, None)

    def default(self, name):
        return self.__set.get(name, None)


data: Data = Data()


class Config:
    """程序配置信息"""

    def __init__(self):
        self.config = dict()

    def set(self, keys, value):
        keys = keys.split('/')

        area = self.config
        last_area = self.config

        key = None

        try:
            for key in keys[:-1]:
                area = area.get(key, None)
                assert area is None or isinstance(area, dict)
                if not area:
                    area = dict()
                    last_area[key] = area
                last_area = area
            area[keys[-1]] = value
        except AssertionError:
            raise KeyError(
                "key: %s, %s is a %s object, expect dict." % (
                    '/'.join(keys), key, type(key).__name__))

    def get(self, keys: str, default=None):
        keys = keys.split('/')
        key = None

        try:
            area = self.config
            for key in keys:
                area = area[key]
            return area
        except KeyError:
            if default is not None:
                self.set('/'.join(keys), default)
                return default
            else:
                raise KeyError(
                    'key: %s. There is no setting option named %s.' % ('/'.join(keys), key)
                )


config: Config = Config()


class Logging:
    def __init__(self, file):
        self.file = open(file, 'w', encoding='utf8')
        self.has_logged = False
        self.file_name = file

    def __del__(self):
        self.file.close()
        # 如果没有做任何有实际意义的记录，就删除记录文件
        if not self.has_logged:
            os.remove(self.file_name)

    def logging(self, error):
        self.file.write(timestamp_to_date(ft='%Y-%m-%d, %H:%M:%S\n'))
        logging = getattr(error, 'logging', None)
        if logging:
            error.logging(self.file)
        else:
            self.file.write('=' * 30 + '\n')
            traceback.print_exception(None, error, error.__traceback__, file=self.file)
            self.file.write('=' * 30 + '\n\n')
        self.has_logged = True

    def close(self):
        del self


log: Logging = Logging(work_dir.log_file())
