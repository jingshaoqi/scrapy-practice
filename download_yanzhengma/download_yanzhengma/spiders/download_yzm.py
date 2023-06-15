import scrapy
import ddddocr

#利用 ddddocr识别验证码
def recognize_yzm(img_bytes):
    ocr = ddddocr.DdddOcr()
    res = ocr.classification(img_bytes)
    return res


class DownloadYzmSpider(scrapy.Spider):
    name = "download_yzm"
    allowed_domains = ["wsemal.com"]
    start_url = 'https://wsemal.com/CZBM/public/checkcode.aspx'
    start_urls = [start_url]
    count = 0

    def parse(self, response):
        # response.body是验证码图片数据
        self.count += 1
        yzm_res = recognize_yzm(response.body)
        filename = './img/{:0>5d}_{}.jpg'.format(self.count, yzm_res)
        with open(filename, 'wb') as f:
            f.write(response.body)
        if self.count < 2000:
            yield scrapy.Request(url=self.start_url, method="GET", callback=self.parse, dont_filter='true')
        else:
            return



