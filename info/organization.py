class organization:

    def __init__(self):
        self.organization_id = None
        self.name = None
        self.image = None
        self.document_name = None
        self.sector_name = None
        self.listed_name = None
        self.country_name = None
        self.state_name = None
        self.city_name = None
        self.area = None
        self.pincode = None
        self.document_number = None
        self.organization_verified = None
        self.organization_name = None
        self.organization_image = None
        self.sector_id = None
        self.listed_id = None
        self.country_id = None
        self.state_id = None
        self.city_id = None
        self.number_of_employee = None
        self.document_type_id = None
        self.document_file = None
        self.date_time = None
        self.gstin = None

    def to_dict(self):
        organization = {}
        for attr_name, attr_value in vars(self).items():
            if attr_value is not None:
                organization[attr_name] = attr_value
        return organization
