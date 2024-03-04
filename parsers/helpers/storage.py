class Storage:
    def __init__(self):
            self.Categories = set()
            self.Cities = set()
            self.Events = set()
            self.Locations = set()

    def clear(self):
        self.Categories.clear()
        self.Cities.clear()
        self.Events.clear()
        self.Locations.clear()
