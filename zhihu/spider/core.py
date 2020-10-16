from http import cookiejar
import requests
from zhihu.auxiliary import data, work_dir


def init_session(load_cookies=False):
    session = requests.Session()
    session.headers.update({'User-Agent': ZhihuRequestsApi.UA})
    if load_cookies:
        try:
            cookies = cookiejar.LWPCookieJar(filename=work_dir.cookies_file())
            cookies.load()
            session.cookies = cookies
        except FileNotFoundError:
            pass

    return session


class ZhihuRequestsApi:
    """获得有关数据的链接类"""

    UA = data.default('user-agent')
    host = data.api('Host')
    index = data.api('Index')
    meMeta = data.api('MeMeat')

    @classmethod
    def get_with_identity(cls, target, identity, /, **kwargs):
        """
        :param identity: id of target
        :param target: name of api
        :param kwargs: offset, limit, sort_by
        :return: str, url
        """
        params = {
            'identity': identity,
            'offset': 0,
            'limit': 20,
            'sort_by': data.api('SORT_BY_VOT')
        }

        params.update(kwargs)

        return data.api(target).format(**params)

