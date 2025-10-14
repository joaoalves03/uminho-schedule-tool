from datetime import timezone

import ics

from lesson import Lesson
from modules.base import BaseExportModule

class IcsExportModule(BaseExportModule):
    """
    The ICS export module supports the following config options:
        - file_name: Exported file name
    """

    file_name = "out.ics"

    def __init__(self, config: dict):
        super().__init__()
        self.file_name = config["file_name"]

    def export(self, lessons: list[Lesson]):
        print("Exporting to ICS...")

        calendar = ics.Calendar()

        for lesson in lessons:
            event = ics.Event(
                name=lesson.name,
                description=lesson.shift,
                location=lesson.location,
                begin=lesson.start.astimezone(timezone.utc),
                end=lesson.end.astimezone(timezone.utc)
            )

            calendar.events.add(event)

        with open(f"./export/{self.file_name}", "w") as f:
            f.writelines(calendar.serialize_iter())