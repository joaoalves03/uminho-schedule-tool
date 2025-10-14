class Lesson:
    name = ""
    location = None
    shift = None
    start = None
    end = None

    def __str__(self):
        return (f"{self.name}\n"
                f"\tShift: {self.shift}\n"
                f"\tStart: {self.start}\n"
                f"\tEnd: {self.end}\n"
                f"\tLocation: {self.location}\n")