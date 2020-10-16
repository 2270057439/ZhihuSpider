import re
import importlib

any = re.compile(r'.*')
art = re.compile(r'^https://zhuanlan.zhihu.com/p/(\d+)$')
zvi = re.compile(r'^https://www.zhihu.com/zvideo/(\d+)$')
que = re.compile(r'^https://www.zhihu.com/question/(\d+)$')
cot = re.compile(r'^https://www.zhihu.com/collection/(\d+)')
col = re.compile(r'^https://www.zhihu.com/column/([a-zA-Z0-9_]+)$')
qan = re.compile(r'^https://www.zhihu.com/question/\d+/answer/(\d+)$')


# pin = re.compile(r'^https://www.zhihu.com/people/([a-zA-Z0-9_]+)/pins$')
# pos = re.compile(r'^https://www.zhihu.com/people/([a-zA-Z0-9_]+)/posts$')
# pan = re.compile(r'^https://www.zhihu.com/people/([a-zA-Z0-9_]+)/answers$')

# https://zhuanlan.zhihu.com/    p/33130566
# https://zhuanlan.zhihu.com/daniujiangtang
# https://www.zhihu.com/  question     /424847061
# https://www.zhihu.com/  collection   /80199642
# https://www.zhihu.com/  people       /maxwell-chen-0109
# https://www.zhihu.com/  column       /c_1250926511692713985
# https://www.zhihu.com/  people       /maxwell-chen-0109/    pins
# https://www.zhihu.com/  people       /maxwell-chen-0109/    posts
# https://www.zhihu.com/  people       /alfredda-lao-hu/      columns
# https://www.zhihu.com/  people       /zhou-ding-33/         collections
# https://www.zhihu.com/  people       /maxwell-chen-0109/    answers
# https://www.zhihu.com/  question     /424847061/            answer         /1517992628


MODULES = [
    ('any', any),
    ('VideoManagement', zvi),
    ('AnswerManagement', qan),
    ('ColumnManagement', col),
    ('ArticleManagement', art),
    ('QuestionManagement', que),
    ('CollectionManagement', cot),

    # ('UserAnswersManagement', pan),
    # ('UserArticlesManagement', pos),
]


def get_module_instance_by_task_feature(task):
    modules_index = len(MODULES) - 1
    while not (match_res := MODULES[modules_index][1].match(task)):
        modules_index -= 1

    if modules_index == 0:
        return None
    else:
        modules = importlib.import_module('zhihu.spider.management')
        management = getattr(modules, MODULES[modules_index][0])
        return management(match_res.group(1))
