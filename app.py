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
    df.columns = df.columns.astype(str).str.strip()

    if "Attended" not in df.columns:
        df["Attended"] = ""

    df["Attended"] = df["Attended"].fillna("")
    return df


def save_data(df):
    df.to_excel(FILE_PATH, index=False)


def normalize_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def is_attended(value):
    return str(value).strip().upper() == "YES"


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


# =========================
# ACTION FUNCTIONS
# =========================
def clear_search():
    st.session_state.search_value = ""


def reset_system():
    df_reset = load_data()
    df_reset["Attended"] = ""
    save_data(df_reset)

    st.session_state.page = "home"
    st.session_state.ticket_value = ""
    st.session_state.search_value = ""


def go_home():
    st.session_state.page = "home"
    st.session_state.ticket_value = ""


def process_ticket(ticket_value, df, col_map):

    ticket_value = normalize_text(ticket_value)

    if not ticket_value:
        st.error("❌ INVALID TICKET")
        return df

    matched = df[
        df[col_map["ticket_id"]].astype(str).str.strip().str.lower()
        == ticket_value.lower()
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
        st.success("✅ APPROVED")

    display_person_details(row, col_map)
    return df


def build_search_label(row, col_map):

    name = normalize_text(row[col_map["name"]])
    email = normalize_text(row[col_map["email"]])
    phone = normalize_text(row[col_map["phone"]])
    ticket_id = normalize_text(row[col_map["ticket_id"]])

    return f"{name} | {phone} | {email} | {ticket_id}"


# =========================
# LOAD DATA
# =========================
if not os.path.exists(FILE_PATH):
    st.error(f"Excel file not found: {FILE_PATH}")
    st.stop()

data = load_data()
col_map = get_column_map(data)


# =========================
# SESSION STATE INIT
# =========================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "ticket_value" not in st.session_state:
    st.session_state.ticket_value = ""

if "search_value" not in st.session_state:
    st.session_state.search_value = ""


# =========================
# HEADER
# =========================
col1, col2 = st.columns([8,1])

with col1:
    st.title("🎟️ Iftar Check-in System")

with col2:
    with st.expander("⚙️"):
        st.write("System tools")
        st.button("Reset Attendance", on_click=reset_system)


# =========================
# HOME PAGE
# =========================
if st.session_state.page == "home":

    option = st.radio(
        "Choose Check-in Method",
        ["Scan QR Code", "Search Attendee"],
        horizontal=True,
        key="mode"
    )

    st.write("")

    # =========================
    # QR SCAN
    # =========================
    if st.session_state.mode == "Scan QR Code":

        st.subheader("Scan Ticket QR")

        scanned_value = qrcode_scanner("Scan attendee QR code")

        if scanned_value:
            st.session_state.ticket_value = normalize_text(scanned_value)
            st.session_state.page = "result"
            st.rerun()


    # =========================
    # SEARCH
    # =========================
    elif st.session_state.mode == "Search Attendee":

        st.subheader("Search Attendee")

        colA, colB = st.columns([5,1])

        with colA:
            search = st.text_input(
                "",
                key="search_value",
                placeholder="Search by Name / Email / Phone / Ticket ID"
            )

        with colB:
            st.button("Clear", on_click=clear_search)

        if search:

            search_lower = search.strip().lower()

            result_mask = (
                data[col_map["name"]].astype(str).str.lower().str.contains(search_lower, na=False)
                | data[col_map["email"]].astype(str).str.lower().str.contains(search_lower, na=False)
                | data[col_map["phone"]].astype(str).str.lower().str.contains(search_lower, na=False)
                | data[col_map["ticket_id"]].astype(str).str.lower().str.contains(search_lower, na=False)
            )

            results = data[result_mask].copy()

            if results.empty:

                st.error("❌ No attendee found")

            else:

                results = results.reset_index()

                results["display_label"] = results.apply(
                    lambda row: build_search_label(row, col_map), axis=1
                )

                selected_label = st.selectbox(
                    "Select attendee",
                    options=results["display_label"].tolist()
                )

                selected_row = results[
                    results["display_label"] == selected_label
                ].iloc[0]

                selected_idx = selected_row["index"]

                st.write("")

                display_person_details(data.loc[selected_idx], col_map)

                if is_attended(data.loc[selected_idx, col_map["attended"]]):

                    st.warning("⚠️ ALREADY CHECKED")

                else:

                    if st.button("✅ Check-in Selected Attendee"):

                        data.loc[selected_idx, col_map["attended"]] = "YES"
                        save_data(data)

                        st.success("✅ Checked In Successfully")
                        st.rerun()


# =========================
# RESULT PAGE
# =========================
elif st.session_state.page == "result":

    st.subheader("Ticket Result")

    data = load_data()

    process_ticket(st.session_state.ticket_value, data, col_map)

    st.button("⬅ Back to Home", on_click=go_home)


# =========================
# DOWNLOAD SHEET
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
