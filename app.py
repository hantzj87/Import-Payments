import streamlit as st
import pandas as pd
import io
from datetime import date
from parsers import parse_file

st.set_page_config(page_title="CSV Import to TV", page_icon="🎟️", layout="centered")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.12em;
    color: #888780;
    text-transform: uppercase;
    margin-bottom: 4px;
  }
  .title { font-size: 28px; font-weight: 300; letter-spacing: -0.02em; margin-bottom: 24px; }
  .title span { font-weight: 500; }
  .stat-box {
    background: #f5f4f0;
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
  }
  .stat-label {
    font-size: 11px;
    color: #888780;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 4px;
  }
  .stat-val { font-size: 22px; font-weight: 500; color: #1a1a18; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="eyebrow">Remittance converter</div>', unsafe_allow_html=True)
st.markdown('<div class="title">Remittance <span>→ TicketVault</span></div>', unsafe_allow_html=True)

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    company = st.selectbox("Company", ["", "YS", "TV"], index=0,
                           format_func=lambda x: "Select..." if x == "" else x)

with col2:
    network = st.selectbox("Network", [
        "", "Gametime", "GoTickets", "Mercury", "SeatGeek", "StubHub",
        "Ticket Evolution", "TicketNetwork", "TicketsNow", "TickPick", "Vivid"
    ], index=0, format_func=lambda x: "Select..." if x == "" else x)

with col3:
    remit_date = st.date_input("Remittance date", value=None, format="MM/DD/YYYY")

uploaded_file = st.file_uploader(
    "Upload remittance file",
    type=["csv", "xlsx", "xls"],
    label_visibility="collapsed",
    help="Drop your remittance file here (.csv or .xlsx)"
)

st.markdown("*Drag & drop or click above to upload your remittance file (.csv or .xlsx)*")

# ── Validation & Parsing ──────────────────────────────────────────────────────
if uploaded_file and company and network and remit_date:
    with st.spinner("Parsing file..."):
        try:
            df = parse_file(uploaded_file, network)
        except Exception as e:
            st.error(f"Could not parse file: {e}")
            st.stop()

    if df is None or df.empty:
        st.error("Could not parse file — check that the file matches the selected network.")
        st.stop()

    # Add remittance date column, format as M/D/YYYY
    date_str = f"{remit_date.month}/{remit_date.day}/{remit_date.year}"
    df["remittancedate"] = date_str

    # Reorder columns
    df = df[["order#", "amount", "remittancedate", "chargebackreason"]]

    # ── Stats ─────────────────────────────────────────────────────────────────
    gross      = df[df["amount"] > 0]["amount"].sum()
    net        = df["amount"].sum()
    chargebacks = (df["amount"] < 0).sum()

    st.markdown("---")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f'<div class="stat-box"><div class="stat-label">Total rows</div><div class="stat-val">{len(df):,}</div></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="stat-box"><div class="stat-label">Gross</div><div class="stat-val">${gross:,.2f}</div></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div class="stat-box"><div class="stat-label">Chargebacks</div><div class="stat-val">{chargebacks}</div></div>', unsafe_allow_html=True)
    with s4:
        st.markdown(f'<div class="stat-box"><div class="stat-label">Net total</div><div class="stat-val">${net:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("#### Preview — first 8 rows")
    st.dataframe(df.head(8), use_container_width=True, hide_index=True)

    # ── Download ──────────────────────────────────────────────────────────────
    csv_out = df.to_csv(index=False)
    short_date = remit_date.strftime("%m-%d-%y")
    filename = f"{company}_{network.replace(' ', '')}_{short_date}.csv"

    st.download_button(
        label="Download CSV",
        data=csv_out,
        file_name=filename,
        mime="text/csv",
        type="primary",
        use_container_width=False,
    )

elif uploaded_file and (not company or not network or not remit_date):
    st.warning("Please select Company, Network, and Remittance Date before uploading.")
