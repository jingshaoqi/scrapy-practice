import scrapy


class AiqiyiVideoSpider(scrapy.Spider):
    name = 'aiqiyi-video'
    allowed_domains = ['www.aiyiqi.com']
    start_urls = ['http://www.aiyiqi.com/']

    def parse(self, response):
        pass
