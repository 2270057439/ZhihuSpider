import re

from zhihu.auxiliary import config as global_config
from zhihu.auxiliary import work_dir
from zhihu import util
from zhihu.spider.modules.basic import SingleManagement, MultipleManagement
from zhihu.spider.core import ZhihuRequestsApi


class AnswerManagement(SingleManagement):
    NAME = 'Answer'

    def __init__(self, identity):
        super(AnswerManagement, self).__init__(identity)

        self.data = super(AnswerManagement, self).fetch_json_data(
            self.name,
            self.identity,
            global_config.get('cached', False)
        )

        self.title = util.getvalue(self.data, 'question/title')
        self.vote_up = self.data.get('voteup_count')


class ArticleManagement(SingleManagement):
    NAME = 'Article'

    def __init__(self, identity):
        super(ArticleManagement, self).__init__(identity)

        self.data = super(ArticleManagement, self).fetch_json_data(
            self.name,
            self.identity,
            global_config.get('cached', False)
        )

        self.title = self.data.get('title')
        self.vote_up = self.data.get('voteup_count')


class VideoManagement(SingleManagement):
    NAME = 'Video'

    def __init__(self, identity):
        super(VideoManagement, self).__init__(identity)
        self.identity = identity
        resp = self.session.get(
            ZhihuRequestsApi.get_with_identity('VideoIndex', identity))

        self.title = re.search(r'<h1 class="ZVideo-title">(.+)</h1>', resp.text).group(1)
        video_id = re.search(r'https://www.zhihu.com/video/(\d+)', resp.text).group(1)
        vote_up = re.search(r'赞同\s*(\d+)?', resp.text).group(1) or '0'
        self.vote_up = int(vote_up)

        self.data = self.fetch_json_data(
            target=self.name,
            identity=video_id,
            cached=global_config.get('cached', default=False),
        )

    def download_video(self, meta, process_bar):
        self._download_helper(
            meta['video_url'],
            meta['file_name'],
            process_bar=process_bar
        )
        if meta['cover']:
            self.download_images(meta['cover'], lambda x: x)

    def parse_data(self, data):
        meta = dict()
        meta['cover'] = data.get('cover_url', None)

        for video_resolution in ('playlist/FHD', 'playlist/HD', 'playlist/LD', 'playlist/SD'):
            try:
                video_msg = util.getvalue(data, video_resolution)

                meta['format'] = video_msg.get('format')
                meta['video_url'] = video_msg.get('play_url')
                meta['file_name'] = work_dir.generate_file_name((self.title, self.identity), meta['format'])

                return meta
            except KeyError:
                pass


class QuestionManagement(MultipleManagement):
    NAME = 'Question'

    def __init__(self, identity):

        def init_totals_title(s):
            json_data_of_response = s.fetch_json_data(target='QuestionMeta', identity=identity)
            s.title = json_data_of_response.get('title')
            totals = json_data_of_response.get('answer_count')

            if totals <= 20:
                self.totals = totals
            elif totals <= 1000:
                s.totals = 20
            else:
                s.totals = int(totals * 0.02)

        super(QuestionManagement, self).__init__(identity, init_totals_title)


class ColumnManagement(MultipleManagement):
    NAME = 'Column'

    def __init__(self, identity):
        def init_totals_title(s):
            json_data_of_response = s.fetch_json_data('ColumnMeta', identity)
            s.title = json_data_of_response.get('title')
            s.totals = json_data_of_response.get('articles_count')

        super(ColumnManagement, self).__init__(identity, init_totals_title)


class CollectionManagement(MultipleManagement):
    NAME = 'Collection'

    def __init__(self, identity):
        def init_totals_title(s):
            json_data_of_response = s.fetch_json_data('CollectionMeta', identity)['collection']
            s.title = json_data_of_response.get('title')
            s.totals = json_data_of_response.get('item_count')

        super(CollectionManagement, self).__init__(identity, init_totals_title)

    def parse_data(self, data):
        data = data.get('content')
        assert isinstance(data, dict)
        return super(CollectionManagement, self).parse_data(data)
