# config:utf-8
from os import getcwd

IN_DOCKER = True # False
API_TOKEN = "<token>"
WEBHOOK_HOST = "<host>"
WEBHOOK_PORT = "8443"

WEBHOOK_SSL_CERT = "./conf/cacert.pem"
WEBHOOK_SSL_PRIV = "./conf/privkey.pem"

WEBHOOK_LISTEN = "0.0.0.0"
DB_PATH = "{}/db.json".format(getcwd())
WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)
