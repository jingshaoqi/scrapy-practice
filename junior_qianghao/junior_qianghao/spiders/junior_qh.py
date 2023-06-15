import json

import scrapy
from urllib.parse import urljoin
import ddddocr

class JuniorQhSpider(scrapy.Spider):
    name = "junior_qh"
    allowed_domains = ["www.baidu.com"]
    start_urls = ["https://wsemal.com/CZBM/JW/JW_iframe.aspx?FS=CC"]
    user_dll_url = ''

    def parse(self, response):
        with open('junior.html', 'w') as f:
            f.write(response.text)
        #print(response.text)
        # find mainframe
        main_frm = response.xpath('//tr/td/div/iframe[@id="mainFrame"]/@src')
        if main_frm is None:
            return
        main_frm_url = main_frm.extract()[0]
        main_frm_url_full = urljoin(response.url, main_frm_url)
        print(main_frm_url_full)

        #获取cookie
        ckie = response.headers['Set-Cookie']
        fdf = str(ckie).split(';')
        # 只需要第一个
        str_cookie = fdf[0] + ';ZLPJUserName=; ZLPJPassWord=; FDZSUserName=; FDZSPassWord=; XQZSUserName=; XQPassWord=; PPUserName=; PPPassWord=; XSQHUserName=; XSQHPassWord='
        headers = {'authority': 'wsemal.com',
                   'referer': response.url,
                   'cookie': str_cookie,
                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.43'}

        #yield scrapy.Request(url=main_frm_url_full, callback=self.main_parse, headers=headers, dont_filter=True)
        self.user_dll_url = main_frm_url_full
        yield scrapy.Request(url=main_frm_url_full, callback=self.main_parse, dont_filter=True)

    def main_parse(self, response):
        with open('junior_main.html', 'w') as f:
            f.write(response.text)
        #print(response.text)
        # 现在来获取验证码的图片
        yzm_url = response.xpath('//table/tr/td/input[@id="ImageButtonYZM"]/@src')
        if yzm_url is None:
            return
        yzm_url_t = yzm_url.extract()[0]
        yzm_url_full = urljoin(response.url, yzm_url_t)
        yield scrapy.Request(url=yzm_url_full, callback=self.yzm_parse, dont_filter=True)

    def yzm_parse(self, response):
        # 保存验证码图片
        with open('yan_zheng_ma.jpg', 'wb') as f:
            f.write(response.body)
        # 利用 ddddocr识别验证码
        ocr = ddddocr.DdddOcr()
        res = ocr.classification(response.body)
        print(res)

        #现在使用用户名，密码，验证码登录
        fm_data={'L_username':'500237201011301419',
                 'L_password':'a201025Q',
                 'L_YZM':res,
                 'Button1':'登录'}
        yield scrapy.Request(url=self.user_dll_url, method='POST', body=json.dumps(fm_data), callback=self.login_parse,
                             dont_filter=True)

    def login_parse(self, response):
        with open('login_res.html', 'w') as f:
            f.write(response.text)
        print(response.text)


