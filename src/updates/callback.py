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
import datetime
from datetime import datetime
from datetime import timedelta
import redis
from mysql.connector import (connection)
import config
from ..objects.callback import Callback
import re


r = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, password='CyVNDRIZng1f')

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

def incostruzione(cb):
    text=("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": "🚧 In costruzione 🚧",
    "parse_mode": "HTML", "reply_markup":
    json.dumps(
        {'inline_keyboard': [
            [{"text": "Home", "callback_data": "home"}],
        ]}
    )
    })
    return text

def process_callback(bot, update, u):
    cursor, cnx = connectmysql()
    cb = Callback(update)

    if cb.query == "home":
        querry="SELECT ruolo FROM info_utente WHERE id_utentetg='"+str(u.id)+"'"
        cursor.execute(querry)
        for row in cursor.fetchall():
            ruolo=int(row[0])
        if(ruolo==1 or ruolo==2):
            u.state("home-admin")
            text = (
                "Questo è il Bot del gruppo @Utorrentitalia"
            )
            bot.api.call("editMessageText", {
                "chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
                "parse_mode": "HTML", "reply_markup":
                json.dumps(
                    {'inline_keyboard': [
                        [{"text": "Help", "callback_data": "help"},
                        {"text":"Gestione","callback_data":"gestione"}],
                         [{"text": "Richiesta", "callback_data": "richiesta"},
                        {"text": "ℹ️ Altre informazioni", "callback_data": "info"}]
                    ]}
                )
            })
        else:
            u.state("home")
            text = (
                "Questo è il Bot del gruppo @Utorrentitalia"
            )
            bot.api.call("editMessageText", {
                "chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
                "parse_mode": "HTML", "reply_markup":
                json.dumps(
                    {'inline_keyboard': [
                        [{"text": "Help", "callback_data": "help"},
                         {"text": "Richiesta", "callback_data": "richiesta"}],
                        [{"text": "ℹ️ Altre informazioni", "callback_data": "info"}]
                    ]}
                )
            })
    elif: cb.query=="gestione":
        querry="SELECT ruolo FROM info_utente WHERE id_utentetg='"+str(u.id)+"'"
        cursor.execute(querry)
        for row in cursor.fetchall():
            ruolo=int(row[0])
        if ruolo==1:
            text(
            "Da qui puoi gestire le richieste degli utenti"
            )
            bot.api.call("editMessageText",{
                "chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
                "parse_mode": "HTML", "reply_markup":
                json.dumps(
                    {'inline_keyboard': [
                        [{"text": "Gestione Richieste", "callback_data": "grichieste"},
                        {"text":"Lista Canali e Gruppi ":"vgruppistaff"}],
                        [{"text": "Indietro", "callback_data": u.state().decode('utf-8')}]
                ]}
            )
            })
            u.state("gestione-mod")
        elif ruolo==2:
            text(
            "Da qui puoi gestire le richieste degli utenti e gli admin del bot"
            )
            bot.api.call("editMessageText",{
                "chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
                "parse_mode": "HTML", "reply_markup":
                json.dumps(
                    {'inline_keyboard': [
                        [{"text": "Gestione Richieste", "callback_data": "grichieste"},
                        {"text":"Lista Canali e Gruppi ","callback_data":"vgruppistaff"}],
                        [{"text":"Gestione dello staff:"gmod"}]
                        [{"text": "Indietro", "callback_data": u.state().decode('utf-8')}]
                ]}
            )
            })
            u.state("gestione-admin")
    
    elif cb.query =="richiesta":
        giorni_attesa=14
        querry="SELECT ruolo from info_utente WHERE id_utentetg='"+str(u.id)+"'"
        cursor.execute(querry)
        for row in cursor.fetchall():
            ruolo=row[0]
            ruolo=int(ruolo)
        datatest='.'
        if(ruolo==0):
            querry="SELECT data_richiesta FROM info_richieste WHERE id_utente_richiedente='"+str(u.id)+"'order by id_richiesta desc LIMIT 1"
            cursor.execute(querry)
            for row in cursor.fetchall():
                datatest=row[0]
        if(datatest=='.'or str(datetime.now())>=str(datatest+ timedelta(days=giorni_attesa)) or ruolo==2 or ruolo==3):
                u.state("richiesta")
                text =("Manda il genere della richiesta"                        )
                bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
                    "parse_mode": "HTML", "reply_markup":
                    json.dumps(
                    {'inline_keyboard': [
                    [{"text":"Film",  "callback_data":"richiesta01"},
                    {"text":"Giochi","callback_data":"richiesta02"}],
                    [{"text":"Libri","callback_data":"richiesta03"},
                    {"text":"Altro","callback_data":"richiesta04"}],
                    [{"text": "Home", "callback_data": "home"}, {"text": "richieste effettuate", "callback_data": "richiestaf"}],
            ]}
        )
    })
    elif cb.query=="richiesta01":
        u.state("richiesta01")
        querry="INSERT INTO info_richieste(tipo,id_utente_richiedente)    VALUES('film','"+str(u.id)+"'); "

        cursor.execute(querry)
        text=(
            "Ora manda l'anno"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
                [{"text": ''+str(datetime.date.today().year),  "callback_data":"richiesta05"},
                 {"text":''+str(datetime.date.today().year-1),"callback_data":"richiesta06"}],
                [{"text":''+str(datetime.date.today().year-2),"callback_data":"richiesta07"},
                 {"text":"Altro","callback_data":"richiesta08"}],
                [{"text": "Annulla Richiesta", "callback_data": "annularichiesta"}]
            ]}
        )
    })
    elif cb.query=="richiesta02":
        u.state("richiesta02")
        querry="INSERT INTO info_richieste(tipo,id_utente_richiedente) VALUES('gioco','"+str(u.id)+"')"
        cursor.execute(querry)
        text=(
            "Ora manda l'anno"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
                [{"text": ''+str(datetime.date.today().year),  "callback_data":"richiesta05"},
                 {"text": ''+str(datetime.date.today().year-1),"callback_data":"richiesta06"}],
                [{"text": ''+str(datetime.date.today().year-2),"callback_data":"richiesta07"},
                 {"text":"Altro","callback_data":"richiesta08"}],
                [{"text": "Annulla Richiesta", "callback_data": "annularichiesta"}],
            ]}
        )
    })
    elif cb.query=="richiesta03":
        u.state("richiesta03")
        querry="INSERT INTO info_richieste(tipo,id_utente_richiedente) VALUES('libri','"+str(u.id)+"')"
        cursor.execute(querry)
        text=(
            "Ora manda l'anno"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
                [{"text": ''+str(datetime.date.today().year),  "callback_data":"richiesta05"},
                 {"text":''+str(datetime.date.today().year-1),"callback_data":"richiesta06"}],
                [{"text":''+str(datetime.date.today().year-2),"callback_data":"richiesta07"},
                 {"text":"Altro","callback_data":"richiesta08"}],
                [{"text": "Annulla Richiesta", "callback_data": "annularichiesta"}],

            ]}
        )
    })



    elif cb.query=="richiesta04":
              u.state("richiesta04")
              text=(
                  "Ora manda il Titolo o il Nome"
              )
              bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
              "parse_mode": "HTML", "reply_markup":
              json.dumps(
                  {'inline_keyboard': [
                      [{"text": "Annulla Richiesta", "callback_data": "annularichiesta"}],
                      [{"text": "Indietro", "callback_data": "richiesta"}],
                      [{"text": "Indietro", "callback_data": "richiesta"}],
                  ]}
              )
          })

    elif cb.query=="richiesta05":
        u.state("richiesta09")
        querry="SELECT max(id_richiesta) FROM info_richieste where id_utente_richiedente='"+str(u.id)+"'"
        cursor.execute(querry)
        for row in cursor.fetchall():
            id_richiesta=row[0]
        querry="UPDATE info_richieste SET anno='"+str(datetime.date.today().year)+"' WHERE id_richiesta='"+str(id_richiesta)+"'";
        cursor.execute(querry)
        text=(
            "                      [{"text": "Indietro", "callback_data": "richiesta"}],
"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
            [{"text": "annulla richiesta", "callback_data": "annularichiesta"}],
            [{"text": "indietro", "callback_data": "richiesta03"}],
            ]}
            )
            })
    elif cb.query=="richiesta06":
        u.state("richiesta09")
        querry="SELECT max(id_richiesta) FROM info_richieste where id_utente_richiedente='"+str(u.id)+"'"
        cursor.execute(querry)
        for row in cursor.fetchall():
            id_richiesta=row[0]
        querry="UPDATE info_richieste SET anno='"+str(datetime.date.today().year-1)+"' WHERE id_richiesta='"+str(id_richiesta)+"'";
        cursor.execute(querry)
        text=(
            "ora manda il contenuto della richiesta"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
            [{"text": "annulla richiesta", "callback_data": "annularichiesta"}],
            [{"text": "indietro", "callback_data": "richiesta03"}],
            ]}
            )
            })
    elif cb.query=="richiesta07":
        u.state("richiesta09")
        querry="SELECT max(id_richiesta) FROM info_richieste where id_utente_richiedente='"+str(u.id)+"'"
        cursor.execute(querry)
        for row in cursor.fetchall():
            id_richiesta=row[0]
        querry="UPDATE info_richieste SET anno='"+str(datetime.date.today().year-2)+"' WHERE id_richiesta='"+str(id_richiesta)+"'";
        cursor.execute(querry)
        text=(
            "ora manda il contenuto della richiesta"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
            [{"text": "annulla richiesta", "callback_data": "annularichiesta"}],
            [{"text": "indietro", "callback_data": "richiesta03"}],
            ]}
            )
            })
    elif cb.query=="richiesta08":
        u.state("richiesta08")
        text=(
            "ora manda l'anno"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
            [{"text": "annulla richiesta", "callback_data": "annularichiesta"}],
            [{"text": "indietro", "callback_data": "richiesta03"}],
            ]}
            )
            })

    elif cb.query=="richiesta09":
        cb.message.message_id
    elif cb.query=="richiestaf":
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": "🚧 In costruzione 🚧",
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
                [{"text": "home", "callback_data": "home"}],
            ]}
        )
        })

    elif cb.query=="annularichiesta":
        text=(
            "sicuro di voler annullare la richiesta"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
                [{"text": "si ", "callback_data": "annullarichiesta01"}],
                [{"text": "no", "callback_data": str(u.state().decode('utf-8')) }],
            ]}
            )
            })
        u.state("annullarichiesta")

    elif cb.query=="annullarichiesta01":
        u.state("annullarichiesta01")
        querry="DELETE FROM info_richieste WHERE id_utente_richiedente='"+str(u.id)+"' order by id_richiesta desc LIMIT 1;"
        text=(
        "la richiesta è stata annulata"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
                [{"text": "home ", "callback_data": "home"}],
                [{"text": "richiesta", "callback_data": "richiesta" }],
            ]}
            )
            })

    disconnectmysql(cursor,cnx)
