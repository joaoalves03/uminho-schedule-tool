from pathlib import Path

from lesson import Lesson


class BaseExportModule:
    def __init__(self):
        Path("./export").mkdir(parents=True, exist_ok=True)

    def export(self, lessons: list[Lesson]):
        pass