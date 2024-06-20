class aadhar:

    def __init__(self):
        self.employee_id = None
        self.employee_name = None
        self.email = None
        self.employee_image = None
        self.mobile_number = None
        self.aadhar_number = None
        self.designation = None
        self.created_on = None
        self.status_id = None
        self.organization_id = None
        self.organization_name = None
        self.organization_image = None

    def to_dict(self):
        employees = {}
        for attr_name, attr_value in vars(self).items():
            if attr_value is not None:
                employees[attr_name] = attr_value
        return employees
