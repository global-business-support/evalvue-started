class payment:

    def __init__(self):
        self.subscription_id = None
        self.razor_pay_status = None
        self.subscriptionLink = None

    def to_dict(self):
        pay = {}
        
        for attr_name, attr_value in vars(self).items():
            if attr_value is not None:
                pay[attr_name] = attr_value
        return pay