import scrapy
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
            if len(itd) != 7:
                continue
            print('has seven td')
            school = itd[2].xpath('./text()')
            school_t = school.extract()[0]
            print(school_t)
            if school_t.find('C校') < 0:
                continue
            school_url = itd[6].xpath('./a/@href')
            school_url_t = school_url.extract()[0]
            print(school_url_t)
            school_url_full = urljoin(response.url, school_url_t)
            # click to qianghao entrance
            yield scrapy.Request(url=school_url_full, callback=self.school_parse)
            break

    def school_parse(self, response):
        with open('school.html', 'w') as f:
            f.write(response.text)
        # now should check identicard whether is normal
        print(response.text)
        sfzh = response.xpath('//a[@id="LinkButtonSFZH"]')
        sfzh_url = sfzh.xpath('./@href')
        sfzh_url_t = sfzh_url.extract()[0]
        print(sfzh_url_t)



