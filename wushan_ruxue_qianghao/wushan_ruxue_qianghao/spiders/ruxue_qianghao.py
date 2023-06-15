import scrapy
import  json
from urllib.parse import urljoin

class RuxueQianghaoSpider(scrapy.Spider):
    name = 'ruxue_qianghao'
    allowed_domains = ['wsemal.com']
    start_urls = ['https://wsemal.com/XQZS/JW/JW_iframe.aspx']
    headers = {'host': 'wsemal.com',
               'cookie': '',
               'Connection':'keep-alive',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.43'}
    form_data = {'__EVENTTARGET': '',
                 '__EVENTARGUMENT': '',
                 '__VIEWSTATE': '',
                 '__VIEWSTATEGENERATOR': '',
                 '__EVENTVALIDATION': ''
                 }

    def parse(self, response):
        with open('ruxue.html', 'w') as f:
            f.write(response.text)
        items = response.xpath('//iframe[contains(@src, "main")]/@src')
        ckie = response.headers['Set-Cookie']
        fdf = str(ckie).split(';')
        # 只需要第一个
        str_cookie = fdf[0]
        self.headers['cookie'] = str_cookie
        self.headers['referer'] = response.url  # https://wsemal.com/XQZS/JW/JW_iframe.aspx
        for i in items:
            end_pr = i.extract()
            main_url = urljoin(response.url, end_pr) #https://wsemal.com/XQZS/JW/JWmain.aspx
            print(main_url)
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
            school_t = school.extract()[0]
            print(school_t)
            # 巫峡幼儿园 机关幼儿园 平湖幼儿园 西坪幼儿园 白杨幼儿园 圣泉幼儿园
            if school_t.find('巫峡幼儿园') < 0:
                continue
            school_url = itd[6].xpath('./a/@href')
            school_url_t = school_url.extract()[0]
            print(school_url_t)
            # https://wsemal.com/XQZS/JW/JW_ZSBM1.aspx?XX=XQ001&ID=13&TT=2023/6/18^%^209:00:00
            school_url_full = urljoin(response.url, school_url_t)
            # 输出请求的URL
            print('school_url_full:{}'.format(school_url_full))
            # click to qianghao entrance
            self.headers['referer'] = response.url
            #yield scrapy.Request(url=school_url_full, callback=self.school_parse_SFZH) #添加身份证号验证
            yield scrapy.Request(url=school_url_full, headers=self.headers, callback=self.school_parse) #bu不添加身份证号验证
            break

    def school_parse_SFZH(self, response):
        with open('school_parse_SFZH.html', 'w') as f:
            f.write(response.text)
        # now should check identicard whether is normal
        #print(response.text)
        sfzh = response.xpath('//a[@id="LinkButtonSFZH"]')
        sfzh_url = sfzh.xpath('./@href')
        sfzh_url_t = sfzh_url.extract()[0]
        print(sfzh_url_t)
        # add data
        fm_data = {'ScriptManager1': 'UpdatePanelAA|LinkButtonSFZH',
                   '__EVENTTARGET':'TextBox_SFZH',
                   'TextBox_SFZH': '500237202005319756',
                   #'TextBox_XM': '',
                   '__EVENTARGUMENT':'',
                   '__LASTFOCUS':'',
                   'TextBox_FJDZ': '重庆市巫山县高唐街道巫峡路110号4幢4单元1-2',
                   'TextBox_JZDZ': '重庆市巫山县高唐街道巫峡路110号4幢4单元1-2',
                   'TextBox_JFRXM': '王大海',
                   'TextBox_JFRSFZH': '500237198905319744',
                  'TextBox_TelePhone': '13278904979',
                   '__ASYNCPOST':'true'}
        yield scrapy.Request(url=response.url, method="POST", body=json.dumps(fm_data),callback=self.SFZH_check)

    def SFZH_check(self, response):
        with open('sfzh_check_sfzh.html', 'w') as f:
            f.write(response.text)
        #print(response.text)
        self.school_parse(response)

    def school_parse(self, response):
        with open('school_parse.html', 'w') as f:
            f.write(response.text)
        # now should check identicard whether is normal
        # print(response.text)
        # sfzh = response.xpath('//a[@id="LinkButtonSFZH"]')
        # sfzh_url = sfzh.xpath('./@href')
        # sfzh_url_t = sfzh_url.extract()[0]
        # print(sfzh_url_t)
        # add data
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
        self.form_data['__LASTFOCUS'] = ''
        self.form_data['TextBox_XM'] = '王秀丽'
        self.form_data['TextBox_SFZH'] = '500237202005319756'
        self.form_data['TextBox_FJDZ'] = '重庆市巫山县高唐街道巫峡路110号4幢4单元1-2'
        self.form_data['TextBox_JZDZ'] = '重庆市巫山县高唐街道巫峡路110号4幢4单元1-2'
        self.form_data['TextBox_JFRXM'] = '王大海'
        self.form_data['TextBox_JFRSFZH'] = '500237198905319744'
        self.form_data['TextBox_TelePhone'] = '13278904979'
        self.form_data['__ASYNCPOST'] = 'true'
        yield scrapy.Request(url=response.url, method="POST", body=json.dumps(self.form_data), headers=self.headers, callback=self.submit_info)

    def submit_info(self, response):
        with open('submit_info.html', 'w') as f:
            f.write(response.text)
        print(response.text)



