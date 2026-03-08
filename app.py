import streamlit as st
import pandas as pd
from streamlit_qrcode_scanner import qrcode_scanner
from io import BytesIO
import os

# =========================
# CONFIG
# =========================
FILE_PATH = "attendees.xlsx"

st.set_page_config(page_title="Iftar Check-in System", page_icon="🎟️", layout="wide")


# =========================
# HELPERS
# =========================
def load_data():
    df = pd.read_excel(FILE_PATH)

    # تنظيف أسماء الأعمدة من المسافات
    df.columns = df.columns.astype(str).str.strip()

    # لو عمود الحضور مش موجود نضيفه
    if "Attended" not in df.columns:
        df["Attended"] = ""

    return df


def save_data(df):
    df.to_excel(FILE_PATH, index=False)


def normalize_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def is_attended(value):
    value = normalize_text(value).lower()
    return value in ["yes", "y", "true", "1", "checked", "attended"]


def get_column_map(df):
    columns = {col.strip(): col for col in df.columns}

    return {
        "name": columns.get("Full Name"),
        "email": columns.get("Email Address"),
        "phone": columns.get("Phone Number"),
        "ticket_id": columns.get("Ticket_ID"),
        "ticket_type": columns.get("Please select your ticket type:"),
        "payment_method": columns.get("Payment Method"),
        "attended": columns.get("Attended"),
    }


def display_person_details(row, col_map):
    st.markdown("### Attendee Details")
    c1, c2 = st.columns(2)

    with c1:
        st.write("**Name:**", normalize_text(row[col_map["name"]]))
        st.write("**Email:**", normalize_text(row[col_map["email"]]))
        st.write("**Phone:**", normalize_text(row[col_map["phone"]]))

    with c2:
        st.write("**Ticket ID:**", normalize_text(row[col_map["ticket_id"]]))
        st.write("**Meal / Ticket Type:**", normalize_text(row[col_map["ticket_type"]]))
        st.write("**Payment Method:**", normalize_text(row[col_map["payment_method"]]))


def go_home():
    st.session_state.page = "home"
    st.session_state.ticket_value = ""
    st.session_state.search_value = ""


def process_ticket(ticket_value, df, col_map):
    ticket_value = normalize_text(ticket_value)

    if not ticket_value:
        st.error("❌ INVALID TICKET")
        return df

    matched = df[
        df[col_map["ticket_id"]].astype(str).str.strip().str.lower() == ticket_value.lower()
    ]

    if matched.empty:
        st.error("❌ INVALID TICKET")
        return df

    idx = matched.index[0]
    row = df.loc[idx]

    if is_attended(row[col_map["attended"]]):
        st.warning("⚠️ ALREADY CHECKED")
    else:
        df.loc[idx, col_map["attended"]] = "YES"
        save_data(df)
        row = df.loc[idx]
        st.success("✅ APPROVED")

    display_person_details(row, col_map)
    return df


# =========================
# LOAD DATA
# =========================
if not os.path.exists(FILE_PATH):
    st.error(f"Excel file not found: {FILE_PATH}")
    st.stop()

data = load_data()
col_map = get_column_map(data)

required_missing = []
if not col_map["name"]:
    required_missing.append("Full Name")
if not col_map["email"]:
    required_missing.append("Email Address")
if not col_map["phone"]:
    required_missing.append("Phone Number")
if not col_map["ticket_id"]:
    required_missing.append("Ticket_ID")
if not col_map["ticket_type"]:
    required_missing.append("Please select your ticket type:")
if not col_map["payment_method"]:
    required_missing.append("Payment Method")
if not col_map["attended"]:
    required_missing.append("Attended")

if required_missing:
    st.error("Missing required columns in Excel file:")
    for item in required_missing:
        st.write("-", item)
    st.stop()


# =========================
# SESSION STATE
# =========================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "ticket_value" not in st.session_state:
    st.session_state.ticket_value = ""

if "search_value" not in st.session_state:
    st.session_state.search_value = ""


# =========================
# UI
# =========================
st.title("🎟️ Iftar Check-in System")


# =========================
# HOME PAGE
# =========================
if st.session_state.page == "home":
    option = st.radio(
        "Choose Check-in Method",
        ["Scan QR Code", "Search Attendee"],
        horizontal=True
    )

    st.write("")

    if option == "Scan QR Code":
        st.subheader("Scan Ticket QR")
        scanned_value = qrcode_scanner("Scan attendee QR code")

        if scanned_value:
            st.session_state.ticket_value = normalize_text(scanned_value)
            st.session_state.page = "result"
            st.rerun()

    elif option == "Search Attendee":
        st.subheader("Search Attendee")

        search = st.text_input(
            "Search by Name / Email / Phone / Ticket ID",
            value=st.session_state.search_value,
            placeholder="Type any name, email, phone, or ticket ID..."
        )

        st.session_state.search_value = search

        if search:
            search_lower = search.strip().lower()

            result_mask = (
                data[col_map["name"]].astype(str).str.lower().str.contains(search_lower, na=False)
                | data[col_map["email"]].astype(str).str.lower().str.contains(search_lower, na=False)
                | data[col_map["phone"]].astype(str).str.lower().str.contains(search_lower, na=False)
                | data[col_map["ticket_id"]].astype(str).str.lower().str.contains(search_lower, na=False)
            )

            results = data[result_mask]

            if results.empty:
                st.error("❌ No attendee found")
            else:
                st.success(f"Found {len(results)} result(s)")

                for i, row in results.iterrows():
                    with st.container():
                        st.write("---")
                        c1, c2 = st.columns([3, 1])

                        with c1:
                            st.write("**Name:**", normalize_text(row[col_map["name"]]))
                            st.write("**Email:**", normalize_text(row[col_map["email"]]))
                            st.write("**Phone:**", normalize_text(row[col_map["phone"]]))
                            st.write("**Ticket ID:**", normalize_text(row[col_map["ticket_id"]]))
                            st.write("**Meal / Ticket Type:**", normalize_text(row[col_map["ticket_type"]]))
                            st.write("**Payment Method:**", normalize_text(row[col_map["payment_method"]]))

                            if is_attended(row[col_map["attended"]]):
                                st.warning("⚠️ Already Checked")
                            else:
                                st.info("Not checked in yet")

                        with c2:
                            if st.button("Check-in", key=f"checkin_{i}"):
                                if not is_attended(data.loc[i, col_map["attended"]]):
                                    data.loc[i, col_map["attended"]] = "YES"
                                    save_data(data)
                                    st.success("✅ Checked In Successfully")
                                    st.rerun()
                                else:
                                    st.warning("⚠️ Already Checked")
                                    st.rerun()


# =========================
# RESULT PAGE
# =========================
elif st.session_state.page == "result":
    st.subheader("Ticket Result")

    data = load_data()
    process_ticket(st.session_state.ticket_value, data, col_map)

    st.write("")
    st.button("⬅ Back to Home", on_click=go_home)


# =========================
# DOWNLOAD UPDATED SHEET
# =========================
st.divider()

latest_data = load_data()
buffer = BytesIO()
latest_data.to_excel(buffer, index=False)
buffer.seek(0)

st.download_button(
    label="📥 Download Attendance Sheet",
    data=buffer,
    file_name="attendance_updated.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
