from zhihu import util
from zhihu.auxiliary import config as global_config
from zhihu.auxiliary import work_dir
from .basic import BasicManagement


###
# 代码暂时不可用
###


class UserManagement(BasicManagement):

    def __init__(self, identity):
        super(UserManagement, self).__init__(identity)

        resp = self.fetch_json_data('UserMate', self.identity)
        self.user_name = resp.json().get('name')
        self.title = self.user_name

        work_dir.change('User', util.escape_file_path(self.user_name))

    def data_packages(self, offset=0):
        json_data_of_response = self.fetch_json_data(
            target=self.name,
            identity=self.identity,
            cached=global_config.get('cached', default=False),
            offset=offset
        )

        if json_data_of_response:
            self.totals = util.getvalue(json_data_of_response, 'paging/totals')

            database = json_data_of_response.get('data', [])
            while database and offset < self.totals:
                offset += 1
                self.current_yield_data = database.pop()
                yield self.current_yield_data

            yield from super(UserManagement, self).data_packages(offset=offset)

        else:
            return


class UserAnswerManagement(UserManagement):
    NAME = 'UserAnswer'

    def __init__(self, identity):
        super(UserAnswerManagement, self).__init__(identity)


class UserArticleManagement(UserManagement):
    NAME = 'UserArticle'

    def __init__(self, identity):
        super(UserArticleManagement, self).__init__(identity)
