class response:

    def __init__(self):
        self.user_id = None
        self.email = None
        self.organization_id=None
        self.employee_id = None
        self.document_type = None
        self.listed_type = None
        self.sector_type=None
        self.country = None
        self.state = None
        self.city = None
        self.is_verified=None
        self.is_user_register_successfull=None
        self.error=None
        self.is_login_successfull = None
        self.is_employee_register_successfull = None
        self.employee_list = None
        self.review_list = None
        self.organization_list = None
        self.is_employee_mapped_to_organization_successfull = None
        self.is_review_added_successfull = None
        self.is_review_mapped_to_employee_successfull = None
        self.otp_send_successfull = None
        self.otp_verified_successfull = None
        self.password_updated_successFull = None
        self.otp_is_expired = None
        self.incorrect_otp = None
        self.is_organization_register_successfull = None
        self.is_organization_mapped = None
        self.is_organization_created_successfully = None
        self.is_email_verified_successfull = None
        self.is_user_verified = None

    def convertToJSON(self):
        res = {}
        
        for attr_name, attr_value in vars(self).items():
            if attr_value is not None:
                res[attr_name] = attr_value
        return res
        # return vars(self)

