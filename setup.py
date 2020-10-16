import os
import re
from setuptools import setup
import zhihu


def find_requirements():
    with open('requirements.txt', 'r', encoding='utf8') as foo:
        return re.split(r'\s+', foo.read())


setup(
    name=zhihu.__name__,
    version=zhihu.__version__,
    keywords=['zhihu', 'spider', 'favorite', 'image', 'collection', 'question', 'answer', 'article'],
    packages=['zhihu', 'zhihu/spider', 'zhihu/spider/modules', 'zhihu/document', 'zhihu/auxiliary'],
    url='https://github.com/Milloyy/ZhihuFavorite',
    license='MIT',
    author='枫知淇',
    author_email='',
    description='本地化收藏知乎优质内容，包括特定答案，问题的优质答案，文章，专栏文章，收藏夹的答案和文章',
    platforms='win10',
    install_requires=find_requirements(),
    scripts=[],
    entry_points={
        'console_scripts': [
            'zhihu = zhihu.main:main'
        ]
    },
    data_files=[
        ('zhihu/auxiliary/attachment', [
            os.path.join('zhihu/auxiliary/attachment', file) for file in os.listdir(
                'zhihu/auxiliary/attachment')])
    ],
    zip_safe=False
)
