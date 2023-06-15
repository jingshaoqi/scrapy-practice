import scrapy


class YanzhengmaSpider(scrapy.Spider):
    name = "yanzhengma"
    allowed_domains = ["www.baidu.com"]
    start_urls = ["https://www.baidu.com"]

    def parse(self, response):
        pass
