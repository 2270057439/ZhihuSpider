import sys
import traceback


class ZhihuException(Exception):
    def logging(self, file):
        file.write('*' * 50 + '\n')

        file.write('%s:\n' % type(self).__name__)

        for msg in self.args:
            file.write(msg)

        file.write('\n' + '~' * 50 + '\n')

        file.write(self.tip.strip())

        file.write('\n' + '^' * 50 + '\n\n')


class ZhihuNetworkError(ZhihuException):
    def __init__(self, url, status_code):
        self.url = url
        self.status_code = status_code

        exc_type, exc_value, exc_traceback = sys.exc_info()
        cause = str(exc_value)

        super(ZhihuNetworkError, self).__init__(
            f'网络错误：{status_code}，url：{url}\ncause: {cause}')

        self.tip = traceback.format_exc()


class ZhihuHtmlParseError(ZhihuException):
    def __init__(self, msg, tag):
        super(ZhihuHtmlParseError, self).__init__(msg)
        self.tip = tag


class ItemError(ZhihuException):
    def __init__(self, item_url):
        exc_type, exc_value, exc_traceback = sys.exc_info()

        if not exc_value:
            exc_type = type(self).__name__
        else:
            exc_type = exc_type.__name__

        msg = str(exc_value)
        err_msg = f'OriginalError: {exc_type}, ItemUrl: {item_url}\n{msg}'

        super(ItemError, self).__init__(err_msg)

        self.tip = traceback.format_exc()

