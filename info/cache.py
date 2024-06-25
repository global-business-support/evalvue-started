from django.core.cache import cache
from django.db import connection



user_data = {}
def fetch_user_data_from_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT Email, Password FROM [User]")
        columns = []
        for col in cursor.description:
            columns.append(col[0])
        
        rows = cursor.fetchall()
        for row in rows:
            row_dict = {}
            for idx, value in enumerate(row):
                row_dict[columns[idx]] = value
            user_data[row[0]] = row_dict
        # print(user_data)
def get_cached_user_data():
    return user_data
def refresh_cached_user_data():
    fetch_user_data_from_db()


organization_data = {}
def fetch_organization_data_from_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT OrganizationId, Name, DocumentTypeId, DocumentNumber, DocumentFile, SectorId, ListedId, Image, NumberOfEmployee, CountryId, StateId, CityId, CreatedOn FROM Organization")
        columns = []
        for col in cursor.description:
            columns.append(col[0])
        rows = cursor.fetchall()
        for row in rows:
            row_dict = {}
            for idx, value in enumerate(row):
                row_dict[columns[idx]] = value
            organization_data[row[0]] = row_dict
        # print(organization_data)
def get_cached_organization_data():
    return organization_data
def refresh_organization_data():
    fetch_organization_data_from_db()


document_type_data = {}
def fetch_document_type_data_from_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT DocumentTypeId,Name FROM DocumentType")
        columns = []
        for col in cursor.description:
            columns.append(col[0])
        rows = cursor.fetchall()
        for row in rows:
            row_dict = {}
            for idx, value in enumerate(row):
                row_dict[columns[idx]] = value
            document_type_data[row[0]] = row_dict
        # print(document_type_data)
def get_cached_document_type_data():
    return document_type_data
def refresh_document_type_data():
    fetch_document_type_data_from_db()

listed_type_data = {}
def fetch_listed_type_data_from_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT ListedTypeId,Name FROM ListedType")
        columns = []
        for col in cursor.description:
            columns.append(col[0])
        rows = cursor.fetchall()
        for row in rows:
            row_dict = {}
            for idx, value in enumerate(row):
                row_dict[columns[idx]] = value
            listed_type_data[row[0]] = row_dict
        # print(listed_type_data)
def get_cached_listed_type_data():
    return listed_type_data
def refresh_listed_type_data():
    fetch_listed_type_data_from_db()


sector_type_data = {}
def fetch_sector_type_data_from_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT SectorTypeId,Name FROM SectorType")
        columns = []
        for col in cursor.description:
            columns.append(col[0])
        rows = cursor.fetchall()
        for row in rows:
            row_dict = {}
            for idx, value in enumerate(row):
                row_dict[columns[idx]] = value
            sector_type_data[row[0]] = row_dict
        # print(sector_type_data)
def get_cached_sector_type_data():
    return sector_type_data
def refresh_sector_type_data():
    fetch_sector_type_data_from_db()



country_data = {}
def fetch_country_data_from_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT CountryId,Name,MobileNumberCode,Currency from Country")
        columns = []
        for col in cursor.description:
            columns.append(col[0])
        rows = cursor.fetchall()
        for row in rows:
            row_dict = {}
            for idx, value in enumerate(row):
                row_dict[columns[idx]] = value
            country_data[row[0]] = row_dict
        # print(country_data)
def get_cached_country_data():
    return country_data
def refresh_country_data():
    get_cached_country_data()



state_data = {}
def fetch_state_data_from_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT StateId,Name,CountryId from State")
        columns = []
        for col in cursor.description:
            columns.append(col[0])
        rows = cursor.fetchall()
        for row in rows:
            row_dict = {}
            for idx, value in enumerate(row):
                row_dict[columns[idx]] = value
            state_data[row[0]] = row_dict
        # print(state_data)
def get_cached_state_data():
    return state_data
def refresh_state_data():
    get_cached_state_data()



