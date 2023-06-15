import scrapy
from urllib.parse import urljoin

class IqiyiVideoSpider(scrapy.Spider):
    name = 'iqiyi_video'
    allowed_domains = ['www.iqiyi.com']
    start_urls = ['http://www.iqiyi.com/dianying']

    def parse(self, response):
        with open('main-iqiyi.html', 'w') as f:
            f.write(response.text)
        # 找到 免费电影 的按钮
        free_url = response.xpath('//div[@class="mod-classes-blcoks"]/div[@class="classes-blcoks_pk"]/dl/dd/a[contains(string(),"免费电影")]')
        if free_url is not None:
            free_href = free_url.xpath('.//@href').get()
            full_url = urljoin(response.url, free_href)
            print(full_url)
            yield scrapy.Request(url=full_url, callback=self.parse_movie, dont_filter=True)

    def parse_movie(self, response):
        with open('movie-iqiyi.html', 'w') as f:
            f.write(response.text)
        # 获取所有的免费电影列表
        url_list = response.xpath('//div[@class="qy-list-page"]//div[@class="list-content"]//ul//li//a[@class="qy-mod-link"]')
        if url_list is not None:
            for i in url_list:
                qy_href = i.xpath('.//@href').get()
                full_qy_url = urljoin(response.url, qy_href)
                print(full_qy_url)
                yield scrapy.Request(url=full_qy_url, callback=self.parse_detail, dont_filter=True)
                break

    def parse_detail(self, response):
        with open('movie-detail.html', 'w') as f:
            f.write(response.text)

