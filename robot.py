import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from hashlib import md5
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import sys

try:
    opt = Options()
    opt.add_argument('--headless')
    opt.add_argument('--disable-gpu')
    opt.add_argument('--no-sandbox')
    opt.add_argument('disable-dev-shm-usage')
    browser = webdriver.Chrome(options=opt)
    browser.implicitly_wait(5)
    js = open('./login.js', 'r',).read()
    browser.get('http://jwglxt.zstu.edu.cn/jwglxt/xtgl/login_slogin.html')
    browser.find_element(By.CLASS_NAME,'footer')
    time.sleep(0.1)
    browser.execute_script(js)
    browser.find_element(By.ID,'requestMap')
    time.sleep(0.1)
    result = browser.get_cookies()
    result = (result[0]['value'], result[1]['value'])
except NoSuchElementException:
    print('User Or Password Wrong!')
    browser.quit()
    sys.exit()
finally:
    browser.quit()
url = 'http://jwglxt.zstu.edu.cn/jwglxt/kbcx/xskbcx_cxXsgrkb.html'
headers = {"Host": "jwglxt.zstu.edu.cn",
           "Connection": "keep-alive",
           "Content-Length": "22",
           "Accept": "*/*",
           "X-Requested-With": "XMLHttpRequest",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.41",
           "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
           "Origin": "http://jwglxt.zstu.edu.cn",
           "Referer": "http://jwglxt.zstu.edu.cn/jwglxt/kbcx/xskbcx_cxXskbcxIndex.html",
           "Accept-Encoding": "gzip, deflate",
           "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
           "Cookie": "JSESSIONID="

           }
headers['Cookie'] = 'JSESSIONID={js};route={rt}'.format(
    rt=result[0], js=result[1])
data = {"xnm": "2021", "xqm": "2", "kzlx": "ck"}
true = True
false = False
requ = requests.post(url=url, headers=headers, data=data)
lst = eval(requ.text)['kbList']
classes = []


def rgWeek(startWeek, endWeek): return [
    i for i in range(startWeek, endWeek + 1)]


map = {'星期一': 1, '星期二': 2, '星期三': 3, '星期四': 4, '星期五': 5, '星期六': 6, '星期日': 7}

for course in lst:
    start = int(course['zcd'][0:course['zcd'].find('-')])
    end = int(course['zcd'][course['zcd'].find('-')+1:-1])
    span = course['jcs']
    jcs = list(range(int(span[0:span.find('-')]),
               int(span[span.find('-')+1:])+1))
    classes.append([course['kcmc'], course['xm'], course['cd_id'],
                   "", rgWeek(start, end), map[course['xqjmc']], jcs])

classTime = [None, (8, 10), (9, 5),  (10, 0),
             (10, 55),  (11, 50),  (13, 30), (14, 25), (15, 20), (16, 50), (19, 15), (20, 10), (21, 5)]
weeks = [None]
starterDay = datetime(2021, 9, 6)
for i in range(1, 30):
    singleWeek = [None]
    for d in range(0, 7):
        singleWeek.append(starterDay)
        starterDay += timedelta(days=1)
    weeks.append(singleWeek)


def uid_generate(key1, key2): return md5(
    f"{key1}{key2}".encode("utf-8")).hexdigest()


iCal = """BEGIN:VCALENDAR
METHOD:PUBLISH
VERSION:2.0
X-WR-CALNAME:课表
X-WR-TIMEZONE:Asia/Shanghai
CALSCALE:GREGORIAN
BEGIN:VTIMEZONE
TZID:Asia/Shanghai
END:VTIMEZONE
"""

runtime = datetime.now().strftime('%Y%m%dT%H%M%SZ')

for Class in classes:
    [Name, Teacher, Location, classID, classWeek,
        classWeekday, classOrder] = Class[:]
    Title = Name + " - " + Location

    customGEO = "LOCATION:理工教学楼？找得到的吧"  # 通过 geo_location 匹配，也可替换为其他文本

    for timeWeek in classWeek:
        classDate = weeks[timeWeek][classWeekday]
        startTime = classTime[classOrder[0]]
        endTime = classTime[classOrder[-1]]
        classStartTime = classDate + \
            timedelta(minutes=startTime[0] * 60 + startTime[1])
        classEndTime = classDate + \
            timedelta(minutes=endTime[0] * 60 + endTime[1] + 45)
        Description = classID + " 任课教师: " + Teacher + "。"

        StartTime = classStartTime.strftime('%Y%m%dT%H%M%S')
        EndTime = classEndTime.strftime('%Y%m%dT%H%M%S')
        singleEvent = f"""BEGIN:VEVENT
DTEND;TZID=Asia/Shanghai:{EndTime}
DESCRIPTION:{Description}
UID:CQUPT-{uid_generate(Name, StartTime)}
DTSTAMP:{runtime}
URL;VALUE=URI:{customGEO}
SUMMARY:{Title}
DTSTART;TZID=Asia/Shanghai:{StartTime}
END:VEVENT
"""
        iCal += singleEvent

iCal += "END:VCALENDAR"

with open("cqupt.ics", "w", encoding="utf-8") as w:
    w.write(iCal)

print('successful!')
