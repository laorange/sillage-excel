import datetime
import json
import math
from collections import namedtuple
from typing import Callable, Tuple
from urllib.parse import urlparse, parse_qs

import httpx

from .types import *

config = httpx.get("https://sillage.siae.top/api/collections/config/records").json()["items"][0]["content"]
semester_start_date = datetime.datetime.strptime(config["semesterStartDate"], "%Y-%m-%d")
dictionary = config["dictionary"]
max_week_num = config["maxWeekNum"]
semester_end_date = semester_start_date + datetime.timedelta(weeks=max_week_num)
print(f"{semester_start_date=}, {max_week_num=}, {semester_end_date=}")


class Course(PocketBaseModel):
    info: CourseInfo
    situations: List[Situation]
    grade: str

    dates: List[str]
    lessonNum: int

    note: Optional[str]
    method: Optional[str]

    def __str__(self):
        def decorateStr(s: str):
            return s + "\n" if s else ""

        courseStr = ""
        if self.info.name in dictionary:
            courseStr += decorateStr(dictionary[self.info.name][0])

        courseStr += decorateStr(self.info.name)
        courseStr += decorateStr(self.method)
        if len(self.situations) == 1:
            situ = self.situations[0]
            courseStr += "\n".join([item for item in [
                decorateStr("&".join(situ.groups) if situ.groups else "").strip(),
                decorateStr("&".join(situ.teachers) if situ.teachers else "").strip(),
                decorateStr("&".join(situ.rooms) if situ.rooms else "").strip()
            ] if item])
        elif len(self.situations) >= 2:
            courseStr += "\n".join([" ".join([item for item in [
                decorateStr("&".join(situ.groups) if situ.groups else "").strip(),
                decorateStr("&".join(situ.teachers) if situ.teachers else "").strip(),
                decorateStr("&".join(situ.rooms) if situ.rooms else "").strip()
            ] if item]) for situ in self.situations])
        courseStr += decorateStr(self.note)
        return courseStr.strip()


CourseFilter = Callable[[Course], bool]


def whether_two_list_have_same_element(list_a: List, list_b: List):
    return bool(len([a for a in list_a if a in list_b]))


