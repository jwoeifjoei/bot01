import json
from datetime import timedelta
import redis
from mysql.connector import (connection)
import config
from datetime import datetime
import datetime
import re


message=("'{'ok': True, 'result': {'entities': [{'offset': 0, 'type': 'hashtag', 'length': 10}, {'offset': 41, 'type': 'mention', 'length': 10}, {'offset': 169, 'type': 'hashtag', 'length': 13}, {'offset': 183, 'type': 'hashtag', 'length': 12}], 'chat': {'first_name': 'Matteo', 'username': 'Matteob99', 'last_name': 'B99', 'type': 'private', 'id': 28746630}, 'message_id': 1068, 'text': '#Richiesta \nUtente: Matteo B99\nUsername: @Matteob99\nId: 28746630\ntipo: film\nanno: 2016\nContenuto "   "Richiesta: \nsdsddssddssd\nSblocco Prossima Richiesta:2017-05-15\nUserTag: #User28746630\n#Richiesta22', 'date': 1493625851, 'from': {'first_name': 'torrent italia bot', 'username': 'TorrentItaliaBot', 'id': 372066297}}}'"
)

b,c=re.split(":", message)[22].split(',')
print(b)
