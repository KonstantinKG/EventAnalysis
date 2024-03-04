class Event:
    def __init__(
            self,
            id=None,
            src_id=None,
            title=None,
            photo=None,
            short_description=None,
            description=None,
            phone=None,
            link=None,
            location_id=None,
            source_id=None,
            city_id=None,
            url=None,
            ticket_url=None,
            category_id=None
    ):
        self.id = id
        self.src_id = src_id
        self.title = title
        self.photo = photo
        self.description = description
        self.short_description = short_description
        self.phone = phone
        self.link = link
        self.location_id = location_id
        self.source_id = source_id
        self.city_id = city_id
        self.url = url
        self.ticket_url = ticket_url
        self.category_id = category_id
