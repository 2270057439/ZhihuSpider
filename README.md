# zhihu-favorite

程序提供一种简单快捷的方式**本地化收藏**知乎上的内容，如：**答案**、**文章**等，并尽可能保持内容格式与知乎上的一致；**支持下载图片、视频**。

用户提供知乎上相应项目的url爬取数据数据，数据经解析后最终输出为**markdown**或**html**文件存储到本地。

# 支持项目

- 专栏
- 答案
- 文章 
- 视频
- 图片
- 收藏夹
- 问题答案(同一问题下的高赞答案)

# 更新

- 修复专栏、收藏夹爬取失败；
- 新增支持**下载知乎视频**；
- 新增支持**仅下载图片**；**去除多媒体，仅保留文案**；
- 新增支持同时输出HTML和markdown;
- 优化控制台输出，新增表格形式输出、进度条动态更新；
- 若干优化。

## 使用

在命令行输入`zhihu -h`获得帮助信息：

```powershell
>>>zhihu -h
usage: zhihu [-u U] [-r R] [-w W] [-f F] [-dg] [-log] [-log2] [--remove-media] [--image-only] [-cd] [-cso] [-v] [-h]

Zhihu Favorite

optional arguments:
  -u U                 收藏对象链接
  -r R                 从文本读取收藏对象链接（每行一个）
  -w W                 文件保存位置
  -f F                 文件输出类型(html/md/all)
  -dg                  附带下载图片
  -log, --login        临时登录知乎
  -log2, --login-long  长期登录知乎
  --remove-media       移除多媒体，仅保留文案文本
  --image-only         只下载图片不收藏文案
  -cd                  缓存原始数据
  -cso                 输出css文件
  -v, --version        版本信息
  -h, --help           帮助
提示：长期登录知乎后，如需退出知乎，可临时登录知乎一次。(zhihu -log)
```
