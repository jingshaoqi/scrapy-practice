import scrapy


class ScrapytestSpider(scrapy.Spider):
    name = "scrapytest2"
    allowed_domains = ["www.taobao.com"]
    start_urls = ['https://www.taobao.com']

    def parse(self, response):
        print('name:{} {}'.format(self.name,response.url))
