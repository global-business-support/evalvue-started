class response:

    def __init__(self):
        self.user_Id = None
        self.document_type = None
        self.listed_type = None
        self.sector_type=None
        self.organization_id=None
        self.is_verified=None
        self.is_user_register_successfull=None
        self.error=None
        self.is_login_successfully = None
        self.is_organization_created_successfully = None
        self.is_organizarion_view_page_rendered_successfully = None
        self.is_employee_added_successfully = None
        self.employee_id = None

    def convertToJSON(self):
        res = {}
        
        for attr_name, attr_value in vars(self).items():
            if attr_value is not None:
                res[attr_name] = attr_value
        return res
        # return vars(self)

