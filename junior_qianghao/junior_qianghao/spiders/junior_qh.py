import time
from datetime import datetime, timedelta
import json
import re
from urllib.parse import urlencode
import scrapy
from urllib.parse import urljoin
import ddddocr
import logging
import logging.config

logging.basicConfig(filename='logging.log', level=logging.DEBUG, format='%(asctime)s %(funcName)s:%(lineno)d %(message)s',  encoding='utf-8', filemode='a')

class JuniorQhSpider(scrapy.Spider):
    name = "junior_qh"
    allowed_domains = ["wsemal.com"]
    start_urls = ["https://wsemal.com/CZBM/JW/JW_iframe.aspx?FS=CC"]
    user_dll_url = ''
    school_code = ''
    grab_time_n = datetime.now()
    grab_time_str = '2023-7-8 14:30:00 000000'
    L_username = '500237201010221601'
    L_password = 'Mayao911162'
    first_school = '巫山初中'
    second_school = '巫山二中'
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
        self.grab_time_n = datetime.strptime(self.grab_time_str, '%Y-%m-%d %H:%M:%S %f')
        headers = {'Sec-Fetch-User': '?1',
                   'Upgrade-Insecure-Requests': '1'}
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=headers, dont_filter=True)

    def parse(self, response):
        logging.info('response.url:{}'.format(response.url))
        logging.info(response.text)
        # find mainframe
        main_frm = response.xpath('//tr/td/div/iframe[@id="mainFrame"]/@src')
        if main_frm is None or len(main_frm) <= 0:
            return
        main_frm_url = main_frm.extract()[0]
        # https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        main_frm_url_full = urljoin(response.url, main_frm_url)
        logging.info(main_frm_url_full)
        headers = {'Referer': response.url,
                   'Sec-Fetch-Dest': 'iframe',
                   'Sec-Fetch-Site': 'same-origin',
                   'Upgrade-Insecure-Requests': '1'}
        self.user_dll_url = main_frm_url_full #https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        yield scrapy.Request(url=main_frm_url_full, callback=self.main_parse, headers=headers, dont_filter=True)

    def main_parse(self, response):
        logging.info('response.url:{}'.format(response.url))
        logging.info(response.text)
        # 现在来获取验证码的图片
        yzm_url = response.xpath('//table/tr/td/input[@id="ImageButtonYZM"]/@src')
        if yzm_url is None or len(yzm_url) <= 0:
            return
        # https://wsemal.com/CZBM/public/checkcode.aspx
        yzm_url_t = yzm_url.extract()[0]
        self.yzm_url_full = urljoin(response.url, yzm_url_t)
        # https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        headers = {'Referer': self.user_dll_url,
                   'Accept': 'image/avif,image/webp,*/*',
                   'Sec-Fetch-Dest': 'image',
                   'Sec-Fetch-Mode': 'no-cors',
                   'Sec-Fetch-Site': 'same-origin'}

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
        with open('yan_zheng_ma.jpg',  mode='wb') as f:
            f.write(response.body)
        # 利用 ddddocr识别验证码
        ocr = ddddocr.DdddOcr()
        res = ocr.classification(response.body)
        print('验证码为:{}'.format(res))
        headers = {'Referer': self.user_dll_url,
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                   'Origin': 'https://wsemal.com',
                   'Upgrade-Insecure-Requests': '1',
                   'Sec-Fetch-Dest': 'iframe',
                   'Sec-Fetch-Mode': 'navigate',
                   'Sec-Fetch-Site': 'same-origin',
                   'Sec-Fetch-User': '?1',
                   'Content-Type': 'application/x-www-form-urlencoded'}

        #现在使用用户名，密码，验证码登录
        self.form_data['L_username'] = self.L_username
        self.form_data['L_password'] = self.L_password
        self.form_data['L_YZM'] = res
        self.form_data['Button1'] = '登录'
        bodystr = urlencode(self.form_data)
        logging.info('username:{} password:{} verify code:{}'.format(self.form_data['L_username'],
                                                                     self.form_data['L_password'], res))
        #准备好了数据 按 登录 按钮
        logging.info('请求登录网页self.user_dll_url：{}'.format(self.user_dll_url))
        yield scrapy.Request(url=self.user_dll_url, method='POST', body=bodystr,
                             callback=self.login_parse, headers=headers, dont_filter=True)
    #登录结果分析，登录结果中添加了 cookie XSQHUserName
    def login_parse(self, response):
        logging.info('response.url:{}'.format(response.url))
        logging.info(response.text)
        # 获取cookie XSQHUserName的值
        if response.headers.get('Set-Cookie') is None:
            #再次请求一个验证码
            logging.info('login fail, try to get another verify code')
            headers = {'Referer': self.user_dll_url,
                       'Accept': 'image/avif,image/webp,*/*',
                       'Sec-Fetch-Dest': 'image',
                       'Sec-Fetch-Mode': 'no-cors',
                       'Sec-Fetch-Site': 'same-origin'}
            yield scrapy.Request(url=self.yzm_url_full, callback=self.yzm_parse, headers=headers, dont_filter=True)
            return
        logging.info('login success')
        ckie = response.headers['Set-Cookie']
        if str(ckie).find('XSQHUserName') < 0:
            logging.info('login fail too. not found cookie:XSQHUserName')
            return
        # https://wsemal.com/CZBM/JW/JW_ZSBM.aspx
        #找到请求的下一个网页
        zsbm = response.xpath('//script[contains(text(), "mainFrame") and contains(text(), "href")]/text()')
        if zsbm is None or len(zsbm) <= 0:
            logging.info('not found zxbm page')
            return
        zsbm_t = zsbm.get()
        zsbm_res = re.findall(r"href=\'(.+?)\';", zsbm_t)
        if len(zsbm_res) <= 0:
            return
        zsbm_ur = zsbm_res[0] # ../JW/JW_ZSBM.aspx
        zsbm_url = urljoin(response.url, zsbm_ur) # 'https://wsemal.com/CZBM/JW/JW_ZSBM.aspx'
        logging.info('请求下一个网页zsbm_url：{}'.format(zsbm_url))
        # 从这个请求开始得到抢号的界面，没有开始的时候是其他界面
        self.zsbm_url = zsbm_url
        headers = {'Origin': 'https://wsemal.com',
                   'Sec-Fetch-Dest': 'iframe',
                   'Sec-Fetch-Mode': 'navigate',
                   'Sec-Fetch-Site': 'same-origin',
                   'Upgrade-Insecure-Requests': '1'
                   }
        yield scrapy.Request(url=zsbm_url, callback=self.ZSBM_parse, headers=headers, dont_filter=True)

    def ZSBM_parse(self, response):
        logging.info('response.url:{}'.format(response.url))
        logging.info(response.text)
        headers = {'Origin': 'https://wsemal.com',
                   'Sec-Fetch-Dest': 'iframe',
                   'Sec-Fetch-Mode': 'navigate',
                   'Sec-Fetch-Site': 'same-origin',
                   'Upgrade-Insecure-Requests': '1'
                   }
        # https://wsemal.com/CZBM/JW/JW_UserDL.aspx
        #再进入 https://wsemal.com/CZBM/JW/JW_XSBMXZ1.aspx
        # 它的参数需要解析出来才行
        spt = response.xpath('//script/text()')
        if spt is None or len(spt) <= 0:
            #判断是否是已经抢到号，抢到号了就不需要再请求数据了
            zsjl = response.xpath('//center/table/tr')
            if zsjl is None or len(zsjl) < 0:
                return
            for j in zsjl:
                tds = j.xpath('./td')
                if tds is None or len(tds) <= 0:
                    return
                if len(tds) != 2:
                    continue
                a = tds[0].xpath('./text()').get()
                record = tds[1].xpath('./text()').get()
                if a.find('正式记录') >= 0 and record.find('IP') >= 0:
                    logging.info('已经抢到号了，记录为:{}'.format(record))
                    return
            #没有抢到号继续请求
            time.sleep(0.1)
            yield scrapy.Request(url=response.url, callback=self.ZSBM_parse, headers=headers, dont_filter=True)
            return
        spt_t = spt.extract()[0]
        #返回的是报名须知
        if spt_t.find('JW_XSBMXZ1.aspx') >= 0:
            str_all = re.findall(r"location=\'(.+?)\'", spt_t)
            if str_all is None or len(str_all) <= 0:
                return
            XSBMXZ1_url = urljoin(response.url, str_all[0])
            yield scrapy.Request(url=XSBMXZ1_url, callback=self.XSBMXZ1_parse, headers=headers, dont_filter=True)
            return
        # 有可能为 'alert(\'未开放报名权限！\');'
        if spt_t.find('JW_ZSBM1.aspx') < 0:
            #说明还没有到开始抢号的时间，重新进入
            localtm = datetime.now()
            if localtm < self.grab_time_n:
                df = self.grab_time_n - localtm
                n = df.total_seconds()
                if n > 300:
                    self.sleep_time(250)
                    tm = datetime.now() - localtm
                    print('cost time:{}'.format(tm.total_seconds()))
                else:
                    self.sleep_time(n)
            else:
                time.sleep(0.1)
            headers['Referer'] = self.user_dll_url
            yield scrapy.Request(url=response.url, callback=self.ZSBM_parse, headers=headers,  dont_filter=True)
            return
        str_all = re.findall(r"href=\'(.+?)\';", spt_t)
        if str_all is None or len(str_all) <= 0:
            return
        zsbm1_url = urljoin(response.url, str_all[0])
        logging.info('请求下一个网页zsbm1_url：{}'.format(zsbm1_url))
        yield scrapy.Request(url=zsbm1_url, callback=self.ZSBM1_parse, headers=headers, dont_filter=True)

    def ZSBM1_parse(self, response):
        logging.info('response.url:{}'.format(response.url))
        logging.info(response.text)
        headers = {'Origin': 'https://wsemal.com',
                   'Sec-Fetch-Dest': 'iframe',
                   'Sec-Fetch-Mode': 'navigate',
                   'Sec-Fetch-Site': 'same-origin'
                   }
        #a判断状态是否在进行中
        zt = response.xpath('//span[@id="Label_ZT"]/text()')
        if zt is None or len(zt) <= 0 or zt.get().find("进行中") < 0:
            time.sleep(0.1)
            yield scrapy.Request(url=self.zsbm_url, callback=self.ZSBM_parse, headers=headers, dont_filter=True)
            return
        #解析响应中有用的数据

        select_school_name = self.first_school
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
                logging.info('{} 还有{}个空位'.format(select_school_name, num))
                choose_suc = 1
            break
        if choose_suc == 0:
            if len(self.second_school) <= 0 or self.second_school == self.first_school:
                logging.info('cant find suitable school:{}'.format(select_school_name))
                return
            #再次选择
            select_school_name = self.second_school
            for y in ful_sch:
                tds = y.xpath('./td/text()')
                if len(tds) < 6:
                    continue
                sch_name = tds[1].get()
                if sch_name.find(select_school_name) < 0:
                    continue
                num = int(tds[4].get())
                if num > 0:
                    logging.info('{} 还有{}个空位'.format(select_school_name, num))
                    choose_suc = 1
                break
        if choose_suc == 0:
            logging.info('cant find suitable school:{}'.format(select_school_name))
            return
        else:
            logging.info('find suitable school:{}'.format(select_school_name))
        # select_school_code = 'A23317' #A23313;A23317;B23301;B23304
        # 先要获取学校名称和代号
        schools = response.xpath('//tr/td/select/option')
        if schools is None or len(schools) <= 0:
            logging.info('not have schools')
            yield scrapy.Request(url=self.zsbm_url, callback=self.ZSBM_parse, dont_filter=True)
            return
        for i in schools:
            school_name = i.xpath('./text()').extract()[0]
            if school_name.find(select_school_name) >= 0:
                self.school_code = i.xpath('./@value').extract()[0]
                break
        if len(self.school_code) <= 0:
            logging.info('not found {} in the list'.format(select_school_name))
            return

        #再要获取下一个请求的url
        action_url = response.xpath('//body/form[@id="form1" and @method="post"]/@action')
        if action_url is None or len(action_url) <= 0:
            return
        action_url_t = action_url.extract()[0]
        # https://wsemal.com/CZBM/JW/JW_ZSBM1.aspx?TT=2023%2f6%2f17+8%3a30%3a00&PC=%u7b2c%u4e00%u6279%u6b21(A%u8f6e)
        action_url_full = urljoin(response.url, action_url_t)

        # https://wsemal.com/CZBM/JW/JW_ZSBM.aspx
        headers = {'Referer': response.url,
                   'Accept': '*/*',
                   'Origin': 'https://wsemal.com',
                   'Cache-Control': 'no-cache',
                   'X-MicrosoftAjax': 'Delta=true',
                   'Sec-Fetch-Dest': 'empty',
                   'Sec-Fetch-Mode': 'cors',
                   'Sec-Fetch-Site': 'same-origin',
                   'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                   'TE': 'trailers'}
        # 修改请求的数据 在实际的浏览器中测试分两次进行，一次是展开下拉列表，第二次是按提交按钮，
        form_data = {}
        form_data['ScriptManager1'] = 'UpdatePanel3|DropDownListQHXX'
        form_data['__EVENTTARGET'] = 'DropDownListQHXX'
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
        logging.info('submit information action_url_full：{}'.format(action_url_full))
        logging.info('length:{} bodystr:{}'.format(len(bodystr), bodystr))
        yield scrapy.Request(url=action_url_full, method='POST', body=bodystr, callback=self.post_zsbm1_parse,
                             headers=headers, dont_filter=True)


    def post_zsbm1_parse(self, response):
        logging.info('response.url:{}'.format(response.url))
        logging.info(response.text)
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
        headers = {'Referer': response.url,
                   'Accept': '*/*',
                   'Origin': 'https://wsemal.com',
                   'Cache-Control': 'no-cache',
                   'X-MicrosoftAjax': 'Delta=true',
                   'Sec-Fetch-Dest': 'empty',
                   'Sec-Fetch-Mode': 'cors',
                   'Sec-Fetch-Site': 'same-origin',
                   'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                   'TE': 'trailers'}
        logging.info('请求下一个网页response.url：{}'.format(response.url))
        logging.info('length:{} bodystr:{}'.format(len(bodystr), bodystr))
        next_url = response.url
        yield scrapy.Request(url=next_url, method='POST', body=bodystr, callback=self.post2_zsbm1_parse,
                             headers=headers, dont_filter=True)

    def post2_zsbm1_parse(self, response):
        logging.info('response.url:{}'.format(response.url))
        logging.info(response.text)
        #如果成功抢到就停止运行
        if response.text.find('已成功报名') >= 0:
            return
        logging.info('继续抢号 zsbm_url：{}'.format(self.zsbm_url))
        headers = {'Referer': self.user_dll_url,
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                   'Origin': 'https://wsemal.com',
                   'Upgrade-Insecure-Requests': '1',
                   'Sec-Fetch-Dest': 'iframe',
                   'Sec-Fetch-Mode': 'navigate',
                   'Sec-Fetch-Site': 'same-origin',
                   'TE': 'trailers'}
        yield scrapy.Request(url=self.zsbm_url, callback=self.ZSBM_parse,headers=headers, dont_filter=True)

    def button_ok_parse(self, response):
        logging.info('response.url:{}'.format(response.url))
        logging.info(response.text)

    #公告的时候是返回的这个
    def XSBMXZ1_parse(self, response):
        logging.info('response.url:{}'.format(response.url))
        logging.info(response.text)
        # https://wsemal.com/CZBM/JW/JW_XSBMXZ1.aspx
        # https://wsemal.com/CZBM/JW/JW_ZSBM.aspx?FS=YES
        next_url = urljoin(response.url, '../JW/JW_ZSBM.aspx?FS=YES')
        headers = {'Origin': 'https://wsemal.com',
                   'Sec-Fetch-Dest': 'iframe',
                   'Sec-Fetch-Mode': 'navigate',
                   'Sec-Fetch-Site': 'same-origin',
                   'Upgrade-Insecure-Requests': '1',
                   'Sec-Fetch-User': '?1'
                   }
        yield scrapy.Request(url=next_url, callback=self.ZSBM_parse, headers=headers, dont_filter=True)

    def sleep_time(self, total_seconds):
        localtm = datetime.now()
        wt = 0
        wt_delta = 0.01
        while 1:
            curtm = datetime.now()
            if curtm > localtm + timedelta(seconds=total_seconds):
                break
            else:
                if wt >= 1:
                    dt = self.grab_time_n - curtm
                    print('left time:{}'.format(dt))
                    wt = 0
                time.sleep(wt_delta)
                wt += wt_delta