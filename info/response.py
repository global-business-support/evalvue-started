class response:

    def __init__(self):
        self.user_id = None
        self.user_name = None
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
        self.dashboard_list = None
        self.is_employee_mapped_to_organization_successfull = None
        self.is_review_added_successfull = None
        self.is_review_mapped_to_employee_successfull = None
        self.otp_send_successfull = None
        self.review_email_send_successfull = None
        self.otp_verified_successfull = None
        self.password_updated_successFull = None
        self.otp_is_expired = None
        self.incorrect_otp = None
        self.is_organization_register_successfull = None
        self.is_organization_mapped = None
        self.is_organization_created_successfull = None
        self.is_email_verified_successfull = None
        self.is_user_verified = None
        self.is_review_mapped = None
        self.employees_list_by_aadhar = None
        self.employees_mapped_to_aadhar = None
        self.top_employee = None
        self.is_top_employee = None
        self.employee_edit_sucessfull = None
        self.organization_edit_sucessfull = None
        self.organization_is_verified = None
        self.organization_verification = None
        self.is_document_verification_data_successfull = None
        self.is_organization_verified_successfull = None
        self.is_organization_rejected_successfull = None
        self.is_user_verified_successfull = None
        self.organizations_paid_count = None

        
        self.refresh = None
        self.employee_editable_data_send_successfull = None
        self.organization_editable_data_send_succesfull = None
        self.is_employee_terminated_successfull = None 
        self.is_terminated_employee_added_successfull = None

        self.subscription_response_list = None
        self.is_subscription_id_created_successfull = None
        self.is_subscription_id_already_exist = None
        self.payment_response_list = None
        self.is_payment_response_sent_succefull = None
        self.is_organization_reapplied_successfull = None

        self.subscription_history_data = None
        self.is_subscription_history_data_sent_successfull = None
        self.no_data_found = None
        self.generate_reciept_data = None
        self.is_generate_reciept_data_send_successfull = None
        self.generate_reciept_data = None
        self.payment_history_list = None
        self.is_payment_history_sent_successfull = None
        self.is_payment_already_done = None
        self.payment_error = None
        self.employee_data_inserted_successfull = None
        self.is_access_token_sent_successfull = None

    def convertToJSON(self):
        res = {}
        for attr_name, attr_value in vars(self).items():
            if attr_value is not None:
                res[attr_name] = attr_value
        return res
