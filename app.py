import streamlit as st
import pandas as pd
from streamlit_qrcode_scanner import qrcode_scanner
from io import BytesIO

file = "attendees.xlsx"

data = pd.read_excel(file)

if "Attended" not in data.columns:
    data["Attended"] = ""

st.title("🎟️ Iftar Check-in System")

# التحكم في الصفحة
if "page" not in st.session_state:
    st.session_state.page = "home"


# زر الرجوع
def go_home():
    st.session_state.page = "home"


# الصفحة الرئيسية
if st.session_state.page == "home":

    option = st.radio(
        "Choose Check-in Method",
        ["Scan QR Code", "Search Attendee"]
    )

    if option == "Scan QR Code":

        ticket = qrcode_scanner("Scan QR Code")

        if ticket:
            st.session_state.ticket = ticket
            st.session_state.page = "result"
            st.rerun()

    if option == "Search Attendee":

        search = st.text_input("Search by Name / Email / Ticket ID")

        if search:

            search = search.lower()

            results = data[
                data["Name"].astype(str).str.lower().str.contains(search)
                | data["Email"].astype(str).str.lower().str.contains(search)
                | data["Ticket_ID"].astype(str).str.lower().str.contains(search)
            ]

            if results.empty:

                st.error("❌ No attendee found")

            else:

                for i, row in results.iterrows():

                    st.write("---")
                    st.write("Name:", row["Name"])
                    st.write("Email:", row["Email"])
                    st.write("Ticket ID:", row["Ticket_ID"])

                    if row["Attended"] == "YES":
                        st.warning("⚠️ Already Checked")

                    else:
                        if st.button(f"Check-in {row['Ticket_ID']}"):

                            data.loc[i, "Attended"] = "YES"
                            data.to_excel(file, index=False)

                            st.success("Checked In ✅")


# صفحة النتيجة
elif st.session_state.page == "result":

    ticket = str(st.session_state.ticket).strip()

    person = data[data["Ticket_ID"].astype(str).str.strip() == ticket]

    if person.empty:

        st.error("❌ INVALID TICKET")

    else:

        idx = person.index[0]

        name = data.loc[idx, "Name"]
        email = data.loc[idx, "Email"]
        ticket_id = data.loc[idx, "Ticket_ID"]

        if data.loc[idx, "Attended"] == "YES":

            st.warning("⚠️ ALREADY CHECKED")

        else:

            data.loc[idx, "Attended"] = "YES"
            data.to_excel(file, index=False)

            st.success("✅ APPROVED")

        st.write("Name:", name)
        st.write("Email:", email)
        st.write("Ticket ID:", ticket_id)

    st.button("⬅ Back to Home", on_click=go_home)


# تحميل الشيت
st.divider()

buffer = BytesIO()
data.to_excel(buffer, index=False)
buffer.seek(0)

st.download_button(
    label="📥 Download Attendance Sheet",
    data=buffer,
    file_name="attendance_updated.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


