import scrapy


class BaidutestSpider(scrapy.Spider):
    name = 'baidutest'
    allowed_domains = ['*.cn']
    start_urls = ['https://www.baidu.com/']
    print(scrapy.Spider)

    def start_requests(self):
        headers = {

        }
        yield scrapy.Request(url='https://www.baidu.com/', callback=self.parse, headers=headers)


    def parse(self, response):
        with open('baidu.com.html', 'w') as f:
            f.write(response.text)
        print(response)
        print('come into parse function')
        print(response.request.headers)
        print(response.request.headers['Cookie'])

        post_url = 'https://m.imusic.cn/vapi/client/noac/activity/cloudtravel/thumbsUp'

        myFormData = {'name': 'John Doe', 'age': '27'}

        headers = {'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*',
                    'Accept': 'application/json, text/plain, */*',
                    'Access-Control-Allow-Credentials': 'true',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
                    'DNT': '1',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Origin': 'https://m.imusic.cn',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Referer': 'https://m.imusic.cn/h5v/yuntour/share?cc=5167&imid=00000580007028acf5a8b48d&videoId=92&activityId=221',
                    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
                   }
        cookies = response.request.headers['Cookie']
        with open('t.html', 'w') as f:
            f.write(response.text)

        dataraw = 'activityId=221&videoId=94&fingerprint=6aaa728e4f34e0e89d597bf943583524&portal=45&channelId=5167'
        yield scrapy.FormRequest(url=post_url, headers=headers, method='POST', formdata=dataraw,
                                 callback=self.parse_res, cookies=cookies)

    def parse_res(self, response):
        print(response.text)
