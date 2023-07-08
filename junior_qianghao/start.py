# coding=utf-8

from scrapy.cmdline import execute

#execute('scrapy crawl junior_qh'.split(' '))
#execute('scrapy crawl junior_qh -a L_username="500237201012240021-" -a L_password="hm240021-" -a first_school="巫峡初中-" -a second_school="巫山初中-" -a student_name="何萌-"'.split(' '))
execute(['scrapy', 'crawl', 'junior_qh',
         '-a', 'start_time=2023-7-8 9:00:00 000000',
         '-a', 'L_username=500237201012240021',
         '-a', 'L_password=hm240021',
         '-a', 'first_school=巫峡初中',
         '-a', 'second_school=巫山初中',
         '-a', 'student_name=何萌'])




