import streamlit as st
from streamlit_option_menu import option_menu
from streamlit import write
import streamlit_authenticator as stauth

from datetime import datetime
import time
import openpyxl

import pandas as pd
from deta import Deta

import database as db
import fuzzyMamdani as fz

import math


page_title = "Rekomendasi Merek Masker"
page_icon = ":money_with_wings:"
layout = "centered"

file_path = 'tamplate.xlsx'


st.set_page_config(page_title=page_title,
                   page_icon=page_icon, layout=layout)

# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
                <style>
                # MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)

# button_style = """
#             <style>
#             .btn-submit {
#                 background-color: green;
#                 color: white;
#                 border-radius: 5px;
#                 padding: 0.5rem 1rem;
#                 margin-right: 1rem;
#                 border: none;
#             }
#             .btn-delete {
#                 background-color: red;
#                 color: white;
#                 border-radius: 5px;
#                 padding: 0.5rem 1rem;
#                 border: none;
#             }
#             </style>
#              """
# st.markdown(button_style, unsafe_allow_html=True)

# ================================================ akhir style

users = db.fetch_all_users()

usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
                                    "rekomendasi_dashboard", "12345678", cookie_expiry_days=15)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    st.title(page_title + " " + page_icon)
    authenticator.logout("Logout", "main")

    # --- NAVIGATION MENU ---
    selected = option_menu(
        menu_title=None,
        options=["Upload Data", "Rekomendasi"],
        # https://icons.getbootstrap.com/
        icons=["pencil-fill", "bar-chart-fill"],
        orientation="horizontal",
    )

    # Schedule the delete_old_data function to run every 2 weeks
    # deta.cron.schedule(delete_old_data, "0 0 */2 * *")
    # deta.cron.schedule(delete_old_data, "0 0 * * *")

    # input data
    if selected == "Upload Data":
        st.header(f"Upload File")

        def file_download_link(file_path, file_name):
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            st.download_button(
                label='Download Tamplate', data=file_bytes, file_name=file_name)

        # Memanggil fungsi download button
        file_path = 'tamplate.xlsx'
        file_name = 'tamplate.xlsx'
        file_download_link(file_path, file_name)

        with st.form("entry_from"):
            data = st.file_uploader(
                "Upload File Excel Sesuai Dengan Tamplate", type=["xlsx"])

            if data:
                # Buka file Excel dengan openpyxl
                wb = openpyxl.load_workbook(data)
                # Cek apakah sheet "Hasil" ada dalam file Excel
                if "Hasil" not in wb.sheetnames:
                    data = "Salah"
                else:
                    # Tampilkan tampilan loading ketika file di-upload
                    with st.spinner("Uploading file..."):
                        df = pd.read_excel(data, sheet_name="Hasil")
                        time.sleep(2)

            submitted = st.form_submit_button("Simpan Data")

            # Jika tombol "Simpan Data" diklik
            if submitted:
                # Jika file belum di-upload
                if not data:
                    st.warning(
                        "Silakan upload file Excel terlebih dahulu. Pastikan Sesuai Dengan Tamplate")
                elif data == "Salah":
                    st.warning(
                        "File Yang Anda Upload Tidak Sesuai Tamplate. Pastikan file yang diupload sesuai dengan template.")
                else:
                    # Tampilkan tampilan loading ketika data di-push ke database
                    with st.spinner("Menyimpan Data, Harap Bersabar..."):
                        # Tambahkan kolom tanggal upload
                        df["tanggal_upload"] = datetime.now().strftime(
                            # "%Y-%m-%d")
                            "%Y-%m-%d %H:%M:%S")
                        # Push data ke database
                        for index, row in df.iterrows():
                            # db.put({
                            #     "merek": row["merek"],
                            #     "stock": row["stock"],
                            #     "total_penjualan": row["total_penjualan"],
                            #     "total_pendapatan": row["total_pendapatan"],
                            #     "tanggal_upload": row["tanggal_upload"]
                            # })
                            db.insert_period(row["merek"], row["stock"], row["total_penjualan"],
                                             row["total_pendapatan"], row["tanggal_upload"])
                            time.sleep(0.5)
                    st.success("Data berhasil diupload ke database Deta.sh")

    if selected == "Rekomendasi":
        st.header(f"Hasil Rekomendasi")
        with st.form("saved_periods"):
            period = st.selectbox("Select Waktu Upload :",
                                  db.fetch_all_tanggal_upload())
            submitted = st.form_submit_button(
                "Dapatkan Rekomendasi")
            deleted = st.form_submit_button(
                "Hapus Data")
            if deleted:
                with st.spinner("Sedang Menghapus Data"):
                    db.delete_data_by_date(period)
                    st.success(
                        f"All data for upload date {period} has been deleted.")
            if submitted:
                with st.spinner("Sedang menghitung..."):
                    period_data = db.fetch_periods_by_date(period)
                    for record in period_data:
                        stock = record['stock']
                        total_penjualan = record['total_penjualan']
                        total_pendapatan = record['total_pendapatan']
                        priority, quantity = fz.fuzzyMamdani(
                            stock, total_penjualan, total_pendapatan)

                        record['priority'] = priority
                        # membulatkan nilai quantity ke atas
                        record['quantity'] = math.ceil(quantity)

                    # for record in period_data:
                    #     st.write(record)

                    # ============== 2
                    # sorted_data = sorted(
                    #     period_data, key=lambda k: k['priority'], reverse=True)

                    # # Printing the data in a table
                    # st.write('Merek \t Quantity')
                    # for record in sorted_data:
                    #     st.write(f"{record['merek']} \t {int(record['quantity'])}")

                    # ============= 3
                    # Tampilkan data hasil fuzzy Mamdani
                    st.write("Hasil rekomendasi: ")

                    # Urutkan data berdasarkan nilai priority
                    sorted_data = sorted(
                        period_data, key=lambda x: x['priority'], reverse=True)

                    # Tampilkan data dalam bentuk list
                    for i, record in enumerate(sorted_data):
                        no = i+1
                        merek = record['merek']
                        quantity = record['quantity']
                        priority = record['priority']
                        st.write(
                            f"{no}. | {merek} | {quantity:.0f} | {priority:.2f}")
