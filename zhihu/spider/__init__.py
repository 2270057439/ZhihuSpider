from zhihu.document import Document
from zhihu.auxiliary import config
from zhihu.spider.login import ZhihuAccount
from zhihu.spider.modules import get_module_instance_by_task_feature


class LaunchTask:
    """
    在这里编写爬虫流程，内容下载，文档生成，用户界面，错误捕捉等一系列操作
    """

    def __init__(self, sign_in, sign_for_long):
        self.sign_for_long = sign_for_long

        if sign_in or sign_for_long:
            ZhihuAccount().sign_in()

    def __del__(self):
        """如果有登录了的知乎账号并且不是长期登录的话就退出知乎账号"""
        if ZhihuAccount.SIGNED and not self.sign_for_long:
            ZhihuAccount.CURRENT_ACCOUNT.sign_out()

    @classmethod
    def start(cls, management, table):
        table.show_interface(management)

        if management.name == 'Video':
            # todo 设置差错处理
            meta = management.parse_data(management.data)
            management.download_video(meta, process_bar=table.download_process)
            table.close()
            return

        if management.name in ('Answer', 'Article'):
            # todo 设置差错处理
            meta = management.parse_data(management.data)
            if config.get('output_html'):
                Document.item2html(meta, config.get('css_output'), config.get('remove_media'))

            if config.get('output_md'):
                Document.item2md(meta, config.get('remove_media'))

            if config.get('download_image'):
                management.download_images(meta.content, table.image_process)

            table.close()
            return

        if management.name in ('Question', 'Column', 'Collection'):
            # todo 设置差错处理

            # 当前模式下无法预知图片总数量，所以只要下载图片就启用 DoubleProcessBar
            table.double_process_bar = config.get('download_image')

            for data in management:

                meta = management.parse_data(data)

                try:
                    assert meta is not None
                except AssertionError:
                    continue

                if config.get('output_html'):
                    Document.item2html(meta, config.get('css_output'), config.get('remove_media'))

                if config.get('output_md'):
                    Document.item2md(meta, config.get('remove_media'))

                if config.get('output_html') or config.get('output_md'):
                    table.text_process(management.totals)

                if config.get('download_image'):
                    management.download_images(meta.content, table.image_process)

            table.close()
            return
