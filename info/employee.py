class employee:

    def __init__(self):
        self.employee_id = None
        self.first_name = None
        self.last_name = None
        self.employee_name = None
        self.email = None
        self.employee_image = None
        self.mobile_number = None
        self.aadhar_number = None
        self.designation = None
        self.image = None
        self.average_rating = None

    # def to_dict(self):
    #     return {
    #         "employee_id": self.employee_id,
    #         "first_name":self.first_name,
    #         "last_name":self.last_name,
    #         "employee_name":self.employee_name,
    #         "email": self.email,
    #         "mobile_number": self.mobile_number,
    #         "employee_image": self.employee_image,
    #         "designation":self.designation,
    #         "aadhar_number": self.aadhar_number,
    #         "average_rating": self.average_rating
    #     }
    def to_dict(self):
        emp = {}
        
        for attr_name, attr_value in vars(self).items():
            if attr_value is not None:
                emp[attr_name] = attr_value
        return emp