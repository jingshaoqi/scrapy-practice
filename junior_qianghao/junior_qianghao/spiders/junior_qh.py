import time
from datetime import datetime
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
    school_code = ''

    form_data = {'__EVENTTARGET': '',
                 '__EVENTARGUMENT': '',
                 '__VIEWSTATE': '',
                 '__VIEWSTATEGENERATOR': '',
                 '__EVENTVALIDATION': ''
                 }
    zsbm_url = ''
    zsbm_headers={}
    yzm_url_full='' #保存验证码的url
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

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
        self.user_dll_url = main_frm_url_full #https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        yield scrapy.Request(url=main_frm_url_full, callback=self.main_parse, dont_filter=True)

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
        headers = {}
        headers['Referer'] = self.user_dll_url
        headers['Accept'] = 'image/avif,image/webp,*/*'

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
        self.form_data['__EVENTTARGET'] = event_target_str
        self.form_data['__EVENTARGUMENT'] = event_argument_str
        self.form_data['__VIEWSTATE'] = view_state_str
        self.form_data['__EVENTVALIDATION'] = event_validation_str
        self.form_data['__VIEWSTATEGENERATOR'] = view_state_generator_str
        yield scrapy.Request(url=self.yzm_url_full, callback=self.yzm_parse, headers=headers, dont_filter=True)

    # 解析验证码后按登录按钮
    def yzm_parse(self, response):
        # 保存验证码图片
        with open('yan_zheng_ma.jpg', 'wb') as f:
            f.write(response.body)
        # 利用 ddddocr识别验证码
        ocr = ddddocr.DdddOcr()
        res = ocr.classification(response.body)
        print('验证码为:{}'.format(res))
        headers = {}
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        headers['Origin'] = 'https://wsemal.com'

        #现在使用用户名，密码，验证码登录
        self.form_data['L_username'] = '500237201011301419'
        self.form_data['L_password'] = 'a201025Q'
        self.form_data['L_YZM'] = res
        self.form_data['Button1'] = '登录'
        bodystr = urlencode(self.form_data)
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Content-Length'] = '{}'.format(len(bodystr))

        print('username:{} password:{}'.format(self.form_data['L_username'], self.form_data['L_password']))
        #准备好了数据 按 登录 按钮
        yield scrapy.Request(url=self.user_dll_url, method='POST', body=bodystr,
                             callback=self.login_parse, headers=headers, dont_filter=True)
    #登录结果分析，登录结果中添加了 cookie XSQHUserName
    def login_parse(self, response):
        with open('login_res.html', 'w') as f:
            f.write(response.text)
        # 获取cookie XSQHUserName的值
        if response.headers.get('Set-Cookie') is None:
            print('login fail')
            #再次请求一个验证码
            print('try to get another yanzhengma')
            headers = {}
            headers['Referer'] = self.user_dll_url
            yield scrapy.Request(url=self.yzm_url_full, callback=self.yzm_parse, headers=headers, dont_filter=True)
            return
        print('login success')
        ckie = response.headers['Set-Cookie']
        if str(ckie).find('XSQHUserName') < 0:
            print('login fail too.')
            return
        # https://wsemal.com/CZBM/JW/JW_ZSBM.aspx
        #找到请求的下一个网页
        zsbm = response.xpath('//script[contains(text(), "mainFrame") and contains(text(), "href")]/text()')
        if zsbm is None:
            print('not found zxbm page')
            return
        zsbm_t = zsbm.get()
        zsbm_res = re.findall(r"href=\'(.+?)\';", zsbm_t)
        if len(zsbm_res) <= 0:
            return
        zsbm_ur = zsbm_res[0] # ../JW/JW_ZSBM.aspx
        zsbm_url = urljoin(response.url, zsbm_ur) # 'https://wsemal.com/CZBM/JW/JW_ZSBM.aspx'
        print('请求下一个网页：{}'.format(zsbm_url))
        # 从这个请求开始得到抢号的界面，没有开始的时候是其他界面
        self.zsbm_url = zsbm_url
        self.zsbm_headers = response.request.headers
        # 添加一个等待时间控制
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
        yield scrapy.Request(url=zsbm_url, callback=self.ZSBM_parse, dont_filter=True)

    def ZSBM_parse(self, response):
        with open('JW_ZSBM.aspx.html', 'w') as f:
            f.write(response.text)
        # https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        headers = {}
        headers['Referer'] = response.url
        #再进入 https://wsemal.com/CZBM/JW/JW_XSBMXZ1.aspx
        # 它的参数需要解析出来才行
        spt = response.xpath('//script/text()')
        if spt is None or len(spt) <= 0:
            # 说明还没有到开始抢号的时间，重新进入
            time.sleep(0.3)
            if len(self.headers) != 13:
                print('ZSBM_parse 1possible headers is not correct, length of headers is:{}'.format(len(self.headers)))
            yield scrapy.Request(url=response.url, callback=self.ZSBM_parse, headers=headers, dont_filter=True)
            return
        spt_t = spt.extract()[0]
        if spt_t.find('JW_ZSBM1.aspx') < 0:
            #说明还没有到开始抢号的时间，重新进入
            time.sleep(0.3)
            if len(self.headers) != 13:
                print('ZSBM_parse 2possible headers is not correct, length of headers is:{}'.format(len(self.headers)))
            yield scrapy.Request(url=response.url, callback=self.ZSBM_parse, headers=headers, dont_filter=True)
            return
        str_all = re.findall(r"href=\'(.+?)\';", spt_t)
        if str_all is None:
            return
        #这个是模拟抢号之前的代码
        #xsbmxz1_url = urljoin(response.url, str_all[0])
        #print('请求下一个网页：{}'.format(xsbmxz1_url))
        #yield scrapy.Request(url=xsbmxz1_url, callback=self.XSBMXZ1_parse, headers=self.headers, dont_filter=True)

        zsbm1_url = urljoin(response.url, str_all[0])
        print('请求下一个网页：{}'.format(zsbm1_url))
        yield scrapy.Request(url=zsbm1_url, callback=self.ZSBM1_parse, dont_filter=True)

    def ZSBM1_parse(self, response):
        with open('JW_ZSBM1.aspx.html', 'w') as f:
            f.write(response.text)
        #a判断状态是否在进行中
        zt = response.xpath('//span[@id="Label_ZT"]/text()')
        if zt is None or zt.get().find("进行中") < 0:
            time.sleep(0.5)
            yield scrapy.Request(url=self.zsbm_url, callback=self.ZSBM_parse, dont_filter=True)
            return
        #解析响应中有用的数据

        select_school_name = '巫山二中'
        #判断选择的学校是否已经满了
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
            #再次选择
            select_school_name = '巫峡初中'
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
        # select_school_code = 'A23317' #A23313;A23317;B23301;B23304
        # 先要获取学校名称和代号
        schools = response.xpath('//tr/td/select/option')
        if schools is None or len(schools) <= 0:
            print('not have schools')
            return
        for i in schools:
            school_name = i.xpath('./text()').extract()[0]
            if school_name.find(select_school_name) >= 0:
                self.school_code = i.xpath('./@value').extract()[0]
                break
        if len(self.school_code) <= 0:
            print('not found {} in the list'.format(select_school_name))
            return

        #再要获取下一个请求的url
        action_url = response.xpath('//body/form[@id="form1" and @method="post"]/@action')
        if action_url is None:
            return
        action_url_t = action_url.extract()[0]
        # https://wsemal.com/CZBM/JW/JW_ZSBM1.aspx?TT=2023%2f6%2f17+8%3a30%3a00&PC=%u7b2c%u4e00%u6279%u6b21(A%u8f6e)
        action_url_full = urljoin(response.url, action_url_t)

        # https://wsemal.com/CZBM/JW/JW_ZSBM.aspx
        headers = {}
        headers['Referer'] = response.url
        headers['Accept'] = '*/*'
        headers['Origin'] = 'https://wsemal.com'
        headers['Cache-Control'] = 'no-cache'
        headers['X-MicrosoftAjax'] = 'Delta=true'
        headers['Sec-Fetch-Dest'] = 'empty'
        headers['Sec-Fetch-Mode'] = 'cors'
        headers['Sec-Fetch-Site'] = 'same-origin'
        # 修改请求的数据 在实际的浏览器中测试分两次进行，一次是展开下拉列表，第二次是按提交按钮，
        form_data = {}
        form_data['ScriptManager1'] = 'UpdatePanel3|DropDownListQHXX'
        form_data['__EVENTTARGET'] = 'DropDownListQHXX'
        #self.form_data['ScriptManager1'] = 'UpdatePanel3|ButtonOK'
        #self.form_data['__EVENTTARGET'] = ''
        form_data['__LASTFOCUS'] = ''
        form_data['__ASYNCPOST'] = 'true'
        #self.form_data['ButtonOK'] = '提交申请'
        form_data['DropDownListQHXX'] = self.school_code
        event_argument = response.xpath('//input[@id="__EVENTARGUMENT"]/@value')
        event_argument_str = event_argument.extract()[0] if len(event_argument) > 0 else ''
        view_state = response.xpath('//input[@id="__VIEWSTATE"]/@value')
        view_state_str = view_state.extract()[0] if len(view_state) > 0 else ''
        event_validation = response.xpath('//input[@id="__EVENTVALIDATION"]/@value')
        event_validation_str = event_validation.extract()[0] if len(event_validation) > 0 else ''
        view_state_generator = response.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')
        view_state_generator_str = view_state_generator.extract()[0] if len(view_state_generator) > 0 else ''

        form_data['__EVENTARGUMENT'] = event_argument_str
        form_data['__VIEWSTATE'] = view_state_str
        form_data['__EVENTVALIDATION'] = event_validation_str
        form_data['__VIEWSTATEGENERATOR'] = view_state_generator_str
        bodystr = urlencode(form_data, encoding='utf-8')
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
        headers['Content-Length'] = '{}'.format(len(bodystr))
        if len(self.headers) != 17:
            print('zsbm1 post first possible headers is not correct, length of headers is:{}'.format(len(self.headers)))
        yield scrapy.Request(url=action_url_full, method='POST', body=bodystr, callback=self.post_zsbm1_parse,
                             headers=headers, dont_filter=True)


    def post_zsbm1_parse(self, response):
        with open('post_zsbm1_parse.aspx.html', 'w') as f:
            f.write(response.text)
        #再提交一次
        form_data = {}
        form_data['ScriptManager1'] = 'UpdatePanel3|ButtonOK'
        form_data['__EVENTTARGET'] = ''
        form_data['__EVENTARGUMENT'] = ''
        form_data['__LASTFOCUS'] = ''
        form_data['__ASYNCPOST'] = 'true'
        form_data['ButtonOK'] = '提交申请'
        form_data['DropDownListQHXX'] = self.school_code
        view_state = re.findall(r'__VIEWSTATE\|(.+?)\|', response.text)
        view_generator = re.findall(r'__VIEWSTATEGENERATOR\|(.+?)\|', response.text)
        event_validation = re.findall(r'__EVENTVALIDATION\|(.+?)\|', response.text)
        form_data['__VIEWSTATE'] = view_state[0] if len(view_state)>0 else ''
        form_data['__EVENTVALIDATION'] = event_validation[0] if len(event_validation) > 0 else ''
        form_data['__VIEWSTATEGENERATOR'] = view_generator[0] if len(view_generator) > 0 else ''

        bodystr = urlencode(form_data, encoding='utf-8')
        headers = {}
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
        headers['Content-Length'] = '{}'.format(len(bodystr))

        if len(self.headers) != 17:
            print('zsbm1 post second possible headers is not correct, len of headers is:{}'.format(len(self.headers)))
        yield scrapy.Request(url=response.url, method='POST', body=bodystr, callback=self.post2_zsbm1_parse,
                             headers=headers, dont_filter=True)

    def post2_zsbm1_parse(self, response):
        with open('post2_zsbm1.aspx.html', 'w') as f:
            f.write(response.text)
        print(response.text)

    def button_ok_parse(self, response):
        with open('button_ok.aspx.html', 'w') as f:
            f.write(response.text)
        print(response.text)

    #公告的时候是返回的这个
    def XSBMXZ1_parse(self, response):
        with open('JW_XSBMXZ1.aspx.html', 'w') as f:
            f.write(response.text)
        # https://wsemal.com/CZBM/JW/JW_XSBMXZ1.aspx
        self.headers['Referer'] = response.url
        # https://wsemal.com/CZBM/JW/JW_ZSBM.aspx?FS=YES
        next_url = urljoin(response.url, '../JW/JW_ZSBM.aspx?FS=YES')
        self.headers['Sec-Fetch-User'] = '?1'
        return #当前已经结束
        yield scrapy.Request(url=next_url, callback=self.ZSBM_FS_YES_parse, headers=self.headers, dont_filter=True)
    def ZSBM_FS_YES_parse(self, response):
        with open('JW_ZSBM_FS_YES.aspx.html', 'w') as f:
            f.write(response.text)
        with open('JW_ZSBM_FS_YES.body.html', 'w') as f:
            f.write(response.body)