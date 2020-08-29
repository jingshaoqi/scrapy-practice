import scrapy


class BaidutestSpider(scrapy.Spider):
    name = 'baidutest'
    allowed_domains = ['www.baidu.com']
    start_urls = ['http://www.baidu.com/']
    print(scrapy.Spider)

    def parse(self, response):
        print(response)
        print('come here aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        pass