city_data = {}
def fetch_city_data_from_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT CityId,Name,StateId from City")
        columns = []
        for col in cursor.description:
            columns.append(col[0])
        rows = cursor.fetchall()
        for row in rows:
            row_dict = {}
            for idx, value in enumerate(row):
                row_dict[columns[idx]] = value
            city_data[row[0]] = row_dict
        # print(city_data)
def get_cached_city_data():
    return city_data
def refresh_city_data():
    get_cached_city_data()




user_organization_mapping_data = {}
def fetch_user_organization_mapping_data_from_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT UserId, OrganizationId, IsVerified FROM UserOrganizationMapping")
        user_organization_data = cursor.fetchall()
        for user_id, org_id, is_verified in user_organization_data:
            if user_id not in user_organization_mapping_data:
                user_organization_mapping_data[user_id] = []
            user_organization_mapping_data[user_id].append({
                "OrganizationId": org_id,
                "Is_Verified": is_verified
            })
        # print(user_organization_mapping_data)
def get_cached_user_organization_mapping_data():
    return user_organization_mapping_data
def refresh_cached_user_organization_mapping_data():
    fetch_user_organization_mapping_data_from_db()


employee_data = {}
def fetch_employee_data_from_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT EmployeeId, Name, Email, MobileNumber, Image, AadharNumber, CreatedOn, ModifiedOn FROM Employee")
        columns = []
        for col in cursor.description:
            columns.append(col[0])
        rows = cursor.fetchall()
        for row in rows:
            row_dict = {}
            for idx, value in enumerate(row):
                row_dict[columns[idx]] = value
            employee_data[row[0]] = row_dict 
        # print(employee_data)
def get_cached_employee_data():
    return employee_data
def refresh_employee_data():
    fetch_employee_data_from_db()


employee_organization_mapping_data = {}
def fetch_employee_organization_mapping_data_from_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT EmployeeId,OrganizationId , StatusId FROM EmployeeOrganizationMapping")
        employee_organization_data = cursor.fetchall()
        for emp_id, org_id, status_id in employee_organization_data:
            if org_id not in employee_organization_mapping_data:
                employee_organization_mapping_data[org_id] = []
            employee_organization_mapping_data[org_id].append({
                "EmployeeId": emp_id,
                "StatusId": status_id
            })
        # print(employee_organization_mapping_data)
def get_cached_employee_organization_mapping_data():
    return employee_organization_mapping_data
def refresh_cached_employee_organization_mapping_data():
    fetch_employee_organization_mapping_data_from_db()

status_data = {}
def fetch_status_data_from_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT StatusId, Name FROM Status")
        columns = []
        for col in cursor.description:
            columns.append(col[0])
        rows = cursor.fetchall()
        for row in rows:
            row_dict = {}
            for idx, value in enumerate(row):
                row_dict[columns[idx]] = value
            status_data[row[0]] = row_dict 
        # print(status_data)
def get_cached_status_data():
    return status_data
def refresh_status_data():
    fetch_status_data_from_db()


review_data = {}
def fetch_review_data_from_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT ReviewId, Comment, Image, Rating FROM Review")
        columns = []
        for col in cursor.description:
            columns.append(col[0])
        rows = cursor.fetchall()
        for row in rows:
            row_dict = {}
            for idx, value in enumerate(row):
                row_dict[columns[idx]] = value
            review_data[row[0]] = row_dict 
        # print(review_data)
def get_cached_review_data():
    return review_data
def refresh_review_data():
    fetch_review_data_from_db()

referral_codes_data={}
def fetch_referral_codes_data_from_db():
    with connection.cursor() as cursor:
        cursor.execute("SELECT ReferralCode,ReferralName From Referral")
        referral_data = cursor.fetchall()
        for ReferralCode,ReferralName in referral_data:
            referral_codes_data[ReferralCode] = ReferralName
        print(referral_codes_data)
def get_cached_referral_codes_data():
    return referral_codes_data
def refresh_referral_codes_data():
    fetch_referral_codes_data_from_db







 











    

