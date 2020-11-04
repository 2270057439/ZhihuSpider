import os
import re

import requests

import zhihu.spider.core as core
from zhihu import exception
from zhihu import util
from zhihu.auxiliary import config as global_config
from zhihu.auxiliary import work_dir, log
from zhihu.document import Meta


def parse_article(data):
    meta = Meta()

    meta.identity = data.get('id')
    meta.title = data.get('title')
    meta.content = data.get('content')
    meta.voteup = data.get('voteup_count')
    meta.background = data.get('image_url')
    meta.author = util.getvalue(data, 'author/name')
    meta.created_date = util.timestamp_to_date(data.get('created'))

    meta.author_homepage = core.ZhihuRequestsApi.get_with_identity(
        'AuthorHomePageUrl', util.getvalue(data, 'author/url_token'))

    meta.source_url = core.ZhihuRequestsApi.get_with_identity('ArticleUrl', data.get('id'))
    meta.author_avatar_url = util.getvalue(data, 'author/avatar_url_template').format(size='l')

    return meta


def parse_answer(data):
    meta = Meta()

    meta.identity = data.get('id')
    meta.content = data.get('content')
    meta.voteup = data.get('voteup_count')
    meta.author = util.getvalue(data, 'author/name')
    meta.title = util.getvalue(data, 'question/title')
    meta.created_date = util.timestamp_to_date(data.get('created_time'))

    meta.author_homepage = core.ZhihuRequestsApi.get_with_identity(
        'AuthorHomePageUrl', util.getvalue(data, 'author/url_token'))

    meta.source_url = core.ZhihuRequestsApi.get_with_identity('AnswerUrl', data.get('id'))
    meta.author_avatar_url = util.getvalue(data, 'author/avatar_url_template').format(size='l')

    return meta


