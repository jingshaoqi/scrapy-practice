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

class sch_info:
    start_time = None
    full_url = ''
    def __init__(self, start_time = None, full_url=None):
        self.start_time = start_time
        self.full_url = full_url

class RuxueQianghaoSpider(scrapy.Spider):
    name = 'ruxue_qianghao'
    allowed_domains = ['wsemal.com']
    #start_urls = ['https://wsemal.com/XQZS/JW/JW_iframe.aspx']
    start_urls = ['http://localhost:8023/garden/JW_iframe.aspx.html']
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
    choose_schools = []
    cur_school = ''
    qh_rukou_url_full = ''
    s_time = datetime.now()
    dict_sch = {}

    def __init__(self, student_file=None, *args, **kwargs):
        super(RuxueQianghaoSpider, self).__init__(*args, **kwargs)
        stu_info = None
        with open(student_file, mode='r', encoding='utf-8') as fs:
            stu_info = json.load(fs)
        self.TextBox_XM = stu_info['TextBox_XM']
        self.TextBox_SFZH = stu_info['TextBox_SFZH']
        self.TextBox_FJDZ = stu_info['TextBox_FJDZ']
        self.TextBox_JZDZ = stu_info['TextBox_JZDZ']
        self.TextBox_JFRXM = stu_info['TextBox_JFRXM']
        self.TextBox_JFRSFZH = stu_info['TextBox_JFRSFZH']
        self.TextBox_TelePhone = stu_info['TextBox_TelePhone']
        self.choose_schools = stu_info['choose_schools']
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
        logging.info('start requests')
        headers ={'Upgrade-Insecure-Requests': '1',
                  'Sec-Fetch-User': '?1'}
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse, dont_filter=True)

    def parse(self, response):
        logging.info(response.text)
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
            # 巫峡幼儿园 机关幼儿园 平湖幼儿园 西坪幼儿园 白杨幼儿园 圣泉幼儿园 南峰小学附属幼儿园
            school_name = itd[2].xpath('./text()').get() #学校名称
            if school_name not in self.choose_schools:
                continue
            start_time = itd[4].xpath('./text()').get()  # 学校开始抢号
            school_url = itd[6].xpath('./a/@href').get() #url
            full_url = urljoin(response.url, school_url) # https://wsemal.com/XQZS/JW/JW_ZSBM1.aspx?XX=XQ001&ID=13&TT=2023/6/18^%^209:00:00
            sch_info1 = sch_info(start_time, full_url)
            self.dict_sch[school_name] = sch_info1
        yield from self.deal_process()

    def deal_process(self):
        if len(self.choose_schools) <= 0:
            return
        self.cur_school = self.choose_schools[0]
        self.choose_schools.pop(0)
        sch_info1 = self.dict_sch[self.cur_school]
        dst_time = datetime.strptime(sch_info1.start_time, '%Y/%m/%d %H:%M:%S')#'2023/6/28 9:00:00 000000'
        # wait
        wt = 0.0
        wt_delta = 0.01
        while 1:
            localtm = datetime.now()
            if localtm >= dst_time:
                break
            else:
                if wt >= 1.0:
                    dt = dst_time - localtm
                    print('left time:{}'.format(dt))
                    wt = 0.0
                time.sleep(wt_delta)
                wt += wt_delta

        self.qh_rukou_url_full = sch_info1.full_url
        headers = {'TE': 'trailers',
                   'Sec-Fetch-Dest': 'iframe',
                   'Sec-Fetch-Mode': 'navigate',
                   'Sec-Fetch-Site': 'same-origin',
                   'Upgrade-Insecure-Requests': '1', }
        next_url = self.qh_rukou_url_full
        yield scrapy.Request(url=next_url, headers=headers,
                             callback=self.qh_ru_kou_check, dont_filter=True)
    def qh_ru_kou_check(self, response):
        logging.info(response.text)
        #这里可能会返回网络拥堵或者其他什么的，待测试再定
        if response.text.find('网络拥堵') >= 0 or response.text.find('errorpath') >= 0:
            headers = {'Sec-Fetch-Dest': 'iframe',
                       'Sec-Fetch-Mode': 'navigate',
                       'Sec-Fetch-Site': 'same-origin',
                       'Upgrade-Insecure-Requests': '1', }
            next_url = response.url
            yield scrapy.Request(url=next_url, headers=headers, callback=self.qh_ru_kou_check, dont_filter=True)
            return
        zt = response.xpath('//tr/td/span[@id="Label_ZT"]/text()')
        if zt is None or len(zt) <= 0:
            logging.info('check code or response')
            return
        zt_s = zt.get()
        if zt_s.find('进行中') < 0:
            if zt_s.find('结束') >= 0 or zt_s.find('满') >= 0: #此学校已经结束就进入下一个页面
                yield from self.deal_process()
                return
            time.sleep(0.05) #即将开始就等待
            headers = {'Sec-Fetch-Dest': 'iframe',
                       'Sec-Fetch-Mode': 'navigate',
                       'Sec-Fetch-Site': 'same-origin',
                       'Upgrade-Insecure-Requests': '1', }
            next_url = response.url
            yield scrapy.Request(url=next_url, headers=headers, callback=self.qh_ru_kou_check, dont_filter=True)
            return

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
        next_url = response.url
        yield scrapy.Request(url=next_url, method="POST", body=bodystr, headers=headers,
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
            #返回此学校已满的情形
            total_s = response.xpath('//tr/td/span[@id="Label_ZSRS"]/text()')
            yb_s = response.xpath('//tr/td/span[@id="Label_YBRS"]/text()')
            if total_s is not None and len(total_s) > 0 and yb_s is not None and len(yb_s) > 0:
                total_n = int(total_s.get())
                yb_n = int(yb_s.get())
                if yb_n >= total_n: #表示已经满了就要选择下一个学校
                    yield from self.deal_process()
                    return
            logging.info('抢注失败，再次请求')
            headers = {'TE': 'trailers',
                       'Sec-Fetch-Dest': 'iframe',
                       'Sec-Fetch-Mode': 'navigate',
                       'Sec-Fetch-Site': 'same-origin',
                       'Upgrade-Insecure-Requests': '1', }
            next_url = self.qh_rukou_url_full
            yield scrapy.Request(url=next_url, headers=headers, callback=self.qh_ru_kou_check,
                                 dont_filter=True)
        else:
            logging.info('抢注成功')




