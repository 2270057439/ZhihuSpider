# class BasicManagement:
#
#     def __init__(self, identity):
#         self.name = 'Basic'
#         self.identity = identity
#         self.current_yield_data = None
#         self.session = core.init_session()
#         self.totals = 1
#
#     def __del__(self):
#         self.session.close()
#
#     def make_document(self, meta):
#         pass
#
#     def parse_data(self):
#         pass
#
#     def fetch_json_data(self, target, identity, cached=False, **kwargs):
#         url = core.ZhihuRequestsApi.get_with_identity(target, identity, **kwargs)
#         resp = self.session.get(url, timeout=30)
#         try:
#             resp.raise_for_status()
#         except requests.RequestException:
#             log.logging(exception.ZhihuNetworkError(url=url, status_code=resp.status_code))
#             return None
#
#         if cached:
#             ofs = kwargs.get('offset', None) or util.timestamp()
#             cached_file = work_dir.cached_file(f'{self.name}-{identity}-{ofs}.json')
#
#             with open(cached_file, 'w', encoding='utf8') as foo:
#                 foo.write(resp.text)
#
#         return resp.json()
#
#     def download_images(self, content, process_bar):
#
#         images_collection = self.search_images(content)
#         for image_meta in images_collection:
#             # image_meta：(image_link, image_file_name, image_name, resolution, format)
#             self._download_helper(
#                 image_meta[0],
#                 work_dir.image_file(f'{self.name.title()}-{self.identity}-{image_meta[1]}')
#             )
#             process_bar(len(images_collection))
#
#     def data_packages(self, offset=0):
#         while offset < self.totals:
#             json_data_of_response = self.fetch_json_data(
#                 target=self.name,
#                 identity=self.identity,
#                 cached=global_config.get('cached', default=False),
#                 offset=offset
#             )
#
#             if json_data_of_response:
#                 try:
#                     assert json_data_of_response.get('paging', None) is None
#                 except AssertionError:
#                     database = json_data_of_response
#                 else:
#                     database = json_data_of_response.get('data', [])
#
#                 while database and offset < self.totals:
#                     offset += 1
#                     yield database.pop()
#             else:
#                 return
#
#     @classmethod
#     def _download_helper(cls, url, file_name, process_record=None):
#         stream = bool(process_record)
#
#         with core.init_session().get(url, stream=stream, timeout=10) as resp:
#             if resp.status_code != 200:
#                 return resp.status_code
#
#             if stream:
#                 totals = int(resp.headers['content-length'])  # Byte
#                 process_record.totals(totals)
#                 with open(file_name, "wb") as foo:
#                     for chunk in resp.iter_content(chunk_size=1024):
#                         foo.write(chunk)
#                         process_record.update()
#             else:
#                 with open(file_name, "wb") as foo:
#                     foo.write(resp.content)
#
#             return resp.status_code
#
#     @classmethod
#     def search_images(cls, content):
#         """
#             # 正则表达式搜索html文本中的图片链接
#             # 结果构成：(image_link, image_file_name, image_name, resolution, format)
#             # for example:
#             # ('https://pic3.zhimg.com/v2-6ee2f3d3ba6fac2deabc5ee6c2ed2b42_b.jpg',
#             # '6ee2f3d3ba6fac2deabc5ee6c2ed2b42_b.jpg', '6ee2f3d3ba6fac2deabc5ee6c2ed2b42', 'b', 'jpg')
#             :param content: html text
#             :return: list, which compose of (image_link, image_file_name, image_name, resolution, format)
#             """
#
#         search_regular_expression = re.compile(
#             r'(https://pic\d.zhimg.com/(?:\d+/)?v\d-((\w+)_([brl]).(jpg|gif|webp|png|jpeg))(?:[?&=a-zA-z0-9]+)?)'
#         )
#         image_search_result_list = search_regular_expression.findall(content)
#
#         # 去重，挑选特定格式、分辨率高的图片
#         # 优先选gif图片，再依据分辨率挑选图片
#         images_dict = dict()
#         # 权重定义，分辨率、格式
#         resolution3 = {'r': 3, 'b': 2, 'l': 1}
#         format4 = {'gif': 5, 'png': 3, 'jpg': 2, 'jpeg': 2, 'webp': 1}
#         while bool(image_search_result_list):
#             image_msg = image_search_result_list.pop()
#             image_name = image_msg[2]
#             if images_dict.get(image_name, None) is not None:
#                 r_weight = resolution3.get(image_msg[3]) * format4.get(image_msg[4])
#                 i_weight = resolution3.get(images_dict[image_name][3]) * format4.get(images_dict[image_name][4])
#                 if r_weight > i_weight:
#                     images_dict[image_name] = image_msg
#             else:
#                 images_dict[image_name] = image_msg
#
#         return list(images_dict.values())
#
#
# class UserManagement(BasicManagement):
#     def __init__(self, identity):
#         super(UserManagement, self).__init__(identity)
#         self.name = 'UserMate'
#
#         resp = self.fetch_json_data(self.name, self.identity)
#         self.user_name = resp.json().get('name')
#         self.title = self.user_name
#
#         work_dir.change('User', util.escape_file_path(self.user_name))
#
#     def data_packages(self, offset=0):
#         json_data_of_response = self.fetch_json_data(
#             target=self.name,
#             identity=self.identity,
#             cached=global_config.get('cached', default=False),
#             offset=offset
#         )
#
#         if json_data_of_response:
#             self.totals = util.getvalue(json_data_of_response, 'paging/totals')
#
#             database = json_data_of_response.get('data', [])
#             while database and offset < self.totals:
#                 offset += 1
#                 self.current_yield_data = database.pop()
#                 yield self.current_yield_data
#
#             yield from super(UserManagement, self).data_packages(offset=offset)
#
#         else:
#             return
#
#
# class UserAnswerManagement(UserManagement):
#     def __init__(self, identity):
#         super(UserAnswerManagement, self).__init__(identity)
#         self.name = 'UserAnswer'
#
#
# class UserArticleManagement(UserManagement):
#     def __init__(self, identity):
#         super(UserArticleManagement, self).__init__(identity)
#         self.name = 'UserArticle'

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

# class UserMetaManagement(MultipleManagement):
#     item_name = 'user'
#
#     def __init__(self, user_id):
#         super(UserMetaManagement, self).__init__(user_id)
#         resp = self.get_network_data_package('user_meta', self.item_id)
#         self.user_name = resp.json().get('name')
#         self.title = self.user_name
#
#         work_dir.change('User')
#         work_dir.append(util.escape_file_path(self.user_name))
#
#
# class UserAnswersManagement(UserMetaManagement):
#     item_name = 'user_answers'
#
#     def __init__(self, user_id):
#         super(UserAnswersManagement, self).__init__(user_id)
#         rjs = self.get_network_data_package(self.item_name, self.item_id, limit=0).json()
#         self.totals = util.getvalue(rjs, 'paging/totals')
#
#         work_dir.append('answers')
#
#
# class UserArticlesManagement(UserMetaManagement):
#     item_name = 'user_articles'
#
#     def __init__(self, user_id):
#         super(UserArticlesManagement, self).__init__(user_id)
#
#         rjs = self.get_network_data_package(self.item_name, self.item_id, limit=0).json()
#         self.totals = util.getvalue(rjs, 'paging/totals')
#
#         work_dir.append('articles')
