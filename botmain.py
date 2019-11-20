# coding:utf-8
from telebot import TeleBot, types
from uuid import uuid1, uuid5
from tdb import Tdb
from time import sleep
from conf.config import *
import flask


tdb = Tdb(DB_PATH)
bot = TeleBot(API_TOKEN, threaded=not IN_DOCKER)
webapp = flask.Flask(__name__)


def sql_result_text(pretext, status):
    endtext = "成功" if status else "失败，请检查相关信息后重新尝试..."
    return pretext + endtext


# BOT
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    itembtn1 = types.InlineKeyboardButton("创建凭据", callback_data="create")
    itembtn2 = types.InlineKeyboardButton("删除凭据", callback_data="delete")
    itembtn3 = types.InlineKeyboardButton("绑定凭据", callback_data="binding")
    itembtn4 = types.InlineKeyboardButton("解除绑定", callback_data="unBind")
    itembtn5 = types.InlineKeyboardButton('查询绑定状态', callback_data="getStatus")
    markup.row(itembtn1, itembtn2)
    markup.row(itembtn3, itembtn4)
    markup.row(itembtn5)
    text = "1. 创建凭据：生成随机id和secret，创建者默认绑定\n" \
           "2. 删除凭据：只有创建者才可执行删除\n" \
           "3. 绑定凭证：绑定后即可获取消息推送\n" \
           "4. 解除绑定：解除相关绑定信息，接触后无法继续获取相关推送\n" \
           "5. 查询绑定状态：查询当前获取绑定数量及相关ID\n\n" \
           "推送接口：https://{host}:{port}/sendMessage/?id=:id&text=:text".format(
        host=WEBHOOK_HOST,
        port=WEBHOOK_PORT
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(lambda query: query.data == 'create')
def process_create(data):
    sid = "DZ" + str(uuid1())[:8]
    secret = str(uuid5(uuid1(), sid))
    status = tdb.insert_cert(dict(sid=sid,
                                  secret=secret,
                                  userid=data.from_user.id))
    if status is True:
        text = "创建凭证成功\n" \
               "ID: {}\n" \
               "SECRET: {}\n" \
               "!!!请妥善保管凭据，SECRET 丢失后无法找回!!!".format(sid, secret)
    else:
        text = "创建凭证失败\n" \
               "请重新尝试..."
    bot.send_message(data.message.chat.id, text)
    status = tdb.bind_cert(dict(
        sid=sid,
        secret=secret,
        userid=data.from_user.id))
    bot.send_message(data.message.chat.id, sql_result_text("绑定凭证 {}".format(sid), status))


@bot.callback_query_handler(lambda query: query.data == 'delete')
def process_delete(data):
    resultList = tdb.search_cert(dict(userid=data.from_user.id))
    if len(resultList) == 0:
        text = "本用户下未创建凭证，请尝试其他操作"
        bot.send_message(data.message.chat.id, text)
    else:
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        text = "你正在执行删除凭证操作，请选择一个已创建的ID"
        for i in resultList:
            markup.add(types.KeyboardButton(i['sid']))
        msg = bot.send_message(data.message.chat.id, text, reply_markup=markup)
        bot.register_next_step_handler(msg, delete_step_i, data.from_user.id, resultList)


def delete_step_i(message, owner, resultList):
    sid = message.text
    if sid in [x['sid'] for x in resultList]:
        text = "请继续输入SECRET，完成删除操作"
        msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(msg, delete_step_ii, dict(owner=owner, sid=sid))
    else:
        text = "输入无效，请重新操作..."
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, text, reply_markup=markup)


def delete_step_ii(message, mdata):
    secret = message.text
    status = tdb.delete_cert(dict(
        sid=mdata['sid'],
        secret=secret,
        userid=mdata['owner']))
    bot.send_message(message.chat.id, sql_result_text("删除凭证 {}".format(mdata['sid']), status))


@bot.callback_query_handler(lambda query: query.data == 'binding')
def process_binding(data):
    text = "请输入ID以及SECRET，格式为 ID:::SECRET"
    msg = bot.send_message(data.message.chat.id, text)
    bot.register_next_step_handler(msg, binging_step_i)


def binging_step_i(message):
    [sid, secret] = str(message.text).split(':::')
    status = tdb.bind_cert(dict(
        sid=sid,
        secret=secret,
        userid=message.from_user.id))
    bot.send_message(message.chat.id, sql_result_text("绑定凭证 {}".format(sid), status))


@bot.callback_query_handler(lambda query: query.data == 'unBind')
def process_unbind(data):
    resultList = tdb.search_ship(dict(userid=data.from_user.id))
    if len(resultList) == 0:
        text = "本用户下未绑定凭证，请尝试其他操作"
        bot.send_message(data.message.chat.id, text)
    else:
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        text = "你正在执行解除凭证操作，请选择一个已绑定的ID"
        for i in resultList:
            markup.add(types.KeyboardButton(i['sid']))
        msg = bot.send_message(data.message.chat.id, text, reply_markup=markup)
        bot.register_next_step_handler(msg, unbind_step_i, resultList)


def unbind_step_i(message, resultList):
    sid = message.text
    if sid in [x['sid'] for x in resultList]:
        status = tdb.unbind_cert(dict(sid=sid, userid=message.from_user.id))
        bot.send_message(message.chat.id, sql_result_text("解除绑定 {}".format(sid), status))
    else:
        text = "输入无效，请重新操作...\n/start"
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(lambda query: query.data == 'getStatus')
def process_getstatus(data):
    resultList = tdb.search_ship(dict(userid=data.from_user.id))
    text = "本用户下绑定有凭证 {} 个\n".format(len(resultList))
    for i, sid in enumerate([x['sid'] for x in resultList]):
        text += "{}: {}\n".format(i, sid)
    bot.send_message(data.message.chat.id, text)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)


# Web
@webapp.route('/', methods=['GET'])
def index():
    return {"status": "OK"}


@webapp.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


@webapp.route('/sendMessage/', methods=['GET'])
def echo_message():
    sid = flask.request.args.get('id')
    text = flask.request.args.get('text')
    return send_message(dict(
        sid=sid,
        text=text
    ))


def send_message(data):
    userList = tdb.find_ship_user(dict(
        sid=data['sid']
    ))
    result_text = {}
    for i, cid in enumerate([x['uid'] for x in userList]):
        status = bot.send_message(
            chat_id=cid,
            text=data['text']
        )
        result_text[i] = status.json
    return result_text


bot.remove_webhook()
sleep(1)
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

webapp.run(host=WEBHOOK_LISTEN,
           port=WEBHOOK_PORT,
           ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
           debug=True)