class CourseDecorator:
    def __init__(self, source: Union[Course, List[Course]]):
        self.value: List[Course] = source if isinstance(source, list) else [source]

    def __getitem__(self, item):
        return self.value.__getitem__(item)

    def get_situ_items(self):
        teachers: List[str] = []
        groups: List[str] = []
        rooms: List[str] = []

        for course in self.value:
            for situation in course.situations:
                teachers.extend(situation.teachers)
                groups.extend(situation.groups)
                rooms.extend(situation.groups)
        SituItems = namedtuple("SituItems", ["teachers", "groups", "rooms"])
        return SituItems(list(set(teachers)), list(set(groups)), list(set(rooms)))

    def filter(self, filter_function: CourseFilter):
        return CourseDecorator(list(filter(filter_function, self.value)))

    def filter_grades(self, grades: List[str]):
        def courseFilter(c: Course) -> bool:
            return c.grade in grades

        return self.filter(courseFilter)

    def filter_of_lesson_num(self, lesson_number: int):
        def courseFilter(c: Course) -> bool:
            return c.lessonNum == lesson_number

        return self.filter(courseFilter)

    def filter_of_grade_groups(self, grade_groups: List[str]):
        grade_groups: List[Tuple[str, str]] = list(map(lambda gg: json.loads(gg), grade_groups))
        grades = list(map(lambda gg: gg[0], grade_groups))

        def courseFiler(c: Course) -> bool:
            for situation in c.situations:
                if len(situation.groups) == 0:
                    # 如果某节课没有指定“班级/小组”，则按年级，则符合条件
                    return True
                groups_of_this_grade = list(map(lambda gg: gg[1], filter(lambda gg: gg[0] == c.grade, grade_groups)))
                # 如果该课程的某 situation.groups 与需要的 groups 有重叠，则符合条件
                if whether_two_list_have_same_element(situation.groups, groups_of_this_grade):
                    return True
            return False

        return self.filter_grades(grades).filter(courseFiler)

    def filter_of_date(self, date: str):
        def courseFiler(c: Course) -> bool:
            return date in c.dates

        return self.filter(courseFiler)

    def filter_of_methods(self, methods: List[str]):
        def courseFiler(c: Course) -> bool:
            return c.method in methods

        return self.filter(courseFiler)

    def filter_of_teachers(self, teachers: List[str]):
        def courseFiler(c: Course) -> bool:
            teacher_list = CourseDecorator(c).get_situ_items().teachers
            return whether_two_list_have_same_element(teacher_list, teachers)

        return self.filter(courseFiler)

    def filter_of_course_names(self, course_names: List[str]):
        def courseFiler(c: Course) -> bool:
            return c.info.name in course_names

        return self.filter(courseFiler)

    def filter_of_rooms(self, rooms: List[str]):
        def courseFiler(c: Course) -> bool:
            room_list = CourseDecorator(c).get_situ_items().rooms
            return whether_two_list_have_same_element(room_list, rooms)

        return self.filter(courseFiler)

    def get_title(self):
        return "丨".join([f"{course.info.name}:"
                          f"{','.join(['-'.join([_ for _ in ['&'.join(situ.groups), '&'.join(situ.rooms)] if _]) for situ in course.situations])}"
                          for course in self.value])

    def __str__(self):
        lessonNumStrList: List[str] = []

        for lessonNum in range(1, 6):
            lessonNumStr = ""
            coursesOfLessonNum = self.filter_of_lesson_num(lessonNum).value
            if len(coursesOfLessonNum):
                # lessonNumStr += f"# 第 {lessonNum} 节课\n\n"
                lessonNumStr += "\n\n---\n\n".join([str(c) for c in coursesOfLessonNum])
                lessonNumStrList.append(lessonNumStr.strip())
        return f"\n\n---\n\n".join(lessonNumStrList)


class ApiHandler:
    base_url = 'https://sillage.siae.top/api/collections/course/records'
    max_per_page = 200
    courseDecorator: CourseDecorator

    def __init__(self):
        self.courseDecorator = self.getNewCourseDecorator()

    def getNewCourseDecorator(self):
        res = httpx.get(self.base_url, params=dict(page=1, perPage=1, sort="-updated"))
        totalItems = res.json()['totalItems']

        rawCourses = []
        for i in range(math.ceil(totalItems / 200)):
            res = httpx.get(self.base_url, params=dict(page=i + 1, perPage=self.max_per_page, sort="-updated"))
            items = res.json()['items']
            rawCourses += items

        return CourseDecorator([Course(**rawCourse) for rawCourse in rawCourses])

    def refreshCourses(self):
        self.courseDecorator = self.getNewCourseDecorator()

    def get_filtered_courses(self, url_with_filters: str):
        url_with_filters = url_with_filters.replace("#", "_")
        urlParseResult = urlparse(url_with_filters)
        queryParseResult = QueryParseResult(**parse_qs(urlParseResult.query))

        courseDecorator = self.courseDecorator
        courseDecorator = courseDecorator.filter_grades(queryParseResult.grade) if queryParseResult.grade else courseDecorator
        courseDecorator = courseDecorator.filter_of_rooms(queryParseResult.room) if queryParseResult.room else courseDecorator
        courseDecorator = courseDecorator.filter_of_methods(queryParseResult.method) if queryParseResult.method else courseDecorator
        courseDecorator = courseDecorator.filter_of_teachers(queryParseResult.teacher) if queryParseResult.teacher else courseDecorator
        courseDecorator = courseDecorator.filter_of_grade_groups(queryParseResult.group) if queryParseResult.group else courseDecorator
        courseDecorator = courseDecorator.filter_of_course_names(queryParseResult.subject) if queryParseResult.subject else courseDecorator

        return courseDecorator
