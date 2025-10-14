import json

from lesson import Lesson
from modules.base import BaseExportModule

class JsonExportModule(BaseExportModule):
    """
    The JSON export module supports the following config options:
        - file_name: Exported file name
        - indent: Pretty print the file with indentation (True/False)
    """

    file_name = "out.json"
    indent = False

    def __init__(self, config: dict):
        super().__init__()
        self.file_name = config["file_name"]
        self.indent = config["indent"]

    def export(self, lessons: list[Lesson]):
        print("Exporting to JSON...")
        with open(f"./export/{self.file_name}", "w") as f:
            f.write(json.dumps([lesson.to_dict() for lesson in lessons],
                               ensure_ascii=False,
                               indent=4 if self.indent else None))