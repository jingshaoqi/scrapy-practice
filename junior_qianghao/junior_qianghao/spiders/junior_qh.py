import scrapy


class JuniorQhSpider(scrapy.Spider):
    name = "junior_qh"
    allowed_domains = ["www.baidu.com"]
    start_urls = ["https://www.baidu.com"]

    def parse(self, response):
        pass
