import datetime
from deta import Deta

DETA_KEY = "c0gxjy11k58_1LNFR6YDq8M1Ptm267jymu1Eau95ELjc"


deta = Deta(DETA_KEY)

db_transaksi = deta.Base("coba")
db_user = deta.Base("user")

# =============================== login


def insert_user(username, name, password):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return db_user.put({"key": username, "name": name, "password": password})


# insert_user("muh_asmann", "Muhammad Asman", "12345678")

def fetch_all_users():
    """Returns a dict of all users"""
    res = db_user.fetch()
    return res.items


# print(fetch_all_users())

def get_user(username):
    """If not found, the function will return none"""
    return db_user.get(username)


def update_user(username, updates):
    """If the item is updated, returns None. Otherwise, an exception is raised"""
    return db_user.update(updates, username)


def delete_user(username):
    """Always returns None, even if the key does not exist"""
    return db_user.delete(username)


# ======================================= upload produk


def insert_period(merek, stock, total_penjualan, total_pendapatan, tanggal_upload):
    """Returns the report on a successful creation, otherwise raises an error"""
    return db_transaksi.put({"merek": merek, "stock": stock, "total_penjualan": total_penjualan, "total_pendapatan": total_pendapatan, "tanggal_upload": tanggal_upload})


# def fetch_all_periods():
#     """Returns a dict of all periods"""
#     res = db_transaksi.fetch()
#     return res.items

def fetch_all_tanggal_upload():
    """Returns a list of all unique values in the tanggal_upload column"""
    all_data = db_transaksi.fetch().items
    unique_tanggal_upload = list(
        set([item['tanggal_upload'] for item in all_data]))
    return unique_tanggal_upload


# def fetch_all_periods():
#     """Returns a dict of all periods"""
#     res = db_transaksi.fetch()
#     res_dict = {item["tanggal_upload"]: item for item in res.items()}
#     # Group the data by upload date
#     periods = {}
#     for item in res_dict:
#         tanggal_upload = item["tanggal_upload"]
#         if tanggal_upload in periods:
#             periods[tanggal_upload].append(item)
#         else:
#             periods[tanggal_upload] = [item]
#     return periods.tanggal_upload


def fetch_periods_by_date(tanggal_upload):
    """Returns a list of all periods with the specified upload date"""
    all_data = db_transaksi.fetch().items
    filtered_data = [
        item for item in all_data if item['tanggal_upload'] == tanggal_upload]
    return filtered_data

# def get_period(period):
#     """If not found, the function will return None"""
#     return db_transaksi.get(period)


# def delete_old_data():
#     # Get the current datetime
#     now = datetime.datetime.now()

#     # Calculate the datetime 2 weeks ago
#     two_weeks_ago = now - datetime.timedelta(weeks=2)

#     # Fetch all data older than 2 weeks
#     old_data = db_transaksi.fetch(
#         {"tanggal_upload": {"$lt": two_weeks_ago.strftime("%Y-%m-%d %H:%M:%S")}})

#     # Delete the old data
#     for item in old_data.items:
#         db_transaksi.delete(item["key"])

# def delete_old_data():
#     # Get the current datetime
#     now = datetime.datetime.now()

#     # Calculate the datetime 2 days ago
#     two_days_ago = now - datetime.timedelta(days=2)

#     # Fetch all data older than 2 days
#     old_data = db_transaksi.fetch(
#         {"tanggal_upload": {"$lt": two_days_ago.strftime("%Y-%m-%d %H:%M:%S")}})

#     # Delete the old data
#     for item in old_data.items:
#         db_transaksi.delete(item["key"])

def delete_data_by_date(tanggal_upload):
    """Deletes all data with the specified tanggal_upload"""
    data = db_transaksi.fetch({"tanggal_upload": tanggal_upload})
    for item in data.items:
        db_transaksi.delete(item["key"])
