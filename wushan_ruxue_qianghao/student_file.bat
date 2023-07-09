set path1=%~dp0
set filename=student_file1.json
set fullpath=%path1%%filename%
echo %fullpath%
scrapy crawl ruxue_qianghao -a student_file=%fullpath%
pause

