import datetime


class Lesson:
    name = ""
    location = ""
    shift = ""
    start: None | datetime.datetime = None
    end: None | datetime.datetime = None

    def __str__(self):
        return (f"{self.name}\n"
                f"\tShift: {self.shift}\n"
                f"\tStart: {self.start}\n"
                f"\tEnd: {self.end}\n"
                f"\tLocation: {self.location}\n")

    def to_dict(self):
        return {
            "name": self.name,
            "location": self.location,
            "shift": self.shift,
            "start": self.start.strftime("%Y-%m-%d %H:%M:%S"),
            "end": self.end.strftime("%Y-%m-%d %H:%M:%S")
        }