import streamlit as st
import pandas as pd
from streamlit_qrcode_scanner import qrcode_scanner

file = "attendees.xlsx"

data = pd.read_excel(file)

st.title("Iftar Check-in System")

# اختيار طريقة الإدخال
option = st.radio(
    "Choose Check-in Method",
    ["Scan QR Code", "Search by Ticket ID"]
)

ticket = None

# الخيار الأول: الكاميرا
if option == "Scan QR Code":
    ticket = qrcode_scanner("Scan QR Code")

# الخيار الثاني: البحث اليدوي
if option == "Search by Ticket ID":
    ticket = st.text_input("Enter Ticket ID")

if ticket:

    person = data[data["Ticket_ID"] == ticket]

    if person.empty:
        st.error("INVALID TICKET ❌")

    else:

        idx = person.index[0]

        if data.loc[idx, "Attended"] == "YES":

            st.warning("ALREADY CHECKED ⚠️")

            st.write(person)

        else:

            data.loc[idx, "Attended"] = "YES"

            data.to_excel(file, index=False)

            st.success("APPROVED ✅")

            st.write(person)
