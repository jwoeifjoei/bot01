# -*- coding: utf-8 -*-
# Copyright (c) 2016-2017 Marco Aceti <dev@marcoaceti.it>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import botogram
import botogram.objects.base
from mysql.connector import (connection)
import config
from .objects.callback import Callback
from .objects.user import User
from .updates import callback, messages
import re

def disconnectmysql(cursor,cnx):
    emp_no = cursor.lastrowid
    cnx.commit()
    cursor.close()
    cnx.close()

def connectmysql():
    cnx = connection.MySQLConnection(user=config.usermariadb,
                                  password=config.passwordmariadb,
                                  host=config.hostmariadb,
                                  database=config.databasemariadb)
    cursor=cnx.cursor()
    return cursor, cnx

class CallbackQuery(botogram.objects.base.BaseObject):
    def __init__(self, update):
        super().__init__(update)

    required = {
        "id": str,
        "from": botogram.User,
        "data": str,
    }
    optional = {
        "inline_message_id": str,
        "message": botogram.Message,
    }
    replace_keys = {
        "from": "sender"
    }

botogram.Update.optional["callback_query"] = CallbackQuery

bot = botogram.create(config.BOT_TOKEN)


@bot.command("start")
def start(chat, message):
    u = User(message.sender)
    u.state("home")
    u.increaseStat('stats_command_start')
    sender = message.sender
    cursor, cnx = connectmysql()
    cursor.execute("SELECT id_utentetg FROM info_utente WHERE id_utentetg='"+str(sender.id)+"'")
    idsender=' '
    for row in cursor.fetchall():
        idsender=row[0]
    if (str(sender.id)==str(idsender)):
        _message="Ti sei già iscritto a questo bot, premi un tasto per continuare."
    elif(idsender==' '):
        cursor.execute('SELECT MAX(id_utente) FROM info_utente')
        for row in cursor.fetchall():
            idtelegram=1+int(row[0])
        dati=(str(sender.id),str(idtelegram))
        cursor.execute("INSERT INTO info_utente (id_utentetg,id_utente,posizione) VALUES (%s,%s,'0');",dati)

        text_messagelog="#Avvio \nUtente: "+str(sender.name)+"\nUsername: @"+str(sender.username)+"\nId: "+str(sender.id)+"\nUserTag: #User"+str(sender.id)

        querry="SELECT idchattg FROM chatsend WHERE tipo=0"
        cursor.execute(querry)
        for row in cursor.fetchall():
            bot.chat(row[0]).send(text_messagelog,syntax="HTML")

    else:
        text_message="Errore Generale"
    if(str(chat.type)!="private"):
        text_message="Avviami in chat privata\n"+text_message
        bot.api.call('sendMessage', {
        'chat_id': chat.id, 'text': text_message, 'parse_mode': 'HTML', 'reply_markup':
        json.dumps(
            {'inline_keyboard': [
            [{"text": "Avviami in privata", "url": "t.me/TorrentItaliaBot"}]
            ]}
        )
    })
    else:
        querry="SELECT ruolo FROM info_utente WHERE id_utentetg='"+str(u.id)+"'"
        cursor.execute(querry)
        for row in cursor.fetchall():
            ruolo=int(row[0])
        if(ruolo==1 or ruolo==2):
            u.state("home-admin")
            text = (
                "bot del gruppo https://t.me/Utorrentitalia ancora in costruzione "
            )
            message =bot.api.call("sendMessage", {
                "chat_id": chat.id,  "text": text,
                "parse_mode": "HTML", "reply_markup":
                json.dumps(
                    {'inline_keyboard': [
                        [{"text": "help", "callback_data": "help"},
                        {"text":"gestione","callback_data":"gestione"}],
                         [{"text": "richiesta", "callback_data": "richiesta"},
                        {"text": "ℹ️ Altre informazioni", "callback_data": "info"}]
                    ]}
                )
            })
            print(message["result"]["message_id"])
        else:
            u.state("home")
            text = (
                "bot del gruppo https://t.me/Utorrentitalia ancora in costruzione "
            )
            message=bot.api.call("sendMessage", {
                "chat_id": chat.id, "text": text,
                "parse_mode": "HTML", "reply_markup":
                json.dumps(
                    {'inline_keyboard': [
                        [{"text": "help", "callback_data": "help"},
                         {"text": "richiesta", "callback_data": "richiesta"}],
                        [{"text": "ℹ️ Altre informazioni", "callback_data": "info"}]
                    ]}
                )
            })
            print(message["result"]["message_id"])



    disconnectmysql(cursor,cnx)
@bot.command("sendall")
def sendall_command(chat,message,args):
    cursor, cnx = connectmysql()
    sender = message.sender
    if(str(sender.id)==str('28746630')):
        querry="SELECT id_utentetg FROM info_utente"
        cursor.execute(querry)
        for row in cursor.fetchall():
            bot.chat(row[0]).send(str(message.text)[9:],syntax="HTML")


@bot.process_message
def process_messages(message):
    u = User(message.sender)
    sender=message.sender
    messages.process_messages(bot, message, u, sender)


def process_callback(__bot, __chains, update):
    del (__bot, __chains)  # Useless arguments from botogram
    cb = Callback(update)
    u = User(cb.sender)
    u.increaseStat('stats_callback_count')

    callback.process_callback(bot, update, u)

bot.register_update_processor("callback_query", process_callback)
