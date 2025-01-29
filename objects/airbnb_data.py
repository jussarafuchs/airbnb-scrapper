from datetime import datetime


class Airbnb_Data:
    def __init__(self, _id=None, airbnbId=None, title=None, name=None, subname=None, price=None, originalPrice=None, url=None, rating=None, reviews=None, location=None, creationDate=None, ownerName=None, type=None, city=None):
        self._id = _id
        self.airbnbId = airbnbId
        self.title = title
        self.name = name
        self.subname = subname
        self.price = price
        self.originalPrice = originalPrice
        self.url = url
        self.rating = rating
        self.reviews = reviews
        self.location = location
        self.creationDate = creationDate
        self.ownerName = ownerName
        self.type = type
        self.city = city

    @classmethod
    def from_dict(cls, data):
        try:
            return cls(
                _id=data.get("_id"),
                airbnbId=data.get("airbnbId"),
                title=data.get("title"),
                name=data.get("name"),
                subname=data.get("subname"),
                price=data.get("price"),
                originalPrice=data.get("originalPrice"),
                url=data.get("url"),
                rating=data.get("rating"),
                reviews=data.get("reviews"),
                location=data.get("location"),
                creationDate=data.get("creationDate"),
                ownerName=data.get("ownerName"),
                type=data.get("type"),
                city=data.get("city")
            )
        except Exception as e:
            print(str(e))

    def to_vars(self):
        return vars(self)
