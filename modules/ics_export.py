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

    @staticmethod
    def lesson_key(l: Lesson):
        return (
            l.name,
            l.shift,
            l.location,
            l.start.astimezone(timezone.utc),
            l.end.astimezone(timezone.utc),
        )

    def export(self, lessons: list[Lesson]):
        print("Exporting to ICS...")

        if self.override_file:
            with open(self.override_file) as f:
                calendar = ics.Calendar(f.read())
        else:
            calendar = ics.Calendar()

        new_lessons = {self.lesson_key(l): l for l in lessons}

        existing_events = {
            (
                e.name,
                e.description,
                e.location,
                e.begin.astimezone(timezone.utc),
                e.end.astimezone(timezone.utc),
            ): e
            for e in calendar.events
        }

        keep_keys = set(existing_events.keys()) & set(new_lessons.keys())
        add_keys = set(new_lessons.keys()) - set(existing_events.keys())

        updated_events = {k: existing_events[k] for k in keep_keys}

        for k in add_keys:
            l = new_lessons[k]
            event = ics.Event(
                name=l.name,
                description=l.shift,
                location=l.location,
                begin=l.start.astimezone(timezone.utc),
                end=l.end.astimezone(timezone.utc),
            )
            updated_events[k] = event

        calendar.events = set(updated_events.values())

        output_file = self.override_file if self.override_file else self.file_name
        with open(output_file, "w") as f:
            f.writelines(calendar.serialize_iter())