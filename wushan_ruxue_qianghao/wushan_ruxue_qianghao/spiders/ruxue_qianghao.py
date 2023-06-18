import scrapy
import  re
import json
from urllib.parse import urljoin
import time
from urllib.parse import urlencode

class RuxueQianghaoSpider(scrapy.Spider):
    name = 'ruxue_qianghao'
    allowed_domains = ['wsemal.com']
    start_urls = ['https://wsemal.com/XQZS/JW/JW_iframe.aspx']
    headers = {'Referer': 'https://wsemal.com/CZBM/',
               'Host': 'wsemal.com',
               'Cookie': '',
               "User-Agent": "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
               "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
               "Accept-Encoding": "gzip, deflate, br",
               "Connection": "keep-alive",
               "Upgrade-Insecure-Requests": "1",
               "Sec-Fetch-Dest": "document",
               "Sec-Fetch-Mode": "navigate",
               "Sec-Fetch-Site": "none",
               "Sec-Fetch-User": "?1",
               "TE": "trailers",
               }
    form_data = {'__EVENTTARGET': '',
                 '__EVENTARGUMENT': '',
                 '__VIEWSTATE': '',
                 '__VIEWSTATEGENERATOR': '',
                 '__EVENTVALIDATION': ''
                 }

    def start_requests(self):
        # wait
        desttime = '2023-6-17 8:00:00'
        a2time = time.strptime(desttime, '%Y-%m-%d %H:%M:%S')
        while 1:
            localtm = time.localtime()
            if localtm >= a2time:
                break
            else:
                time.sleep(0.01)
        if self.headers.get('Cookie') is not None:
            self.headers.pop('Cookie')
        if self.headers.get('Referer') is not None:
            self.headers.pop('Referer')
        if self.headers.get('TE') is not None:
            self.headers.pop('TE')

        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse, dont_filter=True)

    def parse(self, response):
        with open('JW_iframe.html', 'w') as f:
            f.write(response.text)
        #items = response.xpath('//iframe[contains(@src, "main")]/@src')
        items = response.xpath('//iframe[@id="mainFrame"]/@src')
        if items is None:
            return
        if response.headers.get('Set-Cookie'):
            ckie = response.headers['Set-Cookie']
            fdf = str(ckie).split(';')
            # 只需要第一个
            for i in fdf:
                if i.find('SessionId') >= 0:
                    self.headers['Cookie'] = i  # ASP.NET_SessionId=3rg5mw45ldudcbmsvfnyayj0
                    break

        self.headers['Referer'] = response.url  # https://wsemal.com/XQZS/JW/JW_iframe.aspx
        end_pr = items.get()
        main_url = urljoin(response.url, end_pr)  # https://wsemal.com/XQZS/JW/JWmain.aspx
        print(main_url)

        self.headers['TE'] = 'trailers'
        if self.headers.get('Sec-Fetch-User') is not None:
            self.headers.pop('Sec-Fetch-User')

        # go to jw main.aspx web
        yield scrapy.Request(url=main_url, headers=self.headers, callback=self.JWmain)


    def JWmain(self, response):
        with open('JWmain.html', 'w') as f:
            f.write(response.text)
        items_tr = response.xpath('//center/table/tr/td/table/tr')
        print('has {} lines'.format(len(items_tr)))
        for j in items_tr:
            itd = j.xpath('./td')
            if len(itd) < 7:
                continue
            print('has seven td')
            school = itd[2].xpath('./text()')
            school_t = school.get()
            print(school_t)
            # 巫峡幼儿园 机关幼儿园 平湖幼儿园 西坪幼儿园 白杨幼儿园 圣泉幼儿园
            if school_t.find('机关幼儿园') < 0:
                continue
            school_url = itd[6].xpath('./a/@href')
            school_url_t = school_url.get()
            print(school_url_t)
            # https://wsemal.com/XQZS/JW/JW_ZSBM1.aspx?XX=XQ001&ID=13&TT=2023/6/18^%^209:00:00
            qh_rukou_url_full = urljoin(response.url, school_url_t)
            # 输出请求的URL
            print('school_url_full:{}'.format(qh_rukou_url_full))
            # click to qianghao entrance
            self.headers['Referer'] = response.url
            yield scrapy.Request(url=qh_rukou_url_full, headers=self.headers, callback=self.qh_ru_kou_check) #添加身份证号验证
            #yield scrapy.Request(url=qh_rukou_url_full, headers=self.headers, callback=self.qh_rukou_parse)
            break

    def qh_ru_kou_check(self, response):
        with open('qh_ru_kou_check.html', 'w') as f:
            f.write(response.text)
            # 提取formdata信息
        event_target = response.xpath('//input[@id="__EVENTTARGET"]/@value')
        event_target_str = event_target.extract()[0] if len(event_target) > 0 else ''
        event_argument = response.xpath('//input[@id="__EVENTARGUMENT"]/@value')
        event_argument_str = event_argument.extract()[0] if len(event_argument) > 0 else ''
        view_state = response.xpath('//input[@id="__VIEWSTATE"]/@value')
        view_state_str = view_state.extract()[0] if len(view_state) > 0 else ''
        event_validation = response.xpath('//input[@id="__EVENTVALIDATION"]/@value')
        event_validation_str = event_validation.extract()[0] if len(event_validation) > 0 else ''
        view_state_generator = response.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')
        view_state_generator_str = view_state_generator.extract()[0] if len(view_state_generator) > 0 else ''
        self.form_data['ScriptManager1'] = 'UpdatePanelAA|LinkButtonSFZH'

        self.form_data['__EVENTTARGET'] = 'LinkButtonSFZH'
        self.form_data['__EVENTARGUMENT'] = event_argument_str
        self.form_data['__VIEWSTATE'] = view_state_str
        self.form_data['__EVENTVALIDATION'] = event_validation_str
        self.form_data['__VIEWSTATEGENERATOR'] = view_state_generator_str
        self.form_data['__LASTFOCUS'] = ''
        self.form_data['TextBox_XM'] = ''
        self.form_data['TextBox_SFZH'] = '500237202005010046'
        self.form_data['TextBox_FJDZ'] = ''
        self.form_data['TextBox_JZDZ'] = ''
        self.form_data['TextBox_JFRXM'] = ''
        self.form_data['TextBox_JFRSFZH'] = ''
        self.form_data['TextBox_TelePhone'] = ''
        self.form_data['__ASYNCPOST'] = 'true'

        self.headers['Referer'] = response.url
        self.headers['X-Requested-With'] = 'XMLHttpRequest'
        self.headers['X-MicrosoftAjax'] = 'Delta=true'
        self.headers['Cache-Control'] = 'no-cache'
        self.headers['Sec-Fetch-Dest'] = 'empty'
        self.headers['Sec-Fetch-Mode'] = 'cors'
        self.headers['Sec-Fetch-Site'] = 'same-origin'
        self.headers['TE'] = 'trailers'
        self.headers['Accept'] = '*/*'
        self.headers['Origin'] = 'https://wsemal.com'
        if self.headers.get('Upgrade-Insecure-Requests') is not None:
            self.headers.pop('Upgrade-Insecure-Requests')

        bodystr = urlencode(self.form_data)
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        self.headers['Content-Length'] = '{}'.format(len(bodystr))

        yield scrapy.Request(url=response.url, method="POST", body=bodystr, headers=self.headers,
                             callback=self.SFZh_check_parse)

    def SFZh_check_parse(self, response):
        with open('SFZh_check_parse.html', 'w') as f:
            f.write(response.text)
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
        self.form_data['TextBox_XM'] = '王秀丽'
        self.form_data['TextBox_SFZH'] = '500237202005010046'
        self.form_data['TextBox_FJDZ'] = '重庆市巫山县高唐街道巫峡路110号4幢4单元1-2'
        self.form_data['TextBox_JZDZ'] = '重庆市巫山县高唐街道巫峡路110号4幢4单元1-2'
        self.form_data['TextBox_JFRXM'] = '王大海'
        self.form_data['TextBox_JFRSFZH'] = '500237198905319744'
        self.form_data['TextBox_TelePhone'] = '13278904979'
        self.form_data['__ASYNCPOST'] = 'true'
        self.form_data['Button1'] = '提交申请' #这行的代码得改

        self.headers['Referer'] = response.url
        self.headers['X-Requested-With'] = 'XMLHttpRequest'
        self.headers['X-MicrosoftAjax'] = 'Delta=true'
        self.headers['Cache-Control'] = 'no-cache'
        self.headers['Sec-Fetch-Dest'] = 'empty'
        self.headers['Sec-Fetch-Mode'] = 'cors'
        self.headers['Sec-Fetch-Site'] = 'same-origin'
        self.headers['TE'] = 'trailers'
        self.headers['Accept'] = '*/*'
        self.headers['Origin'] = 'https://wsemal.com'
        if self.headers.get('Upgrade-Insecure-Requests') is not None:
            self.headers.pop('Upgrade-Insecure-Requests')

        bodystr = urlencode(self.form_data)
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        self.headers['Content-Length'] = '{}'.format(len(bodystr))

        yield scrapy.Request(url=response.url, method="POST", body=bodystr, headers=self.headers,
                             callback=self.submit_info)

    def submit_info(self, response):
        with open('submit_info.html', 'w') as f:
            f.write(response.text)
        print(response.text)




