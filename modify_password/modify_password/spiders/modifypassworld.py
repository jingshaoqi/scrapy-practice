import time
import json
import re
from urllib.parse import urlencode
import scrapy
from urllib.parse import urljoin
import ddddocr


class ModifypassworldSpider(scrapy.Spider):
    name = "modifypassworld"
    allowed_domains = ["www.baidu.com"]
    start_urls = ["https://wsemal.com/CZBM/JW/JW_iframe.aspx?FS=CC"]

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
                 '__EVENTVALIDATION': '',
                 '__LASTFOCUS': '',
                 }
    cur_user_pwd = ''  # 当前用户的密码
    user_dll_url = ''

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
        # find mainframe
        main_frm = response.xpath('//tr/td/div/iframe[@id="mainFrame"]/@src')
        if main_frm is None:
            return
        main_frm_url = main_frm.extract()[0]
        # https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        main_frm_url_full = urljoin(response.url, main_frm_url)
        print(main_frm_url_full)
        # 获取cookie
        if response.headers.get('Set-Cookie'):
            ckie = response.headers['Set-Cookie']
            fdf = str(ckie).split(';')
            # 只需要第一个
            for i in fdf:
                if i.find('SessionId') >= 0:
                    self.headers['Cookie'] = i  # ASP.NET_SessionId=3rg5mw45ldudcbmsvfnyayj0
                    break
        self.headers['Referer'] = response.url  # https://wsemal.com/CZBM/JW/JW_iframe.aspx?FS=CC
        self.headers['Sec-Fetch-Dest'] = 'iframe'
        self.headers['Sec-Fetch-Mode'] = 'navigate'
        self.headers['Sec-Fetch-Site'] = 'same-origin'
        self.headers['TE'] = 'trailers'
        # self.headers['Sec-Fetch-User'] = '?1'
        self.user_dll_url = main_frm_url_full  # https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        if self.headers.get('Content-Type') is not None:
            self.headers.pop('Content-Type')
        if self.headers.get('Content-Length') is not None:
            self.headers.pop('Content-Length')
        if self.headers.get('X-MicrosoftAjax') is not None:
            self.headers.pop('X-MicrosoftAjax')
        if self.headers.get('Origin') is not None:
            self.headers.pop('Origin')
        if self.headers.get('Sec-Fetch-User') is not None:
            self.headers.pop('Sec-Fetch-User')
        yield scrapy.Request(url=main_frm_url_full, callback=self.main_parse, headers=self.headers, dont_filter=True)

    def main_parse(self, response):
        with open('JW_UserDL.aspx.html', 'w') as f:
            f.write(response.text)
        # 现在来获取验证码的图片
        yzm_url = response.xpath('//table/tr/td/input[@id="ImageButtonYZM"]/@src')
        if yzm_url is None:
            return
        # https://wsemal.com/CZBM/public/checkcode.aspx
        yzm_url_t = yzm_url.extract()[0]
        self.yzm_url_full = urljoin(response.url, yzm_url_t)
        # https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        self.headers['Referer'] = self.user_dll_url
        self.headers['Accept'] = 'image/avif,image/webp,*/*'
        self.headers['Sec-Fetch-Dest'] = 'image'
        self.headers['Sec-Fetch-Mode'] = 'no-cors'
        self.headers['Sec-Fetch-Site'] = 'same-origin'
        self.headers['TE'] = 'trailers'
        if self.headers.get('Sec-Fetch-User') is not None:
            self.headers.pop('Sec-Fetch-User')
        # 提取formdata信息
        event_target = response.xpath('//div/input[@id="__EVENTTARGET"]/@value')
        event_target_str = event_target.extract()[0] if len(event_target) > 0 else ''
        event_argument = response.xpath('//div/input[@id="__EVENTARGUMENT"]/@value')
        event_argument_str = event_argument.extract()[0] if len(event_argument) > 0 else ''
        view_state = response.xpath('//div/input[@id="__VIEWSTATE"]/@value')
        view_state_str = view_state.extract()[0] if len(view_state) > 0 else ''
        event_validation = response.xpath('//div/input[@id="__EVENTVALIDATION"]/@value')
        event_validation_str = event_validation.extract()[0] if len(event_validation) > 0 else ''
        view_state_generator = response.xpath('//div/input[@id="__VIEWSTATEGENERATOR"]/@value')
        view_state_generator_str = view_state_generator.extract()[0] if len(view_state_generator) > 0 else ''
        self.form_data['__EVENTTARGET'] = event_target_str
        self.form_data['__EVENTARGUMENT'] = event_argument_str
        self.form_data['__VIEWSTATE'] = view_state_str
        self.form_data['__EVENTVALIDATION'] = event_validation_str
        self.form_data['__VIEWSTATEGENERATOR'] = view_state_generator_str
        yield scrapy.Request(url=self.yzm_url_full, callback=self.yzm_parse, headers=self.headers, dont_filter=True)

    # 解析验证码后按登录按钮
    def yzm_parse(self, response):
        # 保存验证码图片
        with open('yan_zheng_ma.jpg', 'wb') as f:
            f.write(response.body)
        # 利用 ddddocr识别验证码
        ocr = ddddocr.DdddOcr()
        res = ocr.classification(response.body)
        print('验证码为:{}'.format(res))
        self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        self.headers['Origin'] = 'https://wsemal.com'
        self.headers['Upgrade-Insecure-Requests'] = '1'
        self.headers['Sec-Fetch-Dest'] = 'iframe'
        self.headers['Sec-Fetch-Mode'] = 'navigate'
        self.headers['Sec-Fetch-Site'] = 'same-origin'
        self.headers['TE'] = 'trailers'
        self.headers['Sec-Fetch-User'] = '?1'

        # 现在使用用户名，密码，验证码登录
        self.form_data['L_username'] = '500237201011301419'
        self.form_data['L_password'] = 'a201025Q'
        self.form_data['L_YZM'] = res
        self.form_data['Button1'] = '登录'
        bodystr = urlencode(self.form_data, encoding='utf-8')
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
        self.headers['Content-Length'] = '{}'.format(len(bodystr))
        # 准备好了数据 按 登录 按钮
        yield scrapy.Request(url=self.user_dll_url, method='POST', body=bodystr,
                             callback=self.login_parse, headers=self.headers, dont_filter=True)

    # 登录结果分析，登录结果中添加了 cookie XSQHUserName
    def login_parse(self, response):
        with open('login_res.html', 'w') as f:
            f.write(response.text)
        # 获取cookie XSQHUserName的值
        if response.headers.get('Set-Cookie') is None:
            print('login fail')
            # 再次请求一个验证码
            print('try to get another yanzhengma')
            self.headers['Referer'] = self.user_dll_url
            self.headers['Accept'] = 'image/avif,image/webp,*/*'
            self.headers['Sec-Fetch-Dest'] = 'image'
            self.headers['Sec-Fetch-Mode'] = 'no-cors'
            self.headers['Sec-Fetch-Site'] = 'same-origin'
            self.headers['TE'] = 'trailers'
            # 请求头中删除不需要的
            if self.headers.get('Content-Type') is not None:
                self.headers.pop('Content-Type')
            if self.headers.get('Content-Length') is not None:
                self.headers.pop('Content-Length')
            if self.headers.get('Sec-Fetch-User') is not None:
                self.headers.pop('Sec-Fetch-User')
            if self.headers.get('Origin') is not None:
                self.headers.pop('Origin')
            if self.headers.get('Upgrade-Insecure-Requests') is not None:
                self.headers.pop('Upgrade-Insecure-Requests')
            if len(self.headers) != 12:
                print('yzm rerequest possible headers is not correct, length of headers is:{}'.format(len(self.headers)))
            yield scrapy.Request(url=self.yzm_url_full, callback=self.yzm_parse, headers=self.headers,
                                     dont_filter=True)
            return
        print('login success')
        ckie = response.headers['Set-Cookie']
        if str(ckie).find('XSQHUserName') < 0:
            print('login fail too.')
            return
        fdf = str(ckie).split(';')
        # 只需要有用的值
        for i in fdf:
            if i.find('XSQHUserName') >= 0:
                self.headers['Cookie'] += ';' + i  # ASP.NET_SessionId=3rg5mw45ldudcbmsvfnyayj0
                break
        self.headers['Referer'] = response.url
        top_frame_url = urljoin(response.url, '../JW/JW_Top.aspx')
        if self.headers.get('Content-Type') is not None:
            self.headers.pop('Content-Type')
        if self.headers.get('Content-Length') is not None:
            self.headers.pop('Content-Length')
        yield scrapy.Request(url=top_frame_url, callback=self.top_frame_parse, headers=self.headers, dont_filter=True)

    def top_frame_parse(self, response):
        # 再响应中找到修改密码的链接
        mpsd = response.xpath('//td/table/tr/td/a[contains(text(),"修改密码")]/@href')
        if mpsd is None:
            return
        mpsd_url = mpsd.get()
        mpsd_url_full = urljoin(response.url, mpsd_url)
        yield scrapy.Request(url=mpsd_url_full, callback=self.post_md_parse, headers=self.headers, dont_filter=True)

    def post_md_parse(self, response):
        print('enter post_md_parse')
        self.form_data['ScriptManager1'] = 'ScriptManager1|Button1'
        self.form_data['__EVENTTARGET'] = ''
        self.form_data['__LASTFOCUS'] = ''
        self.form_data['__ASYNCPOST'] = 'true'
        self.form_data['Button1'] = '确认'
        self.form_data['Hselect'] = ''
        event_argument = response.xpath('//div/input[@id="__EVENTARGUMENT"]/@value')
        event_argument_str = event_argument.extract()[0] if len(event_argument) > 0 else ''
        view_state = response.xpath('//div/input[@id="__VIEWSTATE"]/@value')
        view_state_str = view_state.extract()[0] if len(view_state) > 0 else ''
        event_validation = response.xpath('//div/input[@id="__EVENTVALIDATION"]/@value')
        event_validation_str = event_validation.extract()[0] if len(event_validation) > 0 else ''
        view_state_generator = response.xpath('//div/input[@id="__VIEWSTATEGENERATOR"]/@value')
        view_state_generator_str = view_state_generator.extract()[0] if len(view_state_generator) > 0 else ''

        self.form_data['__EVENTARGUMENT'] = event_argument_str
        self.form_data['__VIEWSTATE'] = view_state_str
        self.form_data['__EVENTVALIDATION'] = event_validation_str
        self.form_data['__VIEWSTATEGENERATOR'] = view_state_generator_str
        self.form_data['L_password1'] = 'a201025Q'
        self.form_data['L_password2'] = 'a201025Q'
        self.form_data['L_password3'] = 'a201025Q'
        self.form_data['TextBox_PWD'] = '17783631632'
        bodystr = urlencode(self.form_data, encoding='utf-8')
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
        self.headers['Content-Length'] = '{}'.format(len(bodystr))
        # yield scrapy.Request(url=action_url_full, method='POST', body=bodystr, callback=self.post_zsbm1_parse,
        # headers=self.headers, dont_filter=True)
        print('exit post_md_parse')
        yield scrapy.Request(url=response.url, method='POST', body=bodystr, callback=self.que_ren_parse,
                             headers=self.headers, dont_filter=True)
    def que_ren_parse(self, response):
        with open('que_ren.txt', 'w') as f:
            f.write(response.text)
        print('finish')