#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, time, json
import random
import re
import sqlite3
import threading
from io import open

from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities  import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_acks.protocolentities      import OutgoingAckProtocolEntity
from yowsup.layers.protocol_presence.protocolentities    import *


def set_interval(func, sec, self):
    def func_wrapper():
        set_interval(func, sec, self)
        func(self)
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def random_line(afile, linen):
    with open(afile, encoding='utf8') as fp:
        for i, line in enumerate(fp):
            if i == linen:
                return(line)

def lines(afile):
    ins = -1
    with open(afile, encoding='utf8') as fp:
        for i, line in enumerate(fp):
            ins += 1
    return ins

def loer(self):
    REPLV = ['Önceden1', 'Önceden2', 'Önceden3']
    TIMEL = 5400
    CEL_FALI = ['Ucretlı fal için v.çb .v.b.b.b.b.b.']
    #CELSE = ['Öncelikle hoşgeldin. Lütfen dikkatlice oku kafanda herhangi bir soru işareti kalmasın. Kahveni içtikten sonra bana kahve fincanının 3-4 adet farklı açıdan fotoğraflarını çekip at.', 'Hoş geldin', 'Hoş geldin laaaaaa']
    conn = sqlite3.connect('data.db')
    max_lines = lines('cevaplar.txt')
    brs = 0

    fls = conn.execute("SELECT * from USERS WHERE sent = 0")
    times = str(int(time.time()))
    for row in fls:
        if(int(times) - int(row[4]) >= TIMEL):
            outgoingMessageProtocolEntity = TextMessageProtocolEntity(
                random_line('cevaplar.txt',brs),
                to = row[5])
            conn.execute("UPDATE USERS set sent = 1 where number = "+row[3]+"")
            conn.commit()
            self.toLower(outgoingMessageProtocolEntity)
            brs += 1
            if brs > max_lines:
                brs = 0


class EchoLayer(YowInterfaceLayer):
    def presence_available(self):
        entity = AvailablePresenceProtocolEntity()
        self.toLower(entity)

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        #send receipt otherwise we keep receiving the same message over and over
        if True:
            print ('-- Yeni Mesaj --')
            timex = str(int(time.time()))
            number = re.findall('^(.*?)\@.*', messageProtocolEntity.getFrom())[0]
            name = messageProtocolEntity.getParticipant()
            senderid = messageProtocolEntity.getFrom()
            chatid = messageProtocolEntity.getId()

            self.toLower(messageProtocolEntity.ack())
            self.toLower(messageProtocolEntity.ack(True))


            if messageProtocolEntity.getType() == 'text':
                print ('-- Mesaj Gönderimi')
                print('Number: ', number)
                print('Name: ', name)
                print('Sender: ', senderid)
                print('ChatID: ', chatid)
                print('Body: ', messageProtocolEntity.getType())


                conn = sqlite3.connect('data.db')

                cursor2 = conn.execute("SELECT * from numbers WHERE number = "+number+"")
                ins2 = 0
                for row2 in cursor2:
                    ins2 += 1
                    

                if(ins2 == 0):
                    outwMessageProtocolEntity = TextMessageProtocolEntity(
                        "Öncelikle Hoş Geldin. Şunu belirtmek isterimki sadece 1 hakkın var iyi değerlendir. Nasıl yapılacağı instagram profilim de yazıyor yoğun olduğumdan bu mesajı direk atıyorum. Eğer analizin 3 saat içinde gelmedi ise yoğunlukdan görememişizdir. Yeniden atman gerekli insanlık hali olabilir.",
                        to = messageProtocolEntity.getFrom())

                    outwMessageProtocolEntity2 = TextMessageProtocolEntity(
                        "En önemlisi aşırı yoğun olduğumdan analizin gelirse lütfen yorumunu sayfama yaparsan sevinirim burdan yazma çünkü çok yoğunum",
                        to = messageProtocolEntity.getFrom())
                    self.toLower(outwMessageProtocolEntity)
                    self.toLower(outwMessageProtocolEntity2)

                    conn.execute("INSERT INTO Numbers (number) VALUES (?)", (number,)  )

                    conn.commit()
                else:
                    print('Önceden gönderilmiş mesaj')
                #receipt = OutgoingReceiptProtocolEntity(messageProtocolEntity.getId(), messageProtocolEntity.getFrom(), 'read', messageProtocolEntity.getParticipant())
                #self.toLower(receipt)

            else:
                print('Number: ', number)
                print('Name: ', name)
                print('Sender: ', senderid)
                print('ChatID: ', chatid)
                print('Body: ', messageProtocolEntity.getType())

                print ('-- Fotoğraf Gönderimi')
                conn = sqlite3.connect('data.db')

                cursor = conn.execute("SELECT * from USERS WHERE number = "+number+" ")
                ins = 0
                for row in cursor:
                    ins += 1


                if(ins == 0):
                    conn.execute("INSERT INTO Users (name, sent, number, datex, sender_id, chat_id) VALUES (?, 0, ?, ?, ?, ?)", (name,number,timex,senderid,chatid)  )
                    conn.commit()

                cursor8 = conn.execute("SELECT * from USERS WHERE number = "+number+" AND sent = 1 ")
                ins8 = 0
                for row8 in cursor8:
                    ins8 += 1

                if(ins8 > 0):
                    print('Önceden gönderilmiş fotoğraf')


                cursor72 = conn.execute("SELECT * from numbers WHERE number = "+number+"")
                ins72 = 0
                for row72 in cursor72:
                    ins72 += 1

                if(ins72 == 0):
                    conn.execute("INSERT INTO Numbers (number) VALUES (?)", (number,)  )

                    conn.commit()
                else:
                    print('Önceden gönderilmiş mesaj')

                #receipt = OutgoingReceiptProtocolEntity(messageProtocolEntity.getId(), messageProtocolEntity.getFrom(), 'read', messageProtocolEntity.getParticipant())
                #self.toLower(receipt)

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())


    @ProtocolEntityCallback("success")
    def onSuccess(self, entity):
        set_interval(loer, 15, self)
        self.presence_available()
