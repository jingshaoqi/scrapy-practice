import scrapy
import  json
from urllib.parse import urljoin

class RuxueQianghaoSpider(scrapy.Spider):
    name = 'ruxue_qianghao'
    allowed_domains = ['wsemal.com']
    start_urls = ['https://wsemal.com/XQZS/JW/JW_iframe.aspx']

    def parse(self, response):
        with open('ruxue.html', 'w') as f:
            f.write(response.text)
        items = response.xpath('//iframe[contains(@src, "main")]/@src')
        for i in items:
            end_pr = i.extract()
            main_url = urljoin(response.url, end_pr)
            print(main_url)
            # go to jw main.aspx web
            yield scrapy.Request(url=main_url, callback=self.JWmain)

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
            if school_t.find('A校') < 0:
                continue
            school_url = itd[6].xpath('./a/@href')
            school_url_t = school_url.extract()[0]
            print(school_url_t)
            school_url_full = urljoin(response.url, school_url_t)
            # 输出请求的URL
            print('school_url_full:{}'.format(school_url_full))
            # click to qianghao entrance
            #yield scrapy.Request(url=school_url_full, callback=self.school_parse_SFZH) #添加身份证号验证
            yield scrapy.Request(url=school_url_full, callback=self.school_parse) #bu不添加身份证号验证
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
        print(response.text)
        sfzh = response.xpath('//a[@id="LinkButtonSFZH"]')
        sfzh_url = sfzh.xpath('./@href')
        sfzh_url_t = sfzh_url.extract()[0]
        print(sfzh_url_t)
        # add data
        fm_data = {#'ScriptManager1': 'UpdatePanelAA|LinkButtonSFZH',
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
        yield scrapy.Request(url=response.url, method="POST", body=json.dumps(fm_data),callback=self.submit_info)

    def submit_info(self, response):
        with open('submit_info.html', 'w') as f:
            f.write(response.text)
        print(response.text)



