from datetime import datetime

class Location:
    def __init__(self, _id=None, airbnbId=None, url=None, location=None, ownerName=None, type=None, typeCompleteDescription=None):
        self._id = _id
        self.airbnbId = airbnbId
        self.url = url
        self.location = location
        self.ownerName = ownerName
        self.type = type
        self.typeCompleteDescription = typeCompleteDescription

    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data.get("_id"),
            airbnbId=data.get("airbnbId"),
            url=data.get("url"),
            location=data.get("location"),
            ownerName=data.get("ownerName"),
            type=data.get("type"),
            typeCompleteDescription=data.get("typeCompleteDescription")
        )
        
    
    def to_vars(self):
        return vars(self)