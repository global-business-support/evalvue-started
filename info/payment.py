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
        self.organization_name = None
        self.plan_id = None
        self.start_date = None
        self.end_date = None
        self.next_due_date = None
        self.status = None
        self.organization_name = None
        self.amount = None
        self.razorpay_order_id = None
        self.transaction_id = None
        self.payment_mode = None
        self.organization_name = None
        self.amount= None

        self.org_name = None
        self.order_id = None
        self.amount = None
        self.created_on = None
        self.transaction_id = None

    def to_dict(self):
        pay = {}
        for attr_name, attr_value in vars(self).items():
            if attr_value is not None:
                pay[attr_name] = attr_value
        return pay