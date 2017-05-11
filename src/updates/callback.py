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
from datetime import datetime
from datetime import timedelta
from datetime import date
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
            [{"text": "home", "callback_data": "home"}],
        ]}
    )
    })
    return text

def process_callback(bot, update, u):
    import time
    start_time = time.time()
    cursor, cnx = connectmysql()
    cb = Callback(update)
    querry="SELECT ruolo FROM info_utente WHERE id_utentetg='"+str(u.id)+"'"
    cursor.execute(querry)
    for row in cursor.fetchall():
        ruolo=int(row[0])
    if cb.query == "home":
        u.stateold(u.state().decode('utf-8'))
        if(ruolo==1 or ruolo==2):
            u.state("home-admin")
            text = (
                    "Questo è il bot di T.me/TorrentItalia "
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
                    "Questo è il bot di T.me/TorrentItalia "
                    )
                bot.api.call("editMessageText", {
                    "chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
                    "parse_mode": "HTML", "reply_markup":
                    json.dumps(
                        {'inline_keyboard': [
                        [{"text": "Help", "callback_data": "help"},
                         {"text": "Richiesta", "callback_data": "richiesta"}],
                        [{"text": "ℹ️ Altre Informazioni", "callback_data": "info"}]
                        ]}
                        )
                        })
    elif cb.query == "gestione":
        u.stateold(u.state().decode('utf-8'))
        querry="SELECT ruolo FROM info_utente WHERE id_utentetg='"+str(u.id)+"'"
        cursor.execute(querry)
        for row in cursor.fetchall():
            ruolo=int(row[0])
        if ruolo==1:
            text=(
            "Da qui puoi gestire le Richieste"
            )
            bot.api.call("editMessageText",{
                "chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
                "parse_mode": "HTML", "reply_markup":
                json.dumps(
                    {'inline_keyboard': [
                        [{"text": "Gestione Richieste", "callback_data": "grichieste"},
                        {"text":"Lista Canali e Gruppi ","callback_data":"vgruppistaff"}],
                        [{"text": "Indietro", "callback_data": u.stateold().decode('utf-8')}]
                ]}
            )
            })
            u.state("gestione-mod")
        elif ruolo==2:
            text=(
            "Da qui puoi gestire le richieste e lo staff del bot"
            )
            bot.api.call("editMessageText",{
                "chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
                "parse_mode": "HTML", "reply_markup":
                json.dumps(
                    {'inline_keyboard': [
                        [{"text": "Gestione Richieste", "callback_data": "grichieste"}],
                        [{"text":"Lista Canali ed i Gruppi ","callback_data":"vgruppistaff"},
                        {"text":"Gestione Staff","callback_data":"gmod"}],
                        [{"text": "Indietro", "callback_data": u.stateold().decode('utf-8')}]
                    ]}
                )
                })
            chat.send(u.state().decode('utf-8'))
            u.state("gestione-admin")
    elif cb.query =="richiesta":
        u.stateold(u.state().decode('utf-8'))
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
        if(datatest=='.'or str(datetime.now())>=str(datatest+ timedelta(days=giorni_attesa)) or ruolo==1 or ruolo==2 or ruolo==0 or  str(datatest)=='NoneType'):
                u.state("richiesta")
                bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": "Manda il <strong>Tipo</strong> della richiesta",
                    "parse_mode": "HTML", "reply_markup":
                    json.dumps(
                    {'inline_keyboard': [
                    [{"text":"Film",  "callback_data":"richiesta01"},
                    {"text":"Giochi","callback_data":"richiesta02"}],
                    [{"text":"Libri","callback_data":"richiesta03"},
                    {"text":"Altro","callback_data":"richiesta04"}],
                    [{"text": "Home", "callback_data": "home"}, {"text": "richieste effettuate", "callback_data": "richiestaf"}]
                        ]}
                    )
                    })
        else:
            bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": "testo da fare p.s. viva i  testi \n \n \n testo ",
                "parse_mode": "HTML", "reply_markup":
                json.dumps(
                {'inline_keyboard': [
                [{"text": "Home", "callback_data": "home"}, {"text": "richieste effettuate", "callback_data": "richiestaf"}]
                    ]}
                )
                })
    elif cb.query=="richiesta01":
        u.stateold(u.state().decode('utf-8'))
        u.state("richiesta01")
        querry="INSERT INTO info_richieste(tipo,id_utente_richiedente,data_richiesta)    VALUES('film','"+str(u.id)+"','"+str(datetime.now())+"'); "
        cursor.execute(querry)
        text=(
            "Ora manda <b>l'anno</b>"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
                [{"text": ''+str(date.today().year),  "callback_data":"richiesta05"},
                 {"text":''+str(date.today().year-1),"callback_data":"richiesta06"}],
                [{"text":''+str(date.today().year-2),"callback_data":"richiesta07"},
                 {"text":"Altro","callback_data":"richiesta08"}],
                [{"text": "Indietro", "callback_data": u.stateold().decode('utf-8') }],
                [{"text": "Annulla Richiesta", "callback_data": "annularichiesta"}]
            ]}
        )
        })
    elif cb.query=="richiesta02":
        u.stateold(u.state().decode('utf-8'))
        u.state("richiesta02")
        querry="INSERT INTO info_richieste(tipo,id_utente_richiedente,data_richiesta)    VALUES('film','"+str(u.id)+"','"+str(datetime.now())+"'); "
        cursor.execute(querry)
        text=(
            "Ora manda <b>l'anno</b>"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
                [{"text": ''+str(date.today().year),  "callback_data":"richiesta05"},
                 {"text": ''+str(date.today().year-1),"callback_data":"richiesta06"}],
                [{"text": ''+str(date.today().year-2),"callback_data":"richiesta07"},
                 {"text":"Altro","callback_data":"richiesta08"}],
                [{"text": "Indietro", "callback_data": u.stateold().decode('utf-8') }],
                [{"text": "Annulla Richiesta", "callback_data": "annularichiesta"}],
            ]}
        )
        })
    elif cb.query=="richiesta03":
        u.stateold(u.state().decode('utf-8'))
        u.state("richiesta03")
        querry="INSERT INTO info_richieste(tipo,id_utente_richiedente,data_richiesta)    VALUES('film','"+str(u.id)+"','"+str(datetime.now())+"'); "
        cursor.execute(querry)
        text=(
            "Ora manda <b>l'anno</b>"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
                [{"text": ''+str(date.today().year),  "callback_data":"richiesta05"},
                 {"text":''+str(date.today().year-1),"callback_data":"richiesta06"}],
                [{"text":''+str(date.today().year-2),"callback_data":"richiesta07"},
                 {"text":"Altro","callback_data":"richiesta08"}],
                [{"text": "Indietro", "callback_data": u.stateold().decode('utf-8') }],
                [{"text": "Annulla richiesta", "callback_data": "annularichiesta"}],
            ]}
        )
        })
    elif cb.query=="richiesta04":
        u.stateold(u.state().decode('utf-8'))
        u.state("richiesta04")
        text=(
                  "Adesso manda il <b>Titolo/Nome</b>"
              )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
              "parse_mode": "HTML", "reply_markup":
          json.dumps(
                  {'inline_keyboard': [
                      [{"text": "Indietro", "callback_data": u.stateold().decode('utf-8')}],
                      [{"text": "Annulla richiesta", "callback_data": "annularichiesta"}],
                  ]}
              )
          })
    elif cb.query=="richiesta05":
        u.stateold(u.state().decode('utf-8'))
        u.state("richiesta09")
        querry="SELECT max(id_richiesta) FROM info_richieste where id_utente_richiedente='"+str(u.id)+"'"
        cursor.execute(querry)
        for row in cursor.fetchall():
            id_richiesta=row[0]
        querry="UPDATE info_richieste SET anno='"+str(date.today().year)+"' WHERE id_richiesta='"+str(id_richiesta)+"'";
        cursor.execute(querry)
        text=(
            "Adesso manda il <b>Titolo/Nome</b>"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
            [{"text": "Annulla Richiesta", "callback_data": "annularichiesta"}],
            [{"text": "Indietro", "callback_data": "richiesta03"}],
            ]}
            )
            })
    elif cb.query=="richiesta06":
        u.stateold(u.state().decode('utf-8'))
        u.state("richiesta09")
        querry="SELECT max(id_richiesta) FROM info_richieste where id_utente_richiedente='"+str(u.id)+"'"
        cursor.execute(querry)
        for row in cursor.fetchall():
            id_richiesta=row[0]
        querry="UPDATE info_richieste SET anno='"+str(date.today().year-1)+"' WHERE id_richiesta='"+str(id_richiesta)+"'";
        cursor.execute(querry)
        text=(
            "Adesso manda il <b>Titolo/Nome</b>"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
            [{"text": "Annulla Richiesta", "callback_data": "annularichiesta"}],
            [{"text": "Indietro", "callback_data": "richiesta03"}],
            ]}
            )
            })
    elif cb.query=="richiesta07":
        u.stateold(u.state().decode('utf-8'))
        u.state("richiesta09")
        querry="SELECT max(id_richiesta) FROM info_richieste where id_utente_richiedente='"+str(u.id)+"'"
        cursor.execute(querry)
        for row in cursor.fetchall():
            id_richiesta=row[0]
        querry="UPDATE info_richieste SET anno='"+str(date.today().year-2)+"' WHERE id_richiesta='"+str(id_richiesta)+"'";
        cursor.execute(querry)
        text=(
            "Adesso manda il <b>Titolo/Nome</b>"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
            [{"text": "Annulla Richiesta", "callback_data": "annularichiesta"}],
            [{"text": "Indietro", "callback_data": "richiesta03"}],
            ]}
            )
            })
    elif cb.query=="richiesta08":
        u.stateold(u.state().decode('utf-8'))
        u.state("richiesta08")
        text=(
            "Ora manda <b>l'anno</b>"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
            [{"text": "Annulla Richiesta", "callback_data": "annularichiesta"}],
            [{"text": "Indietro", "callback_data": "richiesta03"}],
            ]}
            )
            })
    elif cb.query=="richiesta10":
        if(ruolo==1 or ruolo==2):
            querry="SELECT idrichiesta FROM idmessaggiorichiesta where idmessaggio='"+str(cb.message.message_id)+"' AND idchat='"+str(cb.chat.id)+"'"
            cursor.execute(querry)
            for row in cursor.fetchall():
                id_richiesta=int(row[0])
            querry="UPDATE info_richieste SET status=2 WHERE id_richiesta='"+str(id_richiesta)+"'"
            cursor.execute(querry)
            text=(
                "frank spanato"
            )
            bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
            "parse_mode": "HTML",
                })
            querry="SELECT idmessaggio,tipo,idchat FROM idmessaggiorichiesta WHERE idrichiesta='"+str(id_richiesta)+"'"
            cursor.execute(querry)
            for row in cursor.fetchall():
                if(cb.chat.id!=row[0]):
                    if(int(row[1])==1):
                        text=(
                        "la richiesta è stata accettata"
                        )
                        bot.api.call("editMessageText", {"chat_id": row[2], "message_id": row[0], "text": text,
                        "parse_mode": "HTML",
                            })
                    elif(int(row[1])==0):
                        text=(
                            "richiesta accettata testo in elaborazione "
                        )
                        message=bot.api.call("editMessageText", {"chat_id": row[2], "message_id": row[0], "text": text,
                        "parse_mode": "HTML", "reply_markup":
                                json.dumps(
                                    {'inline_keyboard': [
                                    [{"text": "home", "callback_data": "home"}],
                                    [{"text": "status richieste","callback_data":"richiestaf"}]
                                    ]}
                                    )
                                })


        else:
            return
    elif cb.query=="richiesta11":
        if(ruolo==1 or ruolo==2):
            querry="SELECT idrichiesta FROM idmessaggiorichiesta where idmessaggio='"+str(cb.message.message_id)+"' AND idchat='"+str(cb.chat.id)+"'"
            cursor.execute(querry)
            for row in cursor.fetchall():
                id_richiesta=int(row[0])
            querry="UPDATE info_richieste SET status=2 WHERE id_richiesta='"+str(id_richiesta)+"'"
            cursor.execute(querry)
            querry="SELECT idmessaggio,tipo,idchat FROM idmessaggiorichiesta WHERE idrichiesta='"+str(id_richiesta)+"'"
            cursor.execute(querry)
            for row in cursor.fetchall():
                if(cb.chat.id!=row[0]):
                    if(int(row[1])==1):
                        text=(
                        "la richiesta non è stata accettata inviare la motivazione? p.s. finire il testo"
                        )
                        bot.api.call("editMessageText", {"chat_id": row[2], "message_id": row[0], "text": text,
                        "parse_mode": "HTML","reply_markup":
                                json.dumps(
                                    {'inline_keyboard':[
                                    [{"text":"no","callback_data":"richiesta12"},{"text":"si","callback_data":"richiesta13"}]
                                    ]}
                                )
                            })


        return
    elif cb.query=="richiesta12":
        if(ruolo==1 or ruolo==2):
            querry="SELECT idrichiesta FROM idmessaggiorichiesta where idmessaggio='"+str(cb.message.message_id)+"' AND idchat='"+str(cb.chat.id)+"'"
            cursor.execute(querry)
            for row in cursor.fetchall():
                id_richiesta=int(row[0])
            querry="UPDATE info_richieste SET status=2 WHERE id_richiesta='"+str(id_richiesta)+"'"
            cursor.execute(querry)
            querry="SELECT idmessaggio,tipo,idchat FROM idmessaggiorichiesta WHERE idrichiesta='"+str(id_richiesta)+"'"
            cursor.execute(querry)
            for row in cursor.fetchall():
                    if(int(row[1])==1):
                        text=(
                        "la richiesta non è stata accettata  p.s. finire il testo"
                        )
                        bot.api.call("editMessageText", {"chat_id": row[2], "message_id": row[0], "text": text,
                        "parse_mode": "HTML"
                            })
                    elif(int(row[1])==0):
                        text=(
                        "richiesta non accettata testo in elaborazione "
                        )
                        message=bot.api.call("editMessageText", {"chat_id": row[2], "message_id": row[0], "text": text,
                            "parse_mode": "HTML", "reply_markup":
                                json.dumps(
                                    {'inline_keyboard': [
                                        [{"text": "home", "callback_data": "home"}],
                                        [{"text": "status richieste","callback_data":"richiestaf"}]
                                        ]}
                                        )
                                        })
    elif cb.query=="richiesta13":
        if(ruolo==1 or ruolo==2):
            u.stateold(u.state().decode('utf-8'))
            u.state("richiesta13")
            querry="SELECT idrichiesta FROM idmessaggiorichiesta where idmessaggio='"+str(cb.message.message_id)+"' AND idchat='"+str(cb.chat.id)+"'"
            cursor.execute(querry)
            for row in cursor.fetchall():
                id_richiesta=int(row[0])
            text01=(
                "specificarla in privato p.s. testo da finire"
                )
            bot.api.call("editMessageText", {"chat_id":cb.chat.id, "message_id": cb.message.message_id, "text": text01,
             "parse_mode": "HTML"})

            text02=(
                "specifica il motivo p.s. testo da finire anche i bottoni"
                )
            message=bot.api.call("sendMessage",{"chat_id": u.id, "text":text02,
            "parse_mode":"HTML","reply_markup":
                json.dumps(
                {'inline_keyboard':[
                [{"text":"già fatta","callback_data":"richiesta14"}],
                [{"text":"scrivi","callback_data":"richiesta15"}]
                ]}
                )})
            idmessaggio=message["result"]["message_id"]
            u.richiestaid(str(id_richiesta))
            querry="INSERT INTO idmessaggiorichiesta(idmessaggio,idrichiesta,tipo,idchat) VALUES('"+str(idmessaggio)+"','"+str(id_richiesta)+"','2','"+str(u.id)+"')"
            cursor.execute(querry)
    elif cb.query=="richiesta14":
        if(ruolo==1 or ruolo==2):
            querry="SELECT idrichiesta FROM idmessaggiorichiesta where idmessaggio='"+str(cb.message.message_id)+"' AND idchat='"+str(cb.chat.id)+"'"
            cursor.execute(querry)
            for row in cursor.fetchall():
                id_richiesta=int(row[0])
            querry="UPDATE info_richieste SET status=2 WHERE id_richiesta='"+str(id_richiesta)+"'"
            cursor.execute(querry)
            querry="SELECT idmessaggio,tipo,idchat FROM idmessaggiorichiesta WHERE idrichiesta='"+str(id_richiesta)+"'"
            cursor.execute(querry)
            for row in cursor.fetchall():
                    if(int(row[1])==1):
                        text=(
                        "la richiesta non è stata accettata perchè è stata già fatta p.s. finire il testo"
                        )
                        bot.api.call("editMessageText", {"chat_id": row[2], "message_id": row[0], "text": text,
                        "parse_mode": "HTML"
                            })
                    elif(int(row[1])==0):
                        text=(
                        "richiesta non accettata perchè è  stata già fatta testo in elaborazione "
                        )
                        message=bot.api.call("editMessageText", {"chat_id": row[2], "message_id": row[0], "text": text,
                            "parse_mode": "HTML", "reply_markup":
                                json.dumps(
                                    {'inline_keyboard': [
                                        [{"text": "home", "callback_data": "home"}],
                                        [{"text": "status richieste","callback_data":"richiestaf"}]
                                        ]}
                                        )
                                        })
                    elif(int(row[1])==2):
                        text=(
                        "richiesta non accetta perchè è staga già fatta "
                        )
                        bot.api.call("editMessageText",{"chat_id":row[2],"message_id": row[0],"text":text,
                        "parse_mode":"HTML"})
    elif cb.query=="richiesta15":
        u.stateold(u.state().decode('utf-8'))
        u.state("richiesta15")
        text01=("invia la motivazione")
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text01,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
                [{"text":"indietro","callback_data":u.stateold().decode('utf-8')}],
                [{"text": "home", "callback_data": "home"}],
            ]}
        )
        })

    elif cb.query=="richiestaf":
        u.stateold(u.state().decode('utf-8'))
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": "🚧 In costruzione 🚧",
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
                [{"text": "home", "callback_data": "home"}],
            ]}
        )
        })
    elif cb.query=="annularichiesta":
        u.stateold(u.state().decode('utf-8'))
        u.state("annullarichiesta")
        text=(
            "sicuro di voler annullare la richiesta"
        )
        bot.api.call("editMessageText", {"chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
        "parse_mode": "HTML", "reply_markup":
        json.dumps(
            {'inline_keyboard': [
                [{"text": "si ", "callback_data": "annullarichiesta01"}],
                [{"text": "no", "callback_data": str(u.stateold().decode('utf-8')) }],
            ]}
            )
            })
        u.state("annullarichiesta")
    elif cb.query=="annullarichiesta01":
        u.stateold(u.state().decode('utf-8'))
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
    print("--- %s seconds ---" % (time.time() - start_time)+str(cb.query)+"     "+str(u.id))
    disconnectmysql(cursor,cnx)
