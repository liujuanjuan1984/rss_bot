# RUM 种子网络订阅器

这是一个基于 mixin messenger 的 bot，让 mixin 的用户更方便地参与到 Rum 的生态之中。

其功能是：

1、用户在 mixin mesenger 上与 bot 对话交互，发出订阅指令

2、bot 从 rum 网络获取待转发的数据并转换为动态，根据用户的订阅要求，转发给用户

3、bot 可以根据一定条件向用户空投 token

4、bot 即将支持代发，帮用户把内容发布到 rum group 上

实例： mixin bot 7000104017

## 如何部署？

1、mixin bot： 在 mixin 开发者后台申请创建，获得 keystore 

2、rum fullnode：加入所有可订阅的 rum groups ，为动态转发提供数据源，为内容代发提供上链入口

3、拷贝源码，初始化环境

```bash
git clone https://github.com/liujuanjuan1984/rss_bot.git
cd rss_bot
```

初始化环境：

可能需要安装 vc C++ 相关依赖组件

```bash
pipenv install
```

如果不需要虚拟环境，也可以直接安装：

```bash
pip install -r requirements.txt

```

4、更新配置文件

- blaze/config.py
- rss/config.py

5、启动如下服务：

- blaze 服务：监听 user 发给 mixin bot 的消息，并写入消息 db

```bash
pipenv run python do_blaze.py
```

- reply 服务：订阅交互，回复特定的用户消息，并更新订阅 db

```bash
pipenv run python do_reply.py
```

- rss 服务：从 rum 获取最新内容，并根据用户订阅推送给用户
- rum 服务：把以“代发：”开头的消息文本，采用托管的密钥发布到指定的 rum group 上

```bash
pipenv run python do_rum.py
```

- airdrop 服务：可向 mixin bot 的用户，或指定 rum group 中符合特定条件的用户空投。


```bash
pipenv run python do_airdrop.py
```

## 依赖：

- [mixinsdk](https://pypi.org/project/mixinsdk/0.1.4/)
- [rumpy](https://github.com/liujuanjuan1984/rumpy)

## 代码格式化

Install:

```bash
pip install black
pip install isort
```

Format:

```bash
isort .
black -l 120 -t py37 -t py38 -t py39 -t py310 .

```
