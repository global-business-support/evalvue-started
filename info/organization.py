class organization:

    def __init__(self):
        self.organization_id = None
        self.name = None
        self.image = None
        self.sector_name = None
        self.listed_name = None
        self.country_name = None
        self.state_name = None
        self.city_name = None
        self.area = None
        self.pincode = None

    def to_dict(self):
        organization = {}
        for attr_name, attr_value in vars(self).items():
            if attr_value is not None:
                organization[attr_name] = attr_value
        return organization
