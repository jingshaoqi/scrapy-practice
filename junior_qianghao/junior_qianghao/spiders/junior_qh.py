import time
import json
import re
from urllib.parse import urlencode
import scrapy
from urllib.parse import urljoin
import ddddocr

class JuniorQhSpider(scrapy.Spider):
    name = "junior_qh"
    allowed_domains = ["www.baidu.com"]
    start_urls = ["https://wsemal.com/CZBM/JW/JW_iframe.aspx?FS=CC"]
    user_dll_url = ''
    headers = {'Referer': 'https://wsemal.com/CZBM/',
               'Host':'wsemal.com',
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
        desttime = '2023-6-16 9:00:00'
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
        ckie = response.headers['Set-Cookie']
        fdf = str(ckie).split(';')
        # 只需要第一个
        #str_cookie = fdf[0] + ';ZLPJUserName=; ZLPJPassWord=; FDZSUserName=; FDZSPassWord=; XQZSUserName=; XQPassWord=; PPUserName=; PPPassWord=; XSQHUserName=; XSQHPassWord='
        for i in fdf:
            if i.find('SessionId') >= 0:
                self.headers['Cookie'] = i #ASP.NET_SessionId=3rg5mw45ldudcbmsvfnyayj0
                break
        self.headers['Referer'] = response.url # https://wsemal.com/CZBM/JW/JW_iframe.aspx?FS=CC
        self.headers['Sec-Fetch-Dest'] = 'iframe'
        self.headers['Sec-Fetch-Mode'] = 'navigate'
        self.headers['Sec-Fetch-Site'] = 'same-origin'
        self.headers['TE'] = 'trailers'
        if self.headers.get('Sec-Fetch-User') is not None:
            self.headers.pop('Sec-Fetch-User')
        #yield scrapy.Request(url=main_frm_url_full, callback=self.main_parse, headers=headers, dont_filter=True)
        self.user_dll_url = main_frm_url_full #https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        yield scrapy.Request(url=main_frm_url_full, callback=self.main_parse, headers=self.headers, dont_filter=True)

    def main_parse(self, response):
        with open('JW_UserDL.aspx.html', 'w') as f:
            f.write(response.text)
        #print(response.text)
        # 现在来获取验证码的图片
        yzm_url = response.xpath('//table/tr/td/input[@id="ImageButtonYZM"]/@src')
        if yzm_url is None:
            return
        # https://wsemal.com/CZBM/public/checkcode.aspx
        yzm_url_t = yzm_url.extract()[0]
        yzm_url_full = urljoin(response.url, yzm_url_t)
        # https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        self.headers['Referer'] = response.url
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
        yield scrapy.Request(url=yzm_url_full, callback=self.yzm_parse, headers=self.headers, dont_filter=True)

    # 解析验证码后按登录按钮
    def yzm_parse(self, response):
        # 保存验证码图片
        with open('yan_zheng_ma.jpg', 'wb') as f:
            f.write(response.body)
        # 利用 ddddocr识别验证码
        ocr = ddddocr.DdddOcr()
        res = ocr.classification(response.body)
        print(res)

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
        yield scrapy.Request(url=self.user_dll_url, method='POST', body=bodystr,
                             callback=self.login_parse,headers=self.headers, dont_filter=True)
    #登录结果分析，登录结果中添加了 cookie XSQHUserName
    def login_parse(self, response):
        with open('login_res.html', 'w') as f:
            f.write(response.text)
        #print(response.text)
        # 获取cookie XSQHUserName的值
        if response.headers.get('Set-Cookie') is None:
            print('login fail')
            #再次请求一个验证码
            print('try to get another yanzhengma')
            self.main_parse(response)
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
        # https://wsemal.com/CZBM/JW/JW_ZSBM.aspx
        zsbm_url = urljoin(response.url, '../JW/JW_ZSBM.aspx')
        print('请求下一个网页：{}'.format(zsbm_url))
        if self.headers.get('Origin') is not None:
            self.headers.pop('Origin')
        # 请求头中删除不需要的
        if self.headers.get('Content-Type') is not None:
            self.headers.pop('Content-Type')
        if self.headers.get('Content-Length') is not None:
            self.headers.pop('Content-Length')
        if self.headers.get('Sec-Fetch-User') is not None:
            self.headers.pop('Sec-Fetch-User')
        yield scrapy.Request(url=zsbm_url, method='GET', callback=self.ZSBM_parse, headers=self.headers,
                             dont_filter=True)

    def ZSBM_parse(self, response):
        with open('JW_ZSBM.aspx.html', 'w') as f:
            f.write(response.text)
        # https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        self.headers['Referer'] = response.url
        #再进入 https://wsemal.com/CZBM/JW/JW_XSBMXZ1.aspx
        # 它的参数需要解析出来才行
        spt = response.xpath('//script/text()')
        if spt is None:
            return
        spt_t = spt.extract()[0]
        str_all = re.findall(r"href=\'(.+?)\';", spt_t)
        if str_all is None:
            return
        xsbmxz1_url = urljoin(response.url, str_all[0])
        print('请求下一个网页：{}'.format(xsbmxz1_url))
        yield scrapy.Request(url=xsbmxz1_url, method='GET', callback=self.XSBMXZ1_parse, headers=self.headers,
                             dont_filter=True)


    def XSBMXZ1_parse(self, response):
        with open('JW_XSBMXZ1.aspx.html', 'w') as f:
            f.write(response.text)
        # https://wsemal.com/CZBM/JW/JW_XSBMXZ1.aspx
        self.headers['Referer'] = response.url
        # https://wsemal.com/CZBM/JW/JW_ZSBM.aspx?FS=YES
        next_url = urljoin(response.url, '../JW/JW_ZSBM.aspx?FS=YES')
        self.headers['Sec-Fetch-User'] = '?1'
        return #当前已经结束
        yield scrapy.Request(url=next_url, method='GET', callback=self.ZSBM_FS_YES_parse, headers=self.headers,
                             dont_filter=True)
    def ZSBM_FS_YES_parse(self, response):
        with open('JW_ZSBM_FS_YES.aspx.html', 'w') as f:
            f.write(response.text)
        with open('JW_ZSBM_FS_YES.body.html', 'w') as f:
            f.write(response.body)