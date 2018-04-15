import datetime
import json
import threading
from time import sleep
from lxml.etree import HTML

import re
from download import Download
from db import MysqlClient

class Scheduler(object):
    def __init__(self):
        self.download = Download()
        self.db = MysqlClient()
        # self.user_url_list = []
        # self.threads = []

    def run(self):
        # self.get_yiparts_parts()
        # self.get_yiparts_detail()
        self.get_car()

    def get_yiparts_parts(self):
        url = 'http://www.yiparts.com/parts/'
        response = self.download.get_html(url)
        doc = HTML(response)
        names = doc.xpath('//div[@id="sort"]/div/ul/li/a/text()')
        name_ens = doc.xpath('//div[@id="sort"]/div/ul/li/a/@href')
        for name, name_en in zip(names,name_ens):
            item_name = name.strip()
            item_name_en = name_en[7:-1]
            sql = 'insert into yiparts(yiparts_name,yiparts_name_en) VALUES ("{item_name}","{item_name_en}")'.format(item_name=item_name, item_name_en=item_name_en)
            print(sql)
            self.db.save(sql)

    def get_yiparts_detail(self):
        sql = 'select * from yiparts'
        results = self.db.find_all(sql)
        for res in results:
            url = 'http://www.yiparts.com/parts/{yiparts_name_en}/'.format(yiparts_name_en=res[2])
            print(url)
            response = self.download.get_html(url)
            doc = HTML(response)
            names = doc.xpath('//div[@id="sort2"]/div/div/a/span[2]/text()')
            name_ens = doc.xpath('//div[@id="sort2"]/div/div/a/@href')
            imgs = doc.xpath('//div[@id="sort2"]/div/div/a/span[1]/img/@src')
            for name, name_en, img in zip(names, name_ens, imgs):
                item_name = name.strip()
                item_name_en = name_en[11:-1]
                item_img = img
                sql = 'insert into yiparts_detail(pid, detail_name, detail_name_en, detail_img) VALUES ("{pid}", "{detail_name}", "{detail_name_en}", "{detail_img}")'.format(
                    pid=res[0], detail_name=item_name, detail_name_en=item_name_en, detail_img=item_img)
                print(sql)
                self.db.save(sql)

    def get_car(self):
        url = 'http://www.yiparts.com/Car/AjaxBrand/'
        response = self.download.get_html(url)
        jsonobj = json.loads(response)
        for res in jsonobj:
            # sql = 'insert into car(valid, pinyin, car_name) VALUES ("{valid}", "{pinyin}", "{car_name}")'.format(
            #     valid=res['id'], pinyin=res['initial'], car_name=res['name'])
            # print(sql)
            # self.db.save(sql)

            url_level1 = 'http://www.yiparts.com/Car/AjaxModel?level=1&bid={bid}'.format(bid=res['id'])
            response =self.download.get_html(url_level1)
            # print(url_level1)
            doc = HTML(response)
            m1ids = doc.xpath('//ul[@class="M1List"]/li/@m1id')
            names1 = doc.xpath('//ul[@class="M1List"]/li/a/text()')
            # for m1id, name in zip(m1ids, names1):
            #     level1_sql = 'insert into car_level1(level1_bid, level1_m1id, level1_name) VALUES ("{level1_bid}", "{level1_m1id}", "{level1_name}")'.format(
            #         level1_bid=res['id'], level1_m1id=m1id, level1_name=name)
            #     print(level1_sql)
            #     self.db.save(level1_sql)

            for m1id in m1ids:
                level2_url = 'http://www.yiparts.com/Car/AjaxModel?level=2&m1id={m1id}'.format(m1id=m1id)
                response = self.download.get_html(level2_url)
                doc = HTML(response)
                m2ids = doc.xpath('//ul[@class="M2List MenuSwitch"]/li/@m2id')
                names2 = doc.xpath('//ul[@class="M2List MenuSwitch"]/li/a/text()')
                # for m2id, name in zip(m2ids, names2):
                #     if m2id[:2] == 'm1':
                #         continue
                #     else:
                #         level2_sql = 'insert into car_level2(level2_m1id, level2_m2id, level2_name) VALUES ("{level2_m1id}", "{level2_m2id}", "{level2_name}")'.format(level2_m1id=m1id, level2_m2id=m2id, level2_name=name)
                #         print(level2_sql)
                #         self.db.save(level2_sql)

                for m2id in m2ids:
                    if m2id[:2] == 'm1':
                        continue
                    level3_url = 'http://www.yiparts.com/Car/AjaxModel?level=3&m2id={m2id}'.format(m2id=m2id)
                    response = self.download.get_html(level3_url)
                    print(level3_url)
                    doc = HTML(response)
                    m3_info = doc.xpath('string(//table[@class="table2"]/tbody/tr/td[1]/a/@onclick)')
                    print(m3_info)
                    if len(m3_info)>0:
                        m3_info = m3_info.split('\'')
                        m3id = m3_info[1]
                        ypc_m3id = m3_info[3]
                    else:
                        m3id =''
                        ypc_m3id = ''
                    chexing = doc.xpath('string(//table[@class="table2"]/tbody/tr/td[1])')
                    nianfen = doc.xpath('string(//table[@class="table2"]/tbody/tr/td[2])')
                    fadongji = doc.xpath('string(//table[@class="table2"]/tbody/tr/td[3])')
                    gonglv = doc.xpath('string(//table[@class="table2"]/tbody/tr/td[4])')
                    pailiang = doc.xpath('string(//table[@class="table2"]/tbody/tr/td[5])')
                    biansuqi = doc.xpath('string(//table[@class="table2"]/tbody/tr/td[6])')
                    ranliao = doc.xpath('string(//table[@class="table2"]/tbody/tr/td[7])')
                    cheshen = doc.xpath('string(//table[@class="table2"]/tbody/tr/td[8])')
                    qianzhidong = doc.xpath('string(//table[@class="table2"]/tbody/tr/td[9])')
                    houzhidong = doc.xpath('string(//table[@class="table2"]/tbody/tr/td[10])')
                    zhuchezhidong = doc.xpath('string(//table[@class="table2"]/tbody/tr/td[11])')
                    qudongfangshi = doc.xpath('string(//table[@class="table2"]/tbody/tr/td[11])')

                    level3_sql = 'insert into car_level3(level3_m2id, level3_m3id, ypc_m3id, chexing, nianfen, fadongji, gonglv, pailiang, biansuqi, ranliao, cheshen, qianzhidong, houzhidong, zhuchezhidong, qudongfangshi) ' \
                                 'VALUES ("{level3_m2id}", "{level3_m3id}", "{ypc_m3id}","{chexing}","{nianfen}","{fadongji}","{gonglv}","{pailiang}","{biansuqi}","{ranliao}","{cheshen}","{qianzhidong}","{houzhidong}","{zhuchezhidong}","{qudongfangshi}")'\
                        .format(level3_m2id=m2id, level3_m3id=m3id, ypc_m3id=ypc_m3id,chexing=chexing,nianfen=nianfen,fadongji=fadongji,gonglv=gonglv,pailiang=pailiang,biansuqi=biansuqi,ranliao=ranliao,cheshen=cheshen,qianzhidong=qianzhidong,houzhidong=houzhidong,zhuchezhidong=zhuchezhidong,qudongfangshi=qudongfangshi)
                    print(level3_sql)
                    self.db.save(level3_sql)




