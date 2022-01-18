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
            raise RuntimeError('Failed')

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
    t.login()
    s = t.get_session()
    url = 'https://sso.zstu.edu.cn/login?service=http:%2F%2Fjwglxt.zstu.edu.cn%2Fsso%2Fjasiglogin'
    s.get(url)
    url = 'http://jwglxt.zstu.edu.cn/jwglxt/kbcx/xskbcx_cxXsgrkb.html'
    data = {"xnm": "2021", "xqm": "12", "kzlx": "ck"}
    r = s.post(url, data)
    return eval(r.text)['kbList']


def make_ics(lst, year=2022, month=2, day=21) -> str:
    classes = []

    def rgWeek(startWeek, endWeek): return [
        i for i in range(startWeek, endWeek + 1)]
    map = {'星期一': 1, '星期二': 2, '星期三': 3,
           '星期四': 4, '星期五': 5, '星期六': 6, '星期日': 7}
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
    starterDay = datetime(year, month, day)
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

    return('successful!')


config = json.load(open('config.json', encoding='utf-8'))


def main():
    make_ics(get_course_list())


if __name__ == "__main__":
    main()
