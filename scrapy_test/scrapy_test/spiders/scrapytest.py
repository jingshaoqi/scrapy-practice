import scrapy


class ScrapytestSpider(scrapy.Spider):
    name = "scrapytest"
    allowed_domains = ["www.baidu.com"]
    start_urls = ['http://localhost:8023/报名须知响应.html']

    def parse(self, response):
        res = response.text.find('进行中')>=0 and response.text.find('提交申请') >= 0
        if res is not True:
            print(' not found')
        else :
            print('found')
