## 一个注重创作的轻博客系统

作为一名技术人员一定要有自己的**博客**，用来记录平时技术上遇到的问题，把**技术分享**出去就像滚雪球一样会越來越大，可以使用博客平台（简书、博客园、开源中国、CSDN等）来写博客，但我总感觉少了点什么，于是就在网上找了很多了博客系统，其实大同小异，于是就用业余时间用**python**开发了[h3blog](http://www.h3blog.com)，一个使用python开发的**轻量博客**系统，麻雀虽小但五脏也快长全了，功能一直都会不断更新...，你也可以先睹为快地址：[http://www.h3blog.com](http://www.h3blog.com)

## 用到的技术

- python
- flask
- flask-wtf
- flask-sqlalchemy
- markdown
- bootstrap4
- 支持sqlite、mysql等

数据库默认使用sqlite3，正式使用时请自行切换到mysql数据库

## 博客功能

- 撰写文章
- 文章列表
- 文章分类
- 标签管理
- 推荐文章
- 内置图床（使用七牛云做存储）
- 网站设置
- 百度推送

## 运行

```bash
$ git clone https://gitee.com/pojoin/h3blog.git
$ cd h3blog
$ python -m venv venv  #创建python虚拟环境
$ source venv/bin/activate
$ 
$ pip install -r requirements.txt # 安装项目依赖，可能不全，根据提示自行安装即可
$ flask initdb #创建数据库
$ export FLASK_ENV=development
$ flask run # 启动
```

**项目配置文件推荐是.env进行私密配置，这也可以减少配置文件的修改**

## 博客截图

![登陆](https://images.gitee.com/uploads/images/2020/0306/141924_e000ec0d_120583.png "Screenshot_2020-03-06 博客登陆.png")

![后台](https://images.gitee.com/uploads/images/2020/0306/141733_3d233e92_120583.png "Screenshot_2020-03-06 何三笔记.png")

![博客前端](https://images.gitee.com/uploads/images/2020/0306/141709_72e17390_120583.png "Screenshot_2020-03-06 何三笔记-一个通过python实现赚钱的技术博客.png")

我的博客 [何三笔记](http://www.h3blog.com)
