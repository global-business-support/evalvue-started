class payment:

    def __init__(self):
        self.subscription_id = None
        self.razor_pay_status = None
        self.subscriptionLink = None
        self.payment_status = None
        self.payment_cancelled = None
        self.error_description = None
        self.error_source = None
        self.error_step = None
        self.transaction = None

    def to_dict(self):
        pay = {}
        
        for attr_name, attr_value in vars(self).items():
            if attr_value is not None:
                pay[attr_name] = attr_value
        return pay