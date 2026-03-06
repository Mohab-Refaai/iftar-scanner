import streamlit as st
import pandas as pd

file = "attendees.xlsx"

data = pd.read_excel(file)

st.title("Iftar Check-in System")

ticket = st.text_input("Scan QR Code")

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