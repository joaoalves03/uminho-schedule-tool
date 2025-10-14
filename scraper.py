import math
import re
from datetime import datetime, timedelta

import bs4
import requests
from bs4 import BeautifulSoup

from lesson import Lesson

SCHEDULE_URL = "https://alunos.uminho.pt/PT/estudantes/Paginas/InfoUteisHorarios.aspx"
STATE = lambda course, course_id: (
    f'{{"logEntries":[],"value":"{course_id}","text":"{course}","enabled":true,'
    f'"checkedIndices":[],"checkedItemsTextOverflows":false}}'
)
TIME_SLOT_SIZE_PX = 60


# Powered by hopes and dreams
class Scraper:
    course_name = None
    form_id = None

    lessons: list[Lesson] = []

    def __init__(self, course_name: str):
        self.course_name = course_name

        res = requests.get(SCHEDULE_URL)
        soup = BeautifulSoup(res.text, features="lxml")
        self.form_id = self.get_form_id(soup)

        res = requests.post(SCHEDULE_URL, headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }, data={
            **self.parse_hidden_inputs(soup),
            f"{self.form_id}dataCurso": self.course_name,
            f"{self.get_client_state_input_name(soup)}": STATE(self.course_name, self.get_course_id(soup, course_name))
        })

        if "Mostrar horário expandido" not in res.text:
            print("Couldn't get course data. Stopping...")
            exit(-1)

        soup = BeautifulSoup(res.text, features="lxml")

        res = requests.post(SCHEDULE_URL, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            # Note: Must fake user agent, or else the website will not render the schedule correctly
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0"
        }, data={
            **self.parse_hidden_inputs(soup),
            "__EVENTTARGET": f"{self.form_id}chkMostraExpandido",
            f"{self.form_id}dataCurso": self.course_name,
            f"{self.form_id}dataAnoCurricular": "1",
            f"{self.form_id}dataWeekSelect": "2025-10-14",
            f"{self.form_id}chkMostraExpandido": "on"
        })

        self.parse_schedule(res.text)
        for lesson in self.lessons:
            print(lesson)



    def parse_schedule(self, raw_schedule_data: str):
        soup = BeautifulSoup(raw_schedule_data, features="lxml")
        table = soup.select_one(".rsContent > table:nth-child(1)")

        days = [th.find("a").attrs["href"][1:] for th in table.select(".rsHorizontalHeaderTable th")]
        earliest_hour = self.parse_earliest_hour(table)
        n_time_slots = self.get_number_of_time_slots(table)

        for day_index, day in enumerate(days):
            time = earliest_hour

            for time_slot in range(1, n_time_slots + 1):
                schedule_slot = table.select_one(
                    f".rsContentTable > tr:nth-child({time_slot}) > td:nth-child({day_index + 1})")

                # if slot contains anything at all
                if schedule_slot.text.strip():
                    self.lessons.append(self.parse_lesson(schedule_slot, time, day))

                time += timedelta(minutes=30)

    @staticmethod
    def parse_hidden_inputs(soup: BeautifulSoup):
        return {
            _input.get("name"): _input.get("value")
            for _input in soup.select("input[type='hidden']")
        }

    @staticmethod
    def get_course_id(soup: BeautifulSoup, course_name: str) -> str | None:
        names = [li.get_text(strip=True) for li in soup.select("li.rcbItem")]

        text = soup.decode()
        match = re.search(r'"itemData"\s*:\s*\[(.*?)]', text, flags=re.S)
        if not match:
            return None

        ids = re.findall(r'["\']?value["\']?\s*:\s*["\'](\d+)["\']', match.group(1))
        if len(ids) != len(names):
            return None

        course_map = dict(zip(names, ids))
        return course_map.get(course_name)

    @staticmethod
    def get_client_state_input_name(soup: BeautifulSoup):
        return soup.select_one(".RadComboBox > input").get("name")

    @staticmethod
    def get_form_id(soup: BeautifulSoup):
        return soup.select_one(".rcbInput").get("name")[:-9]

    @staticmethod
    def parse_earliest_hour(table: BeautifulSoup) -> datetime:
        return datetime.strptime(table.select_one(
            ".rsVerticalHeaderTable > tr:nth-child(1) > th:nth-child(1) > div:nth-child(1)").text.strip(), "%H:%M")

    @staticmethod
    def get_number_of_time_slots(table: BeautifulSoup) -> int:
        return len(table.select_one(".rsContentTable").select("table > tr"))

    @staticmethod
    def parse_lesson(slot: bs4.Tag, start: datetime, date: str) -> Lesson:
        new_lesson = Lesson()
        main = slot.select_one(".rsWrap > .rsApt")

        new_lesson_date = datetime.strptime(date, "%Y-%m-%d").date()
        new_lesson.start = start.replace(year=new_lesson_date.year, month=new_lesson_date.month,
                                         day=new_lesson_date.day)

        match = re.search(r'height:\s*([\d.]+)(px|%)?', main.get("style"))
        if match:
            height_value = int(match.group(1))
            time = math.ceil(height_value / TIME_SLOT_SIZE_PX)
        else:
            time = 1

        new_lesson.end = new_lesson.start + timedelta(minutes=time * 30)

        metadata = main.select_one(".rsAptOut > .rsAptMid > .rsAptIn > .rsAptContent")
        new_lesson.name = metadata.contents[0].get_text(strip=True)
        new_lesson.location = metadata.find('span').get_text(strip=True).strip('[]')
        new_lesson.shift = metadata.contents[3].get_text(strip=True)

        return new_lesson
