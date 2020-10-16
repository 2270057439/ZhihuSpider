import os
import platform
import time
from http import cookiejar
from requests import RequestException
from zhihu.auxiliary import work_dir
from zhihu.spider import core
from zhihu.util import yes_or_no

__all__ = ['ZhihuAccount']


class ZhihuAccount:
    BASE_HEAD = {'Host': core.ZhihuRequestsApi.host}

    SIGNED = False  # 已登录？
    CURRENT_ACCOUNT = None  # 当前登录的账号实例

    def __init__(self):
        self.session = core.init_session(load_cookies=True)

        resp = self.session.get('https://www.zhihu.com/signup?next=%2F',
                                headers=ZhihuAccount.BASE_HEAD, allow_redirects=False)

        self.__class__.SIGNED = True if resp.status_code == 302 else False

        self.__class__.CURRENT_ACCOUNT = self

        self.user_name = None

    @property
    def cookies(self):
        return self.session.cookies

    def sign_in(self):
        if self.__class__.SIGNED:
            if not self.user_name:
                self.user_info()
            print('嘿，%s，你已经登录过了！' % self.user_name)
        elif self.__login():
            self.user_info()
            print('哈喽，%s，我们又见面啦！' % self.user_name)
            self.__class__.SIGNED = True
            self.save_requests_cookiejar()

    def save_requests_cookiejar(self):
        cookies = cookiejar.LWPCookieJar()
        for cookie_in_jar in self.session.cookies:
            cookies.set_cookie(cookie_in_jar)
        cookies.save(work_dir.cookies_file())

    def sign_out(self):
        if self.__class__.SIGNED:
            print('再见，%s！\n' % self.user_name)
            self.session.get('https://www.zhihu.com/logout',
                             headers=ZhihuAccount.BASE_HEAD, allow_redirects=False)
            self.session.cookies.save()
            self.__class__.SIGNED = False

    def __login(self):
        print('开始登录...')

        try:
            captcha_head = {"Referer": "https://www.zhihu.com/"}

            captcha_head.update(ZhihuAccount.BASE_HEAD)
            self.session.get("https://www.zhihu.com/api/v3/oauth/captcha?lang=en",
                             headers=captcha_head)
            resp = self.session.post("https://www.zhihu.com/udid", headers=ZhihuAccount.BASE_HEAD)
            token_head = {
                'Origin': 'https://www.zhihu.com',
                'Referer': 'https://www.zhihu.com/signup?next=%2F',
                'x-udid': resp.content.decode('utf8')
            }

            token_head.update(ZhihuAccount.BASE_HEAD)
            resp = self.session.post("https://www.zhihu.com/api/v3/account/api/login/qrcode",
                                     headers=token_head)
            token = resp.json().get('token')
            qr = self.session.get(
                f'https://www.zhihu.com/api/v3/account/api/login/qrcode/{token}/image',
                headers=token_head)

            self.__show_qr_code(qr.content)

            print('操作系统已使用关联程序显示二维码，请使用知乎APP扫描。\n')
            print('准备扫描...', end='\r')

            time.sleep(10)
            scan_time = 60
            remaining_time = scan_time
            presetting_time = time.time()

            while True:
                rjs = self.session.get(
                    f'https://www.zhihu.com/api/v3/account/api/login/qrcode/{token}/scan_info',
                    headers=captcha_head).json()

                if rjs.get('user_id', None) or rjs.get('status', None) == 6 or rjs.get('error'):
                    break

                if time.time() - presetting_time >= scan_time:
                    if yes_or_no('发生了什么？是二维码飞走了？手速不够没扫完？'):
                        self.__show_qr_code(None)
                        remaining_time = scan_time
                        presetting_time = time.time()
                        continue
                    else:
                        print('已停止登录。')
                    return False

                end = '\n' if remaining_time <= 2 else '\r'
                print('请在{:>02d}s内完成扫描...'.format(remaining_time), end=end)
                remaining_time -= 2
                time.sleep(2)

            return True
        except KeyboardInterrupt as e:
            print('-------已退出！-------')
            return False
        except RequestException:
            print('无法登录，请稍后再试！')
            return False

    def user_info(self):
        me = core.ZhihuRequestsApi.meMeta
        resp = self.session.get(me, allow_redirects=False)
        if resp.status_code == 200:
            rjs = resp.json()
            self.user_name = rjs.get('name')
            return rjs
        else:
            return None

    @staticmethod
    def __show_qr_code(image):
        """
        调用系统软件显示图片
        """

        image_file = work_dir.cached_file('QR.jpg')

        if image is not None:
            with open(image_file, 'wb') as foo:
                foo.write(image)

        if os.path.exists(image_file):

            if platform.system() == 'Darwin':
                os.subprocess.call(['open', image_file])
            elif platform.system() == 'Linux':
                os.subprocess.call(['xdg-open', image_file])
            else:
                os.startfile(image_file)

        else:
            print('二维码云游四海去了，稍后再尝试登录吧！')

    def __del__(self):
        self.session.close()
        try:
            os.remove(work_dir.cached_file('QR.jpg'))
        except IOError:
            pass

