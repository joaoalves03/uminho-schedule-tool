from datetime import timezone

import ics

from lesson import Lesson
from modules.base import BaseExportModule

class IcsExportModule(BaseExportModule):
    """
    The ICS export module supports the following config options:
        - file_name: Exported file name
        - override_file: Replace data on existing ICS file (useful for updating a single day/week)
    """

    file_name = "./export/out.ics"
    override_file = None

    def __init__(self, config: dict):
        super().__init__()
        self.file_name = config["file_name"]
        self.override_file = config["override_file"]

    def export(self, lessons: list[Lesson]):
        print("Exporting to ICS...")

        if self.override_file:
            with open(self.override_file) as f:
                calendar = ics.Calendar(f.read())
                days = list(set(map(lambda l: l.start.strftime('%Y-%m-%d'), lessons)))
                calendar.events = set([e for e in calendar.events if str(e.begin).split("T")[0] not in days])
        else:
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

        with open(self.override_file if self.override_file else self.file_name, "w") as f:
            f.writelines(calendar.serialize_iter())