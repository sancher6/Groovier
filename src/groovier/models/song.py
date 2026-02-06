class Song:
    def __init__(self, url, title, duration, thumbnail, requester):
        self.url = url
        self.title = title
        self.duration = duration
        self.thumbnail = thumbnail
        self.requester = requester

    def to_dict(self):
        return {
            'url': self.url,
            'title': self.title,
            'duration': self.duration,
            'thumbnail': self.thumbnail,
            'requester': self.requester
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['url'],
            data['title'],
            data['duration'],
            data['thumbnail'],
            data['requester']
        )