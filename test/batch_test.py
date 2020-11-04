from zhihu.main import main
import sys

test_items = {
    'user': [
        # 高冷冷
        'https://www.zhihu.com/people/gao-leng-leng-61/answers',
        'https://www.zhihu.com/people/gao-leng-leng-61/posts',
        # # 蘑菇汤
        # 'https://www.zhihu.com/people/mo-gu-tang-37-71/answers',
        # 'https://www.zhihu.com/people/mo-gu-tang-37-71/posts',
        # # 叶倩倩
        # 'https://www.zhihu.com/people/xie-qian-qian-20-2/answers',
        # 'https://www.zhihu.com/people/xie-qian-qian-20-2/posts'
    ],
    'question': [
        'https://www.zhihu.com/question/324068870',
        'https://www.zhihu.com/question/296752647',
        'https://www.zhihu.com/question/43607087',
        'https://www.zhihu.com/question/52178718'
    ],
    'answer': [
        'https://www.zhihu.com/question/385504810/answer/1132126959',  # 普通
        'https://www.zhihu.com/question/380314348/answer/1130582607',  # 禁止转载
        'https://www.zhihu.com/question/384956473/answer/1131239176',  # 普通
        'https://www.zhihu.com/question/385520014/answer/1132730616',  # 申请转载
        'https://www.zhihu.com/question/385520014/answer/1132856138',  # 禁止转载
    ],
    'collection': [
        'https://www.zhihu.com/collection/105052833',  # 128
        'https://www.zhihu.com/collection/26915405',  # 145
        'https://www.zhihu.com/collection/136306793',  # 135
        'https://www.zhihu.com/collection/64536240',  # 57
    ],
    'column': [
        'https://zhuanlan.zhihu.com/daniujiangtang',  # 23
        # 'https://zhuanlan.zhihu.com/c_89290344',  # 34
        # 'https://zhuanlan.zhihu.com/c_29950851',  # 17
        # 'https://zhuanlan.zhihu.com/lilyzhao',  # 60
        # 'https://www.zhihu.com/column/yiyuguancha' # 1110
    ],
    'article': [
        'https://zhuanlan.zhihu.com/p/113378691',
        'https://zhuanlan.zhihu.com/p/109564663',
        'https://zhuanlan.zhihu.com/p/106680041',
        'https://zhuanlan.zhihu.com/p/110167658'
    ],
    'video': [
        'https://www.zhihu.com/zvideo/1228331394134720512',
        'https://www.zhihu.com/zvideo/1226920279831769088',
        'https://www.zhihu.com/zvideo/1204881700238757888',
        'https://www.zhihu.com/zvideo/1225838899404423168'
    ]
}
for item_type, urls in test_items.items():
    if item_type == 'article':
        for url in urls:
            sys.argv = ['zhihu', '-u', url, '-dg', '-w', r"E:\test", '-cd']
            main()
