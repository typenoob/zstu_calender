from hashlib import md5
from datetime import datetime, timedelta
from Crypto.Cipher import DES
from Crypto.Util import Padding
from base64 import b64encode, b64decode
from requests import Session
from re import compile
import json


class ZstuSso:
    def __init__(self, username: str, password: str) -> None:
        self.__username = username
        self.__password = password
        self.__session = Session()

    def login(self) -> Session:
        login_url = 'https://sso.zstu.edu.cn/login'
        res = self.__session.get(login_url).text
        execution, croypto = self.__get_execution_and_crypto(res)
        payload = \
            {
                'username': self.__username,
                'type': 'UsernamePassword',
                '_eventId': 'submit',
                'geolocation': '',
                'execution': execution,
                'captcha_code': '',
                'croypto': croypto,
                'password': self.__encrypto_password(croypto),
            }
        res = self.__session.post(login_url, payload, allow_redirects=False)
        if len(res.content) != 0:
            return None
        else:
            return self.__session

    def get_session(self):
        return self.__session

    def __get_execution_and_crypto(self, data: str):
        execution_pat = compile('<p id="login-page-flowkey">(.*?)</p>')
        crypto_pat = compile('<p id="login-croypto">(.*?)</p>')
        return execution_pat.search(data).group(1), crypto_pat.search(data).group(1)

    def __encrypto_password(self, key: str) -> str:
        key = b64decode(key)
        enc = DES.new(key, DES.MODE_ECB)
        data = Padding.pad(self.__password.encode('utf-8'), 16)
        return b64encode(enc.encrypt(data))


def get_course_list() -> list:
    true = True
    false = False
    t = ZstuSso(config['sno'], config['password'])
    if not t.login():
        return None

    s = t.get_session()
    url = 'https://sso.zstu.edu.cn/login?service=http:%2F%2Fjwglxt.zstu.edu.cn%2Fsso%2Fjasiglogin'
    s.get(url)
    url = 'http://jwglxt.zstu.edu.cn/jwglxt/kbcx/xskbcx_cxXsgrkb.html'
    data = {"xnm": "2021", "xqm": "12", "kzlx": "ck"}
    r = s.post(url, data)
    return eval(r.text)['kbList']


def make_ics(lst, year=2022, month=2, day=21) -> str:
    def oeWeek(startWeek, endWeek, mode): return [
        i for i in range(startWeek, endWeek + 1) if (i + mode) % 2 == 0]

    def rgWeek(startWeek, endWeek): return [
        i for i in range(startWeek, endWeek + 1)]

    def uid_generate(key1, key2): return md5(
        f"{key1}{key2}".encode("utf-8")).hexdigest()
    convert = {'?????????': 1, '?????????': 2, '?????????': 3,
               '?????????': 4, '?????????': 5, '?????????': 6, '?????????': 7}
    classes = []
    for course in lst:
        start, end = map(int, compile('\d+').findall(course['zcd']))
        span = course['jcs']
        jcs = list(range(int(span[0:span.find('-')]),
                         int(span[span.find('-')+1:])+1))
        classes.append([course['kcmc'], course['xm'], course['cd_id'],
                        "", rgWeek(start, end), convert[course['xqjmc']], jcs])
    classTime = [None, (8, 10), (9, 5),  (10, 0),
                 (10, 55),  (11, 50),  (13, 30), (14, 25), (15, 20), (16, 50), (19, 15), (20, 10), (21, 5)]
    weeks = [None]
    starterDay = datetime(year, month, day)
    for i in range(1, 30):
        singleWeek = [None]
        for d in range(0, 7):
            singleWeek.append(starterDay)
            starterDay += timedelta(days=1)
        weeks.append(singleWeek)

    iCal = """BEGIN:VCALENDAR
METHOD:PUBLISH
VERSION:2.0
X-WR-CALNAME:??????
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

        customGEO = 'location'  # ?????? geo_location ????????????????????????????????????

        for timeWeek in classWeek:
            classDate = weeks[timeWeek][classWeekday]
            startTime = classTime[classOrder[0]]
            endTime = classTime[classOrder[-1]]
            classStartTime = classDate + \
                timedelta(minutes=startTime[0] * 60 + startTime[1])
            classEndTime = classDate + \
                timedelta(minutes=endTime[0] * 60 + endTime[1] + 45)
            Description = classID + " ????????????: " + Teacher + "???"

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

    return('successful!')


def main():
    global config
    config = json.load(open('config.json', encoding='utf-8'))
    if config['date']:
        date = datetime.strptime(config['date'], '%Y-%m-%d')
        courses = get_course_list()
        if courses:
            return make_ics(courses, date.year, date.month, date.day)
        else:
            return "???????????????????????????????????????????????????"
    else:
        courses = get_course_list()
        if courses:
            return make_ics(courses)
        else:
            return "???????????????????????????????????????????????????"


if __name__ == "__main__":
    main()
