import scrapy
import time
from datetime import datetime

class ScrapytestSpider(scrapy.Spider):
    name = "scrapytest"
    allowed_domains = ["www.qq.com"]
    start_urls = ['https://www.qq.com']

    def parse(self, response):
        localtm = time.localtime()
        #print('name:{} {} time:{}'.format(self.name,response.url, localtm))
        dt = datetime.now()
        st1 = dt.strftime('%Y-%m-%d %H:%M:%S %f')

        dt2 = datetime(2023, 7, 2, 14, 30, 0)
        st2 = dt2.strftime('%Y-%m-%d %H:%M:%S %f')

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

