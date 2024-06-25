from django.apps import AppConfig
from django.apps import AppConfig
from django.core.cache import cache


from .cache import *  # Adjust the import according to your structure

class MyAppConfig(AppConfig):
    name = 'info'
    def ready(self):
        fetch_sector_type_data_from_db()
        fetch_listed_type_data_from_db()
        fetch_document_type_data_from_db()
        fetch_organization_data_from_db()
        fetch_user_organization_mapping_data_from_db()
        fetch_user_data_from_db()
        fetch_employee_data_from_db()
        fetch_document_type_data_from_db()
        fetch_country_data_from_db()
        fetch_state_data_from_db()
        fetch_city_data_from_db()
        fetch_employee_organization_mapping_data_from_db()
        fetch_status_data_from_db()
        fetch_review_data_from_db()
        fetch_referral_codes_data_from_db()

        

        

