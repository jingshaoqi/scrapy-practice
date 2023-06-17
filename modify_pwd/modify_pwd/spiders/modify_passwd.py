import re
import scrapy
from urllib.parse import urljoin
from urllib.parse import urlencode
import ddddocr

class ModifyPasswdSpider(scrapy.Spider):
    name = "modify_passwd"
    allowed_domains = ["www.baidu.com"]
    main_url = "https://wsemal.com/CZBM/JW/JW_iframe.aspx?FS=CC"
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
                 '__LASTFOCUS':'',
                 }
    cur_user_pwd = '' # 当前用户的密码
    user_dll_url = ''

    def parse(self, response):
        with open('JW_iframe.aspx.html', 'w') as f:
            f.write(response.text)
        # find topframe
        top_frm = response.xpath('//tr/td/table/tr/td/iframe[@name="topFrame"]/@src')
        if top_frm is None:
            return
        top_frm_url = top_frm.extract()[0]
        # https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        top_frm_url_full = urljoin(response.url, top_frm_url)
        print(top_frm_url_full)

        # 获取cookie
        ckie = response.headers['Set-Cookie']
        fdf = str(ckie).split(';')

        for i in fdf:
            if i.find('SessionId') >= 0:
                self.headers['Cookie'] = i  # ASP.NET_SessionId=3rg5mw45ldudcbmsvfnyayj0
                break
        self.headers['Referer'] = response.url  # https://wsemal.com/CZBM/JW/JW_iframe.aspx?FS=CC

        self.headers['Referer'] = response.url  # https://wsemal.com/CZBM/JW/JW_iframe.aspx?FS=CC
        self.headers['Sec-Fetch-Dest'] = 'iframe'
        self.headers['Sec-Fetch-Mode'] = 'navigate'
        self.headers['Sec-Fetch-Site'] = 'same-origin'
        self.headers['TE'] = 'trailers'
        if self.headers.get('Sec-Fetch-User') is not None:
            self.headers.pop('Sec-Fetch-User')
        self.user_dll_url = top_frm_url_full  # https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        yield scrapy.Request(url=top_frm_url_full, callback=self.top_parse, headers=self.headers, dont_filter=True)

    def top_parse(self, response):
        with open('top_frame.aspx.html', 'w') as f:
            f.write(response.text)
        #找到找回密码
        ssp = response.xpath('//table/tr/td/table/tr/td/a[contains(text(), "找回密码")]/@href')
        if ssp is None:
            return
        ssp_url = ssp.extract()[0]
        ssp_url_full = urljoin(response.url, ssp_url)
        yield scrapy.Request(url=ssp_url_full, callback=self.SSP_parse, headers=self.headers, dont_filter=True)

        # 在浏览器中实际上还有更新 身份证，姓名和电话号码的步骤，我们这里直接按确认按钮
    def SSP_parse(self, response):
        with open('ssp_parse.aspx.html', 'w') as f:
            f.write(response.text)

        self.form_data['ScriptManager1'] = 'UpdatePanel1|Button1'
        self.form_data['Hselcet'] = ''

        # 提取formdata信息
        event_target = response.xpath('//div/input[@id="__EVENTTARGET"]/@value')
        self.form_data['__EVENTTARGET'] = ''

        event_argument = response.xpath('//div/input[@id="__EVENTARGUMENT"]/@value')
        self.form_data['__EVENTARGUMENT'] = event_argument.extract()[0] if len(event_argument) > 0 else ''
        view_state = response.xpath('//div/input[@id="__VIEWSTATE"]/@value')
        self.form_data['__VIEWSTATE']  = view_state.extract()[0] if len(view_state) > 0 else ''
        event_validation = response.xpath('//div/input[@id="__EVENTVALIDATION"]/@value')
        self.form_data['__EVENTVALIDATION']  = event_validation.extract()[0] if len(event_validation) > 0 else ''
        view_state_generator = response.xpath('//div/input[@id="__VIEWSTATEGENERATOR"]/@value')
        self.form_data['__VIEWSTATEGENERATOR'] = view_state_generator.extract()[0] if len(view_state_generator) > 0 else ''
        last_focus = response.xpath('//div/input[@id="__LASTFOCUS"]/@value')
        self.form_data['__LASTFOCUS'] = last_focus.extract()[0] if len(last_focus) > 0 else ''

        #填充数据
        self.form_data['TextBox_SFZH'] = '500237201011301419'
        self.form_data['TextBox_XM'] = '彭鑫'
        self.form_data['TextBox_T1'] = '17783631632'
        self.form_data['__ASYNCPOST'] = 'true'
        self.form_data['Button1'] = '确认'

        self.headers['Sec-Fetch-Dest'] = 'empty'
        self.headers['Sec-Fetch-Mode'] = 'cors'
        self.headers['Sec-Fetch-Site'] = 'same-origin'
        self.headers['TE'] = 'trailers'
        self.headers['X-MicrosoftAjax'] = 'Delta=true'
        self.headers['Origin'] = 'https://wsemal.com'
        self.headers['Referer'] = response.url
        bodystr = urlencode(self.form_data)
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        self.headers['Content-Length'] = '{}'.format(len(bodystr))
        yield scrapy.Request(url=response.url, method='POST', body=bodystr, callback=self.confirm_parse, headers=self.headers, dont_filter=True)

    def confirm_parse(self, response):
        with open('confirm_parse.aspx.html', 'w') as f:
            f.write(response.text)
        # 解析出密码
        pwd = response.xpath('//tr/td/span[@id="LabelTS"]')
        if pwd is None:
            print('not found password')
            return
        pwd_t = pwd.get()
        pwd_real = re.findall(r'密码为【(.+?)】', response.text)
        if len(pwd_real) <= 0:
            return
        print('real password is :{}'.format(pwd_real[0]))
        self.cur_user_pwd = pwd_real[0]

        self.headers['Sec-Fetch-Dest'] = 'document'
        self.headers['Sec-Fetch-Mode'] = 'navigate'
        self.headers['Sec-Fetch-Site'] = 'none'
        self.headers['TE'] = 'trailers'
        if self.headers.get('Sec-Fetch-User') is not None:
            self.headers.pop('Sec-Fetch-User')
        if self.headers.get('Referer') is not None:
            self.headers.pop('Referer')

        yield scrapy.Request(url=self.main_url, callback=self.parse_main_login, headers=self.headers, dont_filter=True)

        #现在来调用修改密码的接口
    def parse_main_login(self, response):
        with open('JW_iframe.aspx.html', 'w') as f:
            f.write(response.text)
        #print(response.text)
        # find mainframe
        main_frm = response.xpath('//tr/td/div/iframe[@id="mainFrame"]/@src')
        if main_frm is None:
            return
        main_frm_url = main_frm.extract()[0]
        # https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        main_frm_url_full = urljoin(response.url, main_frm_url)
        print(main_frm_url_full)

        #获取cookie
        if response.headers.get('Set-Cookie'):
            ckie = response.headers['Set-Cookie']
            fdf = str(ckie).split(';')
            # 只需要第一个
            for i in fdf:
                if i.find('SessionId') >= 0:
                    self.headers['Cookie'] = i #ASP.NET_SessionId=3rg5mw45ldudcbmsvfnyayj0
                    break
        self.headers['Referer'] = response.url # https://wsemal.com/CZBM/JW/JW_iframe.aspx?FS=CC
        self.headers['Sec-Fetch-Dest'] = 'iframe'
        self.headers['Sec-Fetch-Mode'] = 'navigate'
        self.headers['Sec-Fetch-Site'] = 'same-origin'
        self.headers['TE'] = 'trailers'
        #self.headers['Sec-Fetch-User'] = '?1'
        self.user_dll_url = main_frm_url_full #https://wsemal.com/CZBM/JW/JW_UserDL.aspx
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

        #现在使用用户名，密码，验证码登录
        self.form_data['L_username'] = '500237201011301419'
        self.form_data['L_password'] = 'a201025Q'
        self.form_data['L_YZM'] = res
        self.form_data['Button1'] = '登录'
        bodystr = urlencode(self.form_data)
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        self.headers['Content-Length'] = '{}'.format(len(bodystr))
        #准备好了数据 按 登录 按钮
        yield scrapy.Request(url=self.user_dll_url, method='POST', body=bodystr,
                             callback=self.login_parse, headers=self.headers, dont_filter=True)
    #登录结果分析，登录结果中添加了 cookie XSQHUserName
    def login_parse(self, response):
        with open('login_res.html', 'w') as f:
            f.write(response.text)
        # 获取cookie XSQHUserName的值
        if response.headers.get('Set-Cookie') is None:
            print('login fail')