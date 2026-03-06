import streamlit as st
import pandas as pd
from streamlit_qrcode_scanner import qrcode_scanner

file = "attendees.xlsx"

# قراءة الشيت
data = pd.read_excel(file)

# لو عمود Attended مش موجود نضيفه
if "Attended" not in data.columns:
    data["Attended"] = ""

st.title("Iftar Check-in System")

# اختيار طريقة الإدخال
option = st.radio(
    "Choose Check-in Method",
    ["Scan QR Code", "Search by Ticket ID"]
)

ticket = None

# Scan بالكاميرا
if option == "Scan QR Code":
    ticket = qrcode_scanner("Scan QR Code")

# البحث اليدوي
if option == "Search by Ticket ID":
    ticket = st.text_input("Enter Ticket ID")

if ticket:

    ticket = str(ticket).strip()

    person = data[data["Ticket_ID"].astype(str).str.strip() == ticket]

    if person.empty:
        st.error("INVALID TICKET ❌")

    else:

        idx = person.index[0]

        name = data.loc[idx, "Name"]
        email = data.loc[idx, "Email"]
        ticket_id = data.loc[idx, "Ticket_ID"]

        if data.loc[idx, "Attended"] == "YES":

            st.warning("ALREADY CHECKED ⚠️")

            st.write("Name:", name)
            st.write("Email:", email)
            st.write("Ticket ID:", ticket_id)

        else:

            data.loc[idx, "Attended"] = "YES"

            data.to_excel(file, index=False)

            st.success("APPROVED ✅")

            st.write("Name:", name)
            st.write("Email:", email)
            st.write("Ticket ID:", ticket_id)
