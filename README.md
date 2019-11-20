# PushBot
 基于pyTelegramBotAPI的消息推送，允许一对一、一对多
 
## 配置

1. 向 `https://t.me/BotFather` 申请一个 bot，记录 token

2. 配置`config.py`文件

    ```plain
    # 必须修改
    IN_DOCKER = <True/False>        # 是否使用 docker 部署，docker 受单线程影响
    API_TOKEN = "<api_token>"       # BotFather 处申请的 token
    WEBHOOK_HOST = "<host or ip>"   # 部署 host 或 ip 均可
    WEBHOOK_PORT = "8443"           # 默认 Web 监听端口，若修改请同时修改 docker-compose 中端口映射
    
    # 替换证书
    # openssl genrsa -out cacert.pem 2048
    # openssl req -new -x509 -days 365 -key privkey.pem -out cacert.pem
    # 生成证书时 Common Name (eg, fully qualified host name) []:需要输入和 WEBHOOK_HOST 相同值
    WEBHOOK_SSL_CERT = "./conf/cacert.pem"
    WEBHOOK_SSL_PRIV = "./conf/privkey.pem"
    
    # 不用修改
    DB_PATH = "{}/db.json".format(getcwd())
    WEBHOOK_LISTEN = "0.0.0.0"
    WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
    WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)
    ```

## 部署

1. docker

    ```shell
    docker-compose up -d
    ```

2. python

    ```bash
    python botmain.py
    ```
  
3. 其他...
   
## 使用

1. 输入`/start`或`/help`后等待结果返回
2. 创建、绑定凭证
3. 通过接口进行消息推送

## 效果

![](https://cdn.sari3l.com/telebot_push.png)

## 注意事项

1. 需部署在能访问`https://api.telegram.org/`的服务器上
2. 凭证创始人无法将绑定同凭证的他人移除，所以需妥善保管 ID 和 SECRET
3. 暂时只支持简单消息推送