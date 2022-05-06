import os
import PIL
from flask import Flask, request
from data import db_session
from data.user import User, Chat, MSG
from hashlib import sha224
from email_validate import validate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import random
import threading
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my genius secret key'
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_PORT"] = 587
# app.config["MAIL_USERNAME"] = "mysen.help.me@gmail.com"
app.config["MAIL_USERNAME"] = "mysen.help@yandex.ru"
app.config["MAIL_PASSWORD"] = "mysen2021"
db_session.global_init("db/data.sqlite")
password_hash = "27b80f2b0304bef4da58f2bde7e93e5b948f96f1c4a3f60abab033e39b41428b"
time_start = datetime.datetime.now()


def send_mail(id):
    me = "mysen.help@yandex.ru"

    session = db_session.create_session()
    user = session.query(User).filter(User.id == id).first()
    you = user.mail

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Восстановление пароля"
    msg['From'] = me
    msg['To'] = you

    extra = "".join([random.choice("0123456789QWERTYUIOPASDFGHJKLZXCVBNM") for _ in range(10)])
    user.extra = extra
    session.commit()
    session.close()
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            .text{text-indent: 10px;
            align: "justify";}
        </style>
    </head>
    """ + f"""<body style="width: 100%; margin: 0px;">
    <div style="display: inline-block; width: 100%; background: #FF9900;">
        <p style="margin: 2%; font-weight: bold; font-size: 20px; color: #000000;">Mysen</p>
    </div>
    <div style="display: inline-block; width: 96%; margin-left: 2%;">
        <p class="text">
            Вам пришло это письмо, потому что кто-то захотел изменить пароль от вашего аккаунта. Если это были не вы, никому
            не говорите код и проигнорируйте это письмо. Код для восстановления пароля:
        </p>
        <p align="center" style="font-size: 40px; color: #ED760E">{extra}</p>
        <p class="text">Это письмо отправленно автоматически, на него не нужно отвечать.</p>
    </div>
    </body>
    </html>
    """

    # part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # msg.attach(part1)
    msg.attach(part2)
    smtpObj = smtplib.SMTP('smtp.yandex.ru', 587)
    smtpObj.starttls()
    smtpObj.login(me, 'mysen2021')
    smtpObj.sendmail(me, you, msg.as_string())
    smtpObj.quit()


def get(data):
    return list(map(int, data.split(";")))


@app.route("/create_user", methods=['GET', 'POST'])
def create_user():
    login = request.args.get("l", default="", type=str)
    password = sha224(request.args.get("p", default="", type=str).encode()).hexdigest()
    mail = request.args.get("m", default="", type=str).replace(" ", "").lower()

    session = db_session.create_session()
    users_login = list(map(lambda x: x.login, session.query(User).all()))
    users_mail = list(map(lambda x: x.mail, session.query(User).all()))

    if login in users_login:
        return "busy"
    elif not validate(mail):
        return "invalid"
    elif mail in users_mail:
        return "mail"
    else:
        user = User()
        user.login = login
        user.password = password
        user.mail = mail
        session.add(user)
        session.commit()
        return str(user.id)


@app.route("/check_user", methods=['GET', 'POST'])
def check_user():
    login = request.args.get("l", default="", type=str)
    password = sha224(request.args.get("p", default="", type=str).encode()).hexdigest()
    session = db_session.create_session()
    user = session.query(User).filter(User.login == login).first()
    if user is None:
        return "not ok"
    if password == user.password:
        return str(user.id)
    return "not ok"


@app.route("/change_mail", methods=['GET', 'POST'])
def change_mail():
    id = request.args.get("i", default="", type=int)
    password = request.args.get("p", default="", type=str)
    mail = request.args.get("m", default="", type=str)

    session = db_session.create_session()
    user = session.query(User).filter(User.id == id).first()

    if user.password == password:
        user.mail = mail
        session.commit()
        return "ok"
    else:
        return "bad password"


@app.route("/change_password", methods=['GET', 'POST'])
def change_password():
    id = request.args.get("i", default="", type=str)
    old_password = request.args.get("op", default="", type=str)
    new_password = request.args.get("np", default="", type=str)

    session = db_session.create_session()
    user = session.query(User).filter(User.id == id).first()

    if user.password == old_password:
        user.password = new_password
        session.commit()
        return "ok"
    else:
        return "bad password"


@app.route("/change_login", methods=['GET', 'POST'])
def change_login():
    user_id = request.args.get("ui", default="", type=int)
    new_login = request.args.get("nl", default="", type=str)
    password = sha224(request.args.get("p", default="", type=str).encode()).hexdigest()

    session = db_session.create_session()
    user = session.query(User).filter(User.id == user_id).first()

    if user.password != password:
        return "bad password"
    user.login = new_login
    session.commit()


@app.route("change_image", methods=['GET', 'POST'])
def change_image():
    user_id = request.args.get("ui", default="", type=int)


# @app.route("/change_user_password", methods=['GET', 'POST'])
# def change_user_password():
#     id = request.args.get("i", default="", type=int)
#     password = request.args.get("p", default="", type=str)
#
#     session = db_session.create_session()
#     user = session.query(User).filter(User.id == id).first()
#     if user is None:
#         return "unauthorized"
#
#     user.password = password
#     session.commit()
#     session.close()
#     return "ok"

# @app.route("/delete_me", methods=['GET', 'POST'])
# def delete_me():
#     id = request.args.get("i", default="", type=int)
#     password = request.args.get("p", default="", type=str)
#
#     session = db_session.create_session()
#     user = session.query(User).filter(User.id == id).first()
#
#     if user.password == password:
#         session.delete(user)
#         session.commit()
#         return "ok"
#     else:
#         return "bad password"

# @app.route("/resend_mail", methods=['GET', 'POST'])
# def resend_mail():
#     id = request.args.get("i", default="нет", type=int)
#     sendmail = threading.Thread(target=send_mail, args=(id,))
#     sendmail.start()
#     return "ok"

# @app.route("/check_mail", methods=['GET', 'POST'])
# def check_mail():
#     id = request.args.get("i", default="нет", type=int)
#     extra = request.args.get("e", default="нет", type=str).replace(" ", "").upper()
#     session = db_session.create_session()
#     user = session.query(User).filter(User.id == id).first()
#     if user is None:
#         return "unauthorized"
#     if user.extra == extra:
#         return "yes"
#     return "no"

# @app.route("/exist_user", methods=['GET', 'POST'])
# def exist_user():
#     login = request.args.get("l", default="", type=str)
#     session = db_session.create_session()
#     user = session.query(User).filter(User.login == login).first()
#     if user is None:
#         return "no"
#     sendmail = threading.Thread(target=send_mail, args=(user.id,))
#     sendmail.start()
#     return str(user.id)

@app.route("/send_message", methods=['GET', 'POST'])
def send_message():
    message = request.args.get("m", default="", type=str)
    chat_id = request.args.get("ci", default="", type=int)
    user_id = request.args.get("ui", default="", type=int)

    session = db_session.create_session()

    msg = MSG()
    msg.text = message
    msg.user = user_id
    msg.chat = chat_id
    session.add(msg)

    chat = session.query(Chat).filter(Chat.id == chat_id).first()
    chat.msg = msg.id + ';' + chat.msg
    session.commit()


@app.route("/edit_message", methods=['GET', 'POST'])
def edit_message():
    id = request.args.get("i", default="", type=int)
    new_msg = request.args.get("nm", default="", type=int)

    session = db_session.create_session()

    msg = session.query(MSG).filter(MSG.id == id).first()
    msg.text = new_msg
    session.commit()


@app.route("/delete_message", methods=['GET', 'POST'])
def delete_message():
    msg_id = request.args.get('mi', default="", type=int)
    user_id = request.args.get('ui', default="", type=int)

    session = db_session.create_session()

    msg = session.query(MSG).filter(MSG.id == msg_id).first()
    if msg.user != user_id:
        return "Not your message"

    chat_id = msg.chat
    chat = session.query(Chat).filter(Chat.id == chat_id)
    temp = chat.msg.split(';')
    del temp[temp.index(msg_id)]
    chat.msg = ';'.join(temp)
    session.commit()


@app.route("/get_messages", methods=['GET', 'POST'])
def get_messages():
    chat_id = request.args.get("ci", default="", type=int)
    count = request.args.get("co", default=0, type=int)

    session = db_session.create_session()

    chat = session.query(Chat).filter(Chat.id == chat_id).first()
    s = chat.msg.split(';')
    if count >= len(s):
        return "end"
    d = {}
    h = session.query(MSG).filter(MSG.id == int(s[count])).first()
    u = session.query(User).filter(User.id == int(h.user)).first()
    d["user"] = u.login
    d["text"] = h.text
    return d


@app.route("/get_chat", methods=['GET', 'POST'])
def get_chat():
    chat_id = request.args.get("ci", default="", type=int)

    session = db_session.create_session()

    chat = session.query(Chat).filter(Chat.id == chat_id).first()
    return chat.name


# for admin:
@app.route("/add_user", methods=['GET', 'POST'])
def add_user():
    chat_id = request.args.get("ci", default="", type=int)
    user_id = request.args.get("ui", default="", type=int)

    session = db_session.create_session()

    chat = session.query(Chat).filter(Chat.id == chat_id).first()
    chat.users += ";" + user_id

    user = session.query(User).filter(User.id == user_id).first()
    user.chats += ";" + chat_id
    session.commit()


@app.route("/del_user", methods=['GET', 'POST'])
def del_user():
    chat_id = request.args.get("ci", default="", type=int)
    user_id = request.args.get("ui", default="", type=int)

    session = db_session.create_session()

    chat = session.query(Chat).filter(Chat.id == chat_id).first()
    temp = chat.users.split(';')
    del temp[temp.index(str(user_id))]
    chat.users = ';'.join(temp)
    session.commit()


def main():
    # app.run(port=int(os.environ.get("PORT")), host='0.0.0.0')
    # app.run(port=8080, host='192.168.56.1')
    app.run(port=54321)


if __name__ == '__main__':
    x = threading.Thread(target=main)
    x.start()
