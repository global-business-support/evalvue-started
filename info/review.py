class review:

    def __init__(self):
        self.review_id = None
        self.comment = None
        self.image = None
        self.rating = None

    def to_dict(self):
        return {
            "review_id": self.review_id,
            "comment": self.comment,
            "image": self.image,
            "rating": self.rating
        }
    def convertToJSON(self):
        rev = {}
        
        for attr_name, attr_value in vars(self).items():
            if attr_value is not None:
                rev[attr_name] = attr_value
        return rev