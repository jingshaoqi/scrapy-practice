# coding=utf-8

from scrapy.cmdline import execute

execute('scrapy crawl ruxue_qianghao -a student_file=student_file1.json'.split(' '))
# execute(['scrapy', 'crawl', 'ruxue_qianghao'])
