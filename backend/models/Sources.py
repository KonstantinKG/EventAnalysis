from models import Source


class Sources:
    def __init__(self):
        self.value = dict(
            sxodim=Source(id=1, name='Sxodim.com', slug='sxodim')
        )
