class employee:

    def __init__(self):
        self.employee_id = None
        self.employee_name = None
        self.email = None
        self.employee_image = None
        self.mobile_number = None
        self.aadhar_number = None
        self.designation = None
        self.image = None
        self.average_rating = None

    def to_dict(self):
        return {
            "employee_id": self.employee_id,
            "name": self.employee_name,
            "email": self.email,
            "mobile_number": self.mobile_number,
            "image": self.employee_image,
            "designation":self.designation,
            "aadhar_number": self.aadhar_number,
            "average_rating": self.average_rating

        }
    # def convertToJSON(self):
    #     emp = {}
        
    #     for attr_name, attr_value in vars(self).items():
    #         if attr_value is not None:
    #             emp[attr_name] = attr_value
    #     return emp