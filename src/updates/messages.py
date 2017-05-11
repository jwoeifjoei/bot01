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
from datetime import timedelta
import redis
from mysql.connector import (connection)
import config
from datetime import datetime
import datetime
from ..objects.callback import Callback
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



def process_messages(bot, message, u,sender ):
    import time
    start_time = time.time()
    state = u.state().decode('utf-8')  # Redis returns strings in bytes, state must be converted in strings
    chat = message.chat
    cursor, cnx = connectmysql()
    if str(chat.type)=="private":
        if state == 'richiesta04':
            u.stateold(u.state().decode('utf-8'))
            if not message.text:
                return
            querry="INSERT INTO info_richieste(tipo,id_utente_richiedente,data_richiesta)    VALUES('film','"+str(u.id)+"','"+str(datetime.datetime.now())+"'); "
            cursor.execute(querry)
            text=(
                "ora manda l'anno"
                )
            bot.api.call("sendMessage", {"chat_id": chat.id,  "text": text,
                "parse_mode": "HTML", "reply_markup":
                    json.dumps(
                        {'inline_keyboard': [
                        [{"text": str(datetime.date.today().year),  "callback_data":"richiesta05"},
                        {"text":str(datetime.date.today().year-1),"callback_data":"richiesta06"}],
                        [{"text":str(datetime.date.today().year-2),"callback_data":"richiesta07"},
                        {"text":"altro","callback_data":"richiesta08"}],
                        [{"text": "annulla richiesta", "callback_data": "annularichiesta"}],
                        ]}
                        )
                    })
        elif state =="richiesta08":
            u.stateold(u.state().decode('utf-8'))
            if( str(message.text).isdigit()==False or int(message.text)>int(datetime.date.today().year-2 or not  message.text)):
                return
            else:
                querry="SELECT max(id_richiesta) FROM info_richieste where id_utente_richiedente='"+str(u.id)+"'"
                cursor.execute(querry)
                for row in cursor.fetchall():
                    id_richiesta=int(row[0])+1
                querry="UPDATE info_richieste SET anno='"+str(message.text)+"' WHERE id_richiesta='"+str(id_richiesta)+"'";
                cursor.execute(querry)
                text=(
                    "ora manda il contenuto della richiesta"
                )
                bot.api.call("sendMessage", {"chat_id": chat.id,  "text": text,
                    "parse_mode": "HTML", "reply_markup":
                        json.dumps(
                            {'inline_keyboard': [
                            [{"text": "annulla richiesta", "callback_data": "annularichiesta"}],
                            ]}
                            )
                        })
                u.state("richiesta09")
        elif state=="richiesta09":
            u.stateold(u.state().decode('utf-8'))
            if  not message.text:
                return
            else:
                querry="SELECT max(id_richiesta) FROM info_richieste where id_utente_richiedente='"+str(u.id)+"'"
                cursor.execute(querry)
                for row in cursor.fetchall():
                    id_richiesta=int(row[0])
                messaggio=message.text
                querry="UPDATE info_richieste  SET contenuto_richiesta='"+str(message.text)+"' WHERE id_richiesta='"+str(id_richiesta)+"'"
                cursor.execute(querry)
                text=(
                    "ora la richiesta sarà controllata dagli admin se andrà bene oppure no verà notificato qui sul bot"
                )
                message=bot.api.call("sendMessage", {"chat_id": chat.id,  "text": text,
                    "parse_mode": "HTML", "reply_markup":
                        json.dumps(
                            {'inline_keyboard': [
                            [{"text": "home", "callback_data": "home"}],
                            ]}
                            )
                        })
                idmessaggio=message["result"]["message_id"]
                querry="INSERT INTO idmessaggiorichiesta(idmessaggio,idrichiesta,tipo,idchat) VALUES('"+str(idmessaggio)+"','"+str(id_richiesta)+"','0','"+str(chat.id)+"')"
                cursor.execute(querry)
                querry="SELECT * FROM info_richieste WHERE id_richiesta='"+str(id_richiesta)+"'"
                cursor.execute(querry)
                for row in cursor.fetchall():
                    richiestan=row[0]
                    anno=row[6]
                    tipo=row[7]
                    giorni_attesa=14
                    date_N_days_ago= datetime.datetime.now() + timedelta(days=giorni_attesa)
                text_messagelog="#Richiesta \nUtente: "+str(sender.name)+"\nUsername: @"+str(sender.username)+"\nTipo: "+str(tipo)+"\nAnno: "+str(anno)+"\nContenuto Richiesta: \n"+str(messaggio)+"\nSblocco Prossima Richiesta:"+str(date_N_days_ago)[:10]+"\nUserTag: #User"+str(u.id)+"\n#Richiesta"+str(richiestan)
                querry="SELECT idchattg FROM chatsend WHERE tipo='1'"
                cursor.execute(querry)
                for row in cursor.fetchall():
                    message =bot.api.call("sendMessage",{"chat_id": row[0], "text":text_messagelog,
                    "parse_mode":"HTML","reply_markup":
                        json.dumps(
                        {'inline_keyboard':[
                        [{"text":"acceta","callback_data":"richiesta10"}],
                        [{"text":"rifiuta","callback_data":"richiesta11"}]
                        ]}
                        )})
                    idmessaggio=message["result"]["message_id"]
                    querry="INSERT INTO idmessaggiorichiesta(idmessaggio,idrichiesta,tipo,idchat) VALUES('"+str(idmessaggio)+"','"+str(id_richiesta)+"','1','"+str(row[0])+"')"
                    cursor.execute(querry)
        elif state=="richiesta15":
            u.stateold(u.state().decode('utf-8'))
            u.state("richiesta16")
            if(  not  message.text):
                return
            else:
                id_richiesta=int(u.richiestaid().decode('utf-8'))
                querry="UPDATE info_richieste SET status=2 WHERE id_richiesta='"+str(id_richiesta)+"'"
                cursor.execute(querry)
                querry="SELECT idmessaggio,tipo,idchat FROM idmessaggiorichiesta WHERE idrichiesta='"+str(id_richiesta)+"'"
                cursor.execute(querry)
                for row in cursor.fetchall():
                        if(int(row[1])==1):
                            text=(
                            "la richiesta non è stata accettata perchè "+str(message.text)+" fatta p.s. finire il testo"
                            )
                            bot.api.call("editMessageText", {"chat_id": row[2], "message_id": row[0], "text": text,
                            "parse_mode": "HTML"
                                })
                        elif(int(row[1])==0):
                            text=(
                            "richiesta non accettata perchè "+str(message.text)+" testo in elaborazione "
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
                            "richiesta non accetta perchè "+str(message.text)+" "
                            )
                            bot.api.call("editMessageText",{"chat_id":row[2],"message_id": row[0],"text":text,
                            "parse_mode":"HTML"})


        else:
            return
        disconnectmysql(cursor,cnx)

    else:
        return
    print("--- %s seconds ---" % (time.time() - start_time)+str(state)+"     "+str(u.id))
