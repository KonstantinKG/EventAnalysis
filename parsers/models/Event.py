import datetime


class Event:
    def __init__(
        self,
        id,
        src_id,
        title,
        photo,
        short_description,
        description,
        phone,
        link,
        start,
        end,
        location_id,
        source_id,
        city_id,
        url,
        ticket_url,
        category_id
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
        self.start = start
        self.end = end
        self.ticket_url = ticket_url
        self.category_id = category_id
        self.relevance = str(datetime.datetime.now())
