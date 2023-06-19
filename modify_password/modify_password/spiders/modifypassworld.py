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
    form_data = {}
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

        for url in self.start_urls:
            yield scrapy.Request(url=url,  callback=self.parse, dont_filter=True)

    def parse(self, response):
        # find mainframe
        main_frm = response.xpath('//tr/td/div/iframe[@id="mainFrame"]/@src')
        if main_frm is None:
            return
        main_frm_url = main_frm.extract()[0]
        # https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        main_frm_url_full = urljoin(response.url, main_frm_url)
        print(main_frm_url_full)
        headers = {}
        headers['Referer'] = response.url  # https://wsemal.com/CZBM/JW/JW_iframe.aspx?FS=CC
        self.user_dll_url = main_frm_url_full  # https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        yield scrapy.Request(url=main_frm_url_full, callback=self.main_parse,  dont_filter=True)

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

        # 提取formdata信息
        event_target = response.xpath('//input[@id="__EVENTTARGET"]/@value')
        self.form_data['__EVENTTARGET'] = event_target.extract()[0] if len(event_target) > 0 else ''
        event_argument = response.xpath('//input[@id="__EVENTARGUMENT"]/@value')
        self.form_data['__EVENTARGUMENT'] = event_argument.extract()[0] if len(event_argument) > 0 else ''
        view_state = response.xpath('//input[@id="__VIEWSTATE"]/@value')
        self.form_data['__VIEWSTATE'] = view_state.extract()[0] if len(view_state) > 0 else ''
        event_validation = response.xpath('//input[@id="__EVENTVALIDATION"]/@value')
        self.form_data['__EVENTVALIDATION'] = event_validation.extract()[0] if len(event_validation) > 0 else ''
        view_state_generator = response.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')
        self.form_data['__VIEWSTATEGENERATOR'] = view_state_generator.extract()[0] if len(view_state_generator) > 0 else ''
        yield scrapy.Request(url=self.yzm_url_full, callback=self.yzm_parse, dont_filter=True)

    # 解析验证码后按登录按钮
    def yzm_parse(self, response):
        # 保存验证码图片
        with open('yan_zheng_ma.jpg', 'wb') as f:
            f.write(response.body)
        # 利用 ddddocr识别验证码
        ocr = ddddocr.DdddOcr()
        res = ocr.classification(response.body)
        print('验证码为:{}'.format(res))

        # 现在使用用户名，密码，验证码登录
        self.form_data['L_username'] = '500237201011301419'
        self.form_data['L_password'] = 'a201025Q'
        self.form_data['L_YZM'] = res
        self.form_data['Button1'] = '登录'
        bodystr = urlencode(self.form_data, encoding='utf-8')
        headers = {}
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
        headers['Content-Length'] = '{}'.format(len(bodystr))
        # 准备好了数据 按 登录 按钮
        yield scrapy.Request(url=self.user_dll_url, method='POST', body=bodystr,
                             callback=self.login_parse, headers=headers, dont_filter=True)

    # 登录结果分析，登录结果中添加了 cookie XSQHUserName
    def login_parse(self, response):
        with open('login_res.html', 'w') as f:
            f.write(response.text)
        # 获取cookie XSQHUserName的值
        if response.headers.get('Set-Cookie') is None:
            print('login fail')
            # 再次请求一个验证码
            print('try to get another yanzhengma')
            yield scrapy.Request(url=self.yzm_url_full, callback=self.yzm_parse, dont_filter=True)
            return
        print('login success')
        top_frame_url = urljoin(response.url, '../JW/JW_Top.aspx')
        yield scrapy.Request(url=top_frame_url, callback=self.top_frame_parse, dont_filter=True)

    def top_frame_parse(self, response):
        # 再响应中找到修改密码的链接
        mpsd = response.xpath('//td/table/tr/td/a[contains(text(),"修改密码")]/@href')
        if mpsd is None:
            return
        mpsd_url = mpsd.get()
        mpsd_url_full = urljoin(response.url, mpsd_url)
        yield scrapy.Request(url=mpsd_url_full, callback=self.post_md_parse,  dont_filter=True)

    def post_md_parse(self, response):
        print('enter post_md_parse')
        self.form_data['ScriptManager1'] = 'ScriptManager1|Button1'
        self.form_data['__EVENTTARGET'] = ''
        self.form_data['__LASTFOCUS'] = ''
        self.form_data['__ASYNCPOST'] = 'true'
        self.form_data['Button1'] = '确认'
        self.form_data['Hselect'] = ''
        event_argument = response.xpath('//input[@id="__EVENTARGUMENT"]/@value')
        self.form_data['__EVENTARGUMENT'] = event_argument.extract()[0] if len(event_argument) > 0 else ''
        view_state = response.xpath('//input[@id="__VIEWSTATE"]/@value')
        self.form_data['__VIEWSTATE'] = view_state.extract()[0] if len(view_state) > 0 else ''
        event_validation = response.xpath('//input[@id="__EVENTVALIDATION"]/@value')
        self.form_data['__EVENTVALIDATION'] = event_validation.extract()[0] if len(event_validation) > 0 else ''
        view_state_generator = response.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')
        self.form_data['__VIEWSTATEGENERATOR'] = view_state_generator.extract()[0] if len(view_state_generator) > 0 else ''

        self.form_data['L_password1'] = 'a201025Q'
        self.form_data['L_password2'] = 'a201025Q'
        self.form_data['L_password3'] = 'a201025Q'
        self.form_data['TextBox_PWD'] = '17783631632'
        bodystr = urlencode(self.form_data, encoding='utf-8')
        headers = {}
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
        headers['Content-Length'] = '{}'.format(len(bodystr))
        print('exit post_md_parse')
        yield scrapy.Request(url=response.url, method='POST', body=bodystr, callback=self.que_ren_parse,
                             headers=headers, dont_filter=True)
    def que_ren_parse(self, response):
        with open('que_ren.txt', 'w') as f:
            f.write(response.text)
        print('finish')