class BasicManagement:
    NAME = 'Basic'

    def __init__(self, identity):
        self.name = self.NAME
        self.identity = identity
        self.current_yield_data = None
        self.session = core.init_session()
        self.title = None
        self.totals = 1
        self.image_count = 0
        self.item_count = 0

    def __del__(self):
        self.session.close()

    def parse_data(self, data):
        data_type = data.get('type')

        if data_type == 'answer':
            self.item_count += 1
            return parse_answer(data)

        if data_type == 'article':
            self.item_count += 1
            return parse_article(data)

    def fetch_json_data(self, target, identity, cached=False, **kwargs):
        url = core.ZhihuRequestsApi.get_with_identity(target, identity, **kwargs)
        resp = self.session.get(url, timeout=30)
        try:
            resp.raise_for_status()
        except requests.RequestException:
            log.logging(exception.ZhihuNetworkError(url=url, status_code=resp.status_code))
            return None

        if cached:
            ofs = kwargs.get('offset', None) or util.timestamp()
            cached_file = work_dir.cached_file(f'{self.name}-{identity}-{ofs}.json')

            with open(cached_file, 'w', encoding='utf8') as foo:
                foo.write(resp.text)

        return resp.json()

    def download_images(self, content, process_bar):

        images_collection = self.search_images(content)
        for image_meta in images_collection:
            # image_meta：(image_link, image_file_name, image_name, resolution, format)
            self._download_helper(
                image_meta[0],
                work_dir.image_file(f'{self.name}-{self.identity}-{image_meta[1]}')
            )
            self.image_count += 1
            process_bar(len(images_collection))

    def data_packages(self, offset=0):
        while offset < self.totals:
            json_data_of_response = self.fetch_json_data(
                target=self.name,
                identity=self.identity,
                cached=global_config.get('cached', default=False),
                offset=offset
            )

            if json_data_of_response:
                try:
                    assert json_data_of_response.get('paging', None) is None
                except AssertionError:
                    database = json_data_of_response
                else:
                    database = json_data_of_response.get('data', [])

                while database and offset < self.totals:
                    offset += 1
                    yield database.pop()
            else:
                return

    @classmethod
    def _download_helper(cls, url, file_name, process_bar=None):
        stream = bool(process_bar)

        def download():
            with core.init_session().get(url, stream=stream, timeout=10) as resp:
                resp.close()
                if resp.status_code != 200:
                    return resp.status_code

                if stream:
                    totals = int(resp.headers['content-length'])  # Byte
                    with open(file_name, "wb") as foo:
                        for chunk in resp.iter_content(chunk_size=1024):
                            foo.write(chunk)
                            process_bar(totals, size=len(chunk))
                else:
                    with open(file_name, "wb") as foo:
                        foo.write(resp.content)

                return resp.status_code

        download_status_code = 0
        try:
            download_status_code = download()
        except requests.exceptions.ReadTimeout:
            for i in range(3):
                try:
                    download_status_code = download()
                    if download_status_code == 200:
                        break
                except requests.exceptions.ReadTimeout:
                    pass
        finally:
            if download_status_code != 200 and os.path.exists(file_name):
                os.remove(file_name)
            return download_status_code == 200

    @classmethod
    def search_images(cls, content):
        """
            # 正则表达式搜索html文本中的图片链接
            # 结果构成：(image_link, image_file_name, image_name, resolution, format)
            # for example:
            # ('https://pic3.zhimg.com/v2-6ee2f3d3ba6fac2deabc5ee6c2ed2b42_b.jpg',
            # '6ee2f3d3ba6fac2deabc5ee6c2ed2b42_b.jpg', '6ee2f3d3ba6fac2deabc5ee6c2ed2b42', 'b', 'jpg')
            :param content: html text
            :return: list, which compose of (image_link, image_file_name, image_name, resolution, format)
            """

        if content is None:
            return list()

        universal = (
            r'(https://pic\d.zhimg.com/(?:\d+/)?v\d-(([a-z0-9]+)(?:_([a-z0-9]+))?\.([a-z]+))(?:[?&=a-zA-z0-9]+)?)'
        )
        original = fr'data-original="{universal}"'

        search_regular_expression = re.compile(original)
        image_search_result_list = search_regular_expression.findall(content)

        # 去重，挑选特定格式、分辨率高的图片
        # 优先选gif图片，再依据分辨率挑选图片
        images_dict = dict()
        # 权重定义，分辨率、格式
        resolution3 = {'r': 3, 'b': 2, 'l': 1}
        format4 = {'gif': 5, 'png': 3, 'jpg': 2, 'jpeg': 2, 'webp': 1}
        while bool(image_search_result_list):
            image_msg = image_search_result_list.pop()
            image_name = image_msg[2]
            if images_dict.get(image_name, None) is not None:
                r_weight = resolution3.get(image_msg[3], 1) * format4.get(image_msg[4], 1)
                i_weight = resolution3.get(images_dict[image_name][3], 1) * format4.get(images_dict[image_name][4], 1)
                if r_weight > i_weight:
                    images_dict[image_name] = image_msg
            else:
                images_dict[image_name] = image_msg

        return list(images_dict.values())


class SingleManagement(BasicManagement):
    def __init__(self, identity):
        super(SingleManagement, self).__init__(identity)
        self.data = None

        work_dir.change(self.name)
        self.work_dir = work_dir.getcwd()


class MultipleManagement(BasicManagement):
    def __init__(self, identity, init_totals_title):
        super(MultipleManagement, self).__init__(identity)

        init_totals_title(self)
        work_dir.change(self.name, util.escape_file_path(self.title))
        self.work_dir = work_dir.getcwd()

    def data_packages(self, offset=0):
        while offset < self.totals:
            json_data_of_response = self.fetch_json_data(
                target=self.name,
                identity=self.identity,
                cached=global_config.get('cached', default=False),
                offset=offset
            )

            if json_data_of_response:
                try:
                    assert json_data_of_response.get('data', None) is None
                except AssertionError:
                    database = json_data_of_response.get('data', [])
                else:
                    database = json_data_of_response

                while database and offset < self.totals:
                    offset += 1
                    yield database.pop()
            else:
                return

    def __iter__(self):
        return self.data_packages()
