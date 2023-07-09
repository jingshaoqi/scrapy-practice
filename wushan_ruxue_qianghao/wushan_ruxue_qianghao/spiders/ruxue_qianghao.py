import scrapy
import  re
import json
from urllib.parse import urljoin
import time
from urllib.parse import urlencode
from datetime import datetime
import logging
import logging.config

#logging.basicConfig(filename='logging.log', level=logging.DEBUG, format='%(asctime)s %(funcName)s:%(lineno)d %(message)s', encoding='utf-8', filemode='a')

class RuxueQianghaoSpider(scrapy.Spider):
    name = 'ruxue_qianghao'
    allowed_domains = ['wsemal.com']
    #start_urls = ['https://wsemal.com/XQZS/JW/JW_iframe.aspx']
    start_urls = ['https://wwww.baidu.com']
    form_data = {'__EVENTTARGET': '',
                 '__EVENTARGUMENT': '',
                 '__VIEWSTATE': '',
                 '__VIEWSTATEGENERATOR': '',
                 '__EVENTVALIDATION': ''
                 }
    TextBox_XM = ''
    TextBox_SFZH = ''
    TextBox_FJDZ = '-2'
    TextBox_JZDZ = '-2'
    TextBox_JFRXM = ''
    TextBox_JFRSFZH = ''
    TextBox_TelePhone = ''
    jw_main_url = ''
    jw_main_url_referer = ''
    s_time = datetime.now()

    def __init__(self, student_file=None, *args, **kwargs):
        super(RuxueQianghaoSpider, self).__init__(*args, **kwargs)
        stu_info = None
        with open(student_file, mode='r', encoding='utf-8') as fs:
            stu_info = json.load(fs)
        self.TextBox_XM = stu_info['TextBox_XM']
        self.TextBox_SFZH = stu_info['TextBox_SFZH']
        self.TextBox_FJDZ = stu_info['TextBox_FJDZ']
        self.TextBox_JFRXM = stu_info['TextBox_JFRXM']
        self.TextBox_JFRSFZH = stu_info['TextBox_JFRSFZH']
        self.TextBox_TelePhone = stu_info['TextBox_TelePhone']
        self.TextBox_XM = stu_info['TextBox_XM']
        log_path = '{}_{}.log'.format(self.TextBox_SFZH, self.TextBox_XM)
        self.init_logging(log_path)

    def init_logging(self, log_path):
        logger = logging.getLogger()
        # 创建日志格式，每个Handler格式可以不同
        fh_formatter = logging.Formatter('%(asctime)s %(funcName)s:%(lineno)d %(message)s')
        # 输出到文件的Handler
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.DEBUG)
        fh.mode = 'a'
        fh.encoding = 'utf-8'
        # handler中使用日志格式
        fh.setFormatter(fh_formatter)
        # 向log文件添加Handler
        logger.addHandler(fh)

    def start_requests(self):
        headers ={'Upgrade-Insecure-Requests': '1',
                  'Sec-Fetch-User': '?1'}
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse, dont_filter=True)

    def parse(self, response):
        logging.info(response.text)
        #items = response.xpath('//iframe[contains(@src, "main")]/@src')
        items = response.xpath('//iframe[@id="mainFrame"]/@src')
        if items is None or len(items) <= 0:
            return
        end_pr = items.get()
        main_url = urljoin(response.url, end_pr)  # https://wsemal.com/XQZS/JW/JWmain.aspx
        logging.info(main_url)
        headers = {'TE': 'trailers',
                   'Sec-Fetch-Dest': 'iframe',
                   'Sec-Fetch-Mode': 'navigate',
                   'Sec-Fetch-Site': 'same-origin',
                   'Upgrade-Insecure-Requests': '1',}
        # 这里保存发现还没开始的时候的请求url和头
        self.jw_main_url = main_url
        self.jw_main_url_referer = response.url
        # go to jw main.aspx web
        yield scrapy.Request(url=main_url, headers=headers, callback=self.JWmain, dont_filter=True)


    def JWmain(self, response):
        logging.info(response.text)
        items_tr = response.xpath('//center/table/tr/td/table/tr')
        print('has {} lines'.format(len(items_tr)))
        for j in items_tr:
            itd = j.xpath('./td')
            if len(itd) < 7:
                continue
            school = itd[2].xpath('./text()')
            school_t = school.get()
            # 巫峡幼儿园 机关幼儿园 平湖幼儿园 西坪幼儿园 白杨幼儿园 圣泉幼儿园 南峰小学附属幼儿园
            if school_t.find('南峰小学') < 0:
                continue
            school_url = itd[6].xpath('./a/@href')
            school_url_t = school_url.get()
            # https://wsemal.com/XQZS/JW/JW_ZSBM1.aspx?XX=XQ001&ID=13&TT=2023/6/18^%^209:00:00
            qh_rukou_url_full = urljoin(response.url, school_url_t)
            # 输出请求的URL
            logging.info('school_url_full:{}'.format(qh_rukou_url_full))

            # wait
            desttime = '2023-6-28 9:00:00 000000'
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
            self.s_time = datetime.now()
            headers = {'TE': 'trailers',
                       'Sec-Fetch-Dest': 'iframe',
                       'Sec-Fetch-Mode': 'navigate',
                       'Sec-Fetch-Site': 'same-origin',
                       'Upgrade-Insecure-Requests': '1', }
            yield scrapy.Request(url=qh_rukou_url_full, headers=headers,
                                 callback=self.qh_ru_kou_check, dont_filter=True) #添加身份证号验证
            break

    def qh_ru_kou_check(self, response):
        logging.info(response.text)
            # 提取formdata信息
        # 查看状态
        zt = response.xpath('//tr/td/span[@id="Label_ZT"]/text()')
        if zt is  None or len(zt) <= 0:
            logging.info('check code or response')
            return
        zt_s = zt.get()
        if zt_s.find('进行中') < 0:
            #点击返回
            logging.info('状态是:{}'.format(zt_s))
            time.sleep(0.05)
            headers = {'Referer': self.jw_main_url_referer,
                       'Sec-Fetch-Dest': 'iframe',
                       'Sec-Fetch-Mode': 'navigate',
                       'Sec-Fetch-Site': 'same-origin',
                       'Upgrade-Insecure-Requests': '1', }
            yield scrapy.Request(url=self.jw_main_url, headers=headers, callback=self.JWmain, dont_filter=True)

        self.form_data['ScriptManager1'] = 'UpdatePanelAA|LinkButtonSFZH'
        self.form_data['__EVENTTARGET'] = 'LinkButtonSFZH'
        self.form_data['__LASTFOCUS'] = ''
        self.form_data['TextBox_XM'] = ''
        self.form_data['TextBox_SFZH'] = self.TextBox_SFZH
        self.form_data['TextBox_FJDZ'] = ''
        self.form_data['TextBox_JZDZ'] = ''
        self.form_data['TextBox_JFRXM'] = ''
        self.form_data['TextBox_JFRSFZH'] = ''
        self.form_data['TextBox_TelePhone'] = ''
        self.form_data['__ASYNCPOST'] = 'true'

        event_argument = response.xpath('//input[@id="__EVENTARGUMENT"]/@value')
        self.form_data['__EVENTARGUMENT'] = event_argument.extract()[0] if len(event_argument) > 0 else ''
        view_state = response.xpath('//input[@id="__VIEWSTATE"]/@value')
        self.form_data['__VIEWSTATE'] = view_state.extract()[0] if len(view_state) > 0 else ''
        event_validation = response.xpath('//input[@id="__EVENTVALIDATION"]/@value')
        self.form_data['__EVENTVALIDATION'] = event_validation.extract()[0] if len(event_validation) > 0 else ''
        view_state_generator = response.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')
        self.form_data['__VIEWSTATEGENERATOR'] = view_state_generator.extract()[0] if len(view_state_generator) > 0 else ''

        headers = {'Referer': response.url,
                   'X-Requested-With': 'XMLHttpRequest',
                   'X-MicrosoftAjax': 'Delta=true',
                   'Cache-Control': 'no-cache',
                   'Sec-Fetch-Dest': 'empty',
                   'Sec-Fetch-Mode': 'cors',
                   'Sec-Fetch-Site': 'same-origin',
                   'TE': 'trailers',
                   'Accept': '*/*',
                   'Origin': 'https://wsemal.com',
                   'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',}
        bodystr = urlencode(self.form_data, encoding='utf-8')
        logging.info('length:{} bodystr:{}'.format(len(bodystr), bodystr))
        yield scrapy.Request(url=response.url, method="POST", body=bodystr, headers=headers,
                             callback=self.SFZh_check_parse, dont_filter=True)

    def SFZh_check_parse(self, response):
        logging.info(response.text)
        # 提取formdata信息
        view_state = re.findall(r'__VIEWSTATE\|(.+?)\|', response.text)
        view_generator = re.findall(r'__VIEWSTATEGENERATOR\|(.+?)\|', response.text)
        event_validation = re.findall(r'__EVENTVALIDATION\|(.+?)\|', response.text)
        self.form_data['ScriptManager1'] = 'UpdatePanelAA|Button1'
        self.form_data['__VIEWSTATE'] = view_state[0] if len(view_state) > 0 else ''
        self.form_data['__EVENTVALIDATION'] = event_validation[0] if len(event_validation) > 0 else ''
        self.form_data['__VIEWSTATEGENERATOR'] = view_generator[0] if len(view_generator) > 0 else ''
        self.form_data['__EVENTTARGET'] = ''
        self.form_data['__EVENTARGUMENT'] = ''
        self.form_data['__LASTFOCUS'] = ''
        self.form_data['TextBox_XM'] = self.TextBox_XM
        self.form_data['TextBox_SFZH'] = self.TextBox_SFZH
        self.form_data['TextBox_FJDZ'] = self.TextBox_FJDZ
        self.form_data['TextBox_JZDZ'] = self.TextBox_JZDZ
        self.form_data['TextBox_JFRXM'] = self.TextBox_JFRXM
        self.form_data['TextBox_JFRSFZH'] = self.TextBox_JFRSFZH
        self.form_data['TextBox_TelePhone'] = self.TextBox_TelePhone
        self.form_data['__ASYNCPOST'] = 'true'
        self.form_data['Button1'] = '提交申请'
        headers = {'Referer': response.url,
                   'X-Requested-With': 'XMLHttpRequest',
                   'X-MicrosoftAjax': 'Delta=true',
                   'Cache-Control': 'no-cache',
                   'Sec-Fetch-Dest': 'empty',
                   'Sec-Fetch-Mode': 'cors',
                   'Sec-Fetch-Site': 'same-origin',
                   'TE': 'trailers',
                   'Accept': '*/*',
                   'Origin': 'https://wsemal.com',
                   'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',}
        bodystr = urlencode(self.form_data, encoding='utf-8')
        req_url = response.url
        logging.info('length:{} bodystr:{}'.format(len(bodystr), bodystr))
        yield scrapy.Request(url=req_url, method="POST", body=bodystr, headers=headers,
                             callback=self.submit_info, dont_filter=True)

    def submit_info(self, response):
        logging.info(response.text)
        e_time = datetime.now()
        c=e_time-self.s_time
        logging.info('cost:{}'.format(c))
        print(response.text)
        ind = response.text.find('抢注成功')
        if ind < 0:
            logging.info('抢注失败，再次请求')
            headers = {'Referer': self.jw_main_url_referer,
                       'TE': 'trailers',
                       'Sec-Fetch-Dest': 'iframe',
                       'Sec-Fetch-Mode': 'navigate',
                       'Sec-Fetch-Site': 'same-origin',
                       'Upgrade-Insecure-Requests': '1', }
            yield scrapy.Request(url=self.jw_main_url, headers=headers, callback=self.JWmain,
                                 dont_filter=True)
        else:
            logging.info('抢注成功')




