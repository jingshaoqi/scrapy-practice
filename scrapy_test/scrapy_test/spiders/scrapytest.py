import scrapy
import time
from datetime import datetime
import logging
import logging.config


logging.basicConfig(filename='logging.log', level=logging.DEBUG, format='%(asctime)s %(funcName)s:%(lineno)d %(message)s',  encoding='utf-8')
#logger = logging.getLogger(__name__)
#logging.config.fileConfig('logging.conf')


    # create logger
#logger = logging.getLogger('simpleExample')

class ScrapytestSpider(scrapy.Spider):
    name = "scrapytest"
    allowed_domains = ["www.qq.com"]
    #start_urls = ['http://192.168.2.101:8023//JW_ZSBM1.aspx.html']
    start_urls = ['http://192.168.2.101:8023/30-.html']


    def parse(self, response):
        if response.text.find('网络拥堵') >= 0:
            print('net is full')
        print(response.text)
        localtm = time.localtime()
        logging.info('asdfsadf')
        #print('name:{} {} time:{}'.format(self.name,response.url, localtm))
        dt = datetime.now()
        st1 = dt.strftime('%Y-%m-%d %H:%M:%S %f')
        #with open('t.txt', encoding=response.encoding, mode='w') as f:
        #windows10 下open打开的编码格式为cp936,而服务器返回的是utf-8
        with open('t.txt',encoding=response.encoding,  mode='w') as f:
            f.write(response.text)

        dt2 = datetime(2023, 7, 2, 14, 30, 0)
        st2 = dt2.strftime('%Y-%m-%d %H:%M:%S %f')

        select_school_name = '巫山二中'
        # 判断选择的学校是否已经满了
        ful_sch = response.xpath('//div[@id="UpdatePanel2"]/table/tr')
        choose_suc = 0
        for y in ful_sch:
            tds = y.xpath('./td/text()')
            if len(tds) < 6:
                continue
            sch_name = tds[1].get()
            if sch_name.find(select_school_name) < 0:
                continue
            num = int(tds[4].get())
            if num > 0:
                choose_suc = 1
            break
        if choose_suc == 0:
            # 再次选择
            select_school_name = '巫山二中'
            for y in ful_sch:
                tds = y.xpath('./td/text()')
                if len(tds) < 6:
                    continue
                sch_name = tds[1].get()
                if sch_name.find(select_school_name) < 0:
                    continue
                num = int(tds[4].get())
                if num > 0:
                    choose_suc = 1
                break
        if choose_suc == 0:
            print('cant find suitable school:{}'.format(select_school_name))
            return

        desttime = '2023-7-2 15:30:00'
        dt4 = datetime.strptime(desttime, '%Y-%m-%d %H:%M:%S')


        a2time = time.strptime(desttime, '%Y-%m-%d %H:%M:%S')

        desttime = '2023-7-2 8:30:00 000000'
        a2time = datetime.strptime(desttime, '%Y-%m-%d %H:%M:%S %f')
        wt = 0
        wt_delta = 0.01
        while 1:
            localtm = datetime.now()
            if localtm >= a2time:
                break
            else:
                if wt >= 1:
                    dt = a2time - localtm
                    print('left time:{}'.format(dt))
                    wt = 0
                time.sleep(wt_delta)
                wt += wt_delta

        print('')

