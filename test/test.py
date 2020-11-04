import sys
from zhihu.main import main

url = r'https://www.zhihu.com/question/296752647'

sys.argv = ['zhihu', '-u', url, '-w', r"E:\test", '--image-only']
main()

