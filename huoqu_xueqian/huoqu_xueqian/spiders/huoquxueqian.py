import scrapy
from urllib.parse import urlencode
import scrapy
from urllib.parse import urljoin
import re


monthDayArr = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
coef = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
verify = ['1',  '0',  'X',  '9', '8', '7', '6', '5', '4', '3', '2']

def generate_sfzh_by_day(month, day):
    res_lst = []
    for m in range(999):
        result = '5002372019{:0>2d}{:0>2d}{:0>3d}'.format(month, day, m + 1)
        sum = 0
        for i in range(len(result)):
            sum += int(result[i]) * coef[i]

        result += verify[sum % 11]
        # print(len(result))
        res_lst.append(result)
    return res_lst
def generate_sfzhs():
    month = 9
    day = 1
    return generate_sfzh_by_day(month, day)


class HuoquxueqianSpider(scrapy.Spider):
    name = "huoquxueqian"
    allowed_domains = ["www.baidu.com"]
    start_urls = ["https://wsemal.com/XQZS/JW/JW_iframe.aspx"]
    form_data={}
    def parse(self, response):
        next_url = urljoin(response.url, '../JW/JWmain.aspx')
        yield scrapy.Request(url=next_url, callback=self.main_parse, dont_filter=True)

    def main_parse(self, response):
        qhrk = response.xpath('//a[contains(text(),"抢号入口")]/@href')
        if qhrk is None:
            return
        qhrk_url = urljoin(response.url, qhrk.get())
        yield scrapy.Request(url=qhrk_url, callback=self.qianghao_rukou, dont_filter=True)

    def qianghao_rukou(self, response):
        #生成多个身份证号
        sfzhs = generate_sfzhs()
        sfzh = sfzhs.pop(0)
        meta = {'sfzhs':sfzhs, 'sfzh':sfzh}
        # 提取formdata信息
        form_data = {}
        event_target = response.xpath('//input[@id="__EVENTTARGET"]/@value')
        #form_data['__EVENTTARGET'] = event_target.extract()[0] if len(event_target) > 0 else ''
        event_argument = response.xpath('//input[@id="__EVENTARGUMENT"]/@value')
        form_data['__EVENTARGUMENT'] = event_argument.extract()[0] if len(event_argument) > 0 else ''
        view_state = response.xpath('//input[@id="__VIEWSTATE"]/@value')
        form_data['__VIEWSTATE'] = view_state.extract()[0] if len(view_state) > 0 else ''
        event_validation = response.xpath('//input[@id="__EVENTVALIDATION"]/@value')
        form_data['__EVENTVALIDATION'] = event_validation.extract()[0] if len(event_validation) > 0 else ''
        view_state_generator = response.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')
        form_data['__VIEWSTATEGENERATOR'] = view_state_generator.extract()[0] if len(view_state_generator) > 0 else ''

        #注释的这两行也可以使用
        #form_data['ScriptManager1'] = 'UpdatePanelAA|LinkButtonSFZH'
        #form_data['__EVENTTARGET'] = 'LinkButtonSFZH'
        form_data['ScriptManager1'] = 'UpdatePanelAA|TextBox_SFZH'
        form_data['__EVENTTARGET'] = 'TextBox_SFZH'
        form_data['__LASTFOCUS'] = ''
        form_data['TextBox_SFZH'] = sfzh #'500237202005319991'
        form_data['TextBox_XM'] = ''
        form_data['TextBox_FJDZ'] = ''
        form_data['TextBox_JZDZ'] = ''
        form_data['TextBox_JFRXM'] = ''
        form_data['TextBox_JFRSFZH'] = ''
        form_data['TextBox_TelePhone'] = ''
        form_data['__ASYNCPOST'] = 'true'
        bodystr = urlencode(form_data, encoding='utf-8')
        headers = {}
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
        #headers['Content-Length'] = '{}'.format(len(bodystr))
        yield scrapy.Request(url=response.url, method='POST', body=bodystr, headers=headers,
                             callback=self.sfzh_check_parse, dont_filter=True, meta=meta)

    def sfzh_check_parse(self, response):
        ts = response.xpath('//span[@id="LabelTS"]/text()')
        if len(ts) > 0:
            ts_str = ts.get()
            sf = response.meta['sfzh']
            #如果已经在某个地方报名保存幼儿园信息
            gd_name = re.findall(r'已在(.+?)报名', response.text)
            if len(gd_name) > 0:
                gdname = gd_name[0]
                print('{} {}'.format(sf, gdname))
            else:
                print('{} 已经成功报名'.format(sf))
        #获取下一个身份证号码
        sfzhs = response.meta['sfzhs']
        if len(sfzhs) <= 0:
            return
        sfzh = sfzhs.pop(0)
        response.meta['sfzh'] = sfzh
        form_data = {}
        view_state = re.findall(r'__VIEWSTATE\|(.+?)\|', response.text)
        view_generator = re.findall(r'__VIEWSTATEGENERATOR\|(.+?)\|', response.text)
        event_validation = re.findall(r'__EVENTVALIDATION\|(.+?)\|', response.text)
        form_data['__VIEWSTATE'] = view_state[0] if len(view_state) > 0 else ''
        form_data['__EVENTVALIDATION'] = event_validation[0] if len(event_validation) > 0 else ''
        form_data['__VIEWSTATEGENERATOR'] = view_generator[0] if len(view_generator) > 0 else ''

        form_data['ScriptManager1'] = 'UpdatePanelAA|TextBox_SFZH'
        form_data['__EVENTARGUMENT'] = ''
        form_data['__EVENTTARGET'] = 'TextBox_SFZH'
        form_data['__LASTFOCUS'] = ''
        form_data['TextBox_SFZH'] = sfzh  # '500237202005319991'
        form_data['TextBox_XM'] = ''
        form_data['TextBox_FJDZ'] = ''
        form_data['TextBox_JZDZ'] = ''
        form_data['TextBox_JFRXM'] = ''
        form_data['TextBox_JFRSFZH'] = ''
        form_data['TextBox_TelePhone'] = ''
        form_data['__ASYNCPOST'] = 'true'
        bodystr = urlencode(form_data, encoding='utf-8')
        headers = {}
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
        #headers['Content-Length'] = '{}'.format(len(bodystr))
        yield scrapy.Request(url=response.url, method='POST', body=bodystr, headers=headers,
                             callback=self.sfzh_check_parse, dont_filter=True, meta=response.meta)