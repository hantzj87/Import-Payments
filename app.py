import streamlit as st

st.set_page_config(page_title="Tools", page_icon="🎟️", layout="centered")

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
    margin-bottom: 8px;
  }
  .title {
    font-size: 32px;
    font-weight: 300;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
  }
  .title span { font-weight: 500; }
  .subtitle {
    font-size: 15px;
    color: #888780;
    margin-bottom: 40px;
  }
  .tool-card {
    background: #fff;
    border: 1px solid #e8e6e0;
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 12px;
    transition: border-color 0.15s;
  }
  .tool-card:hover { border-color: #1a1a18; }
  .tool-name {
    font-size: 16px;
    font-weight: 500;
    color: #1a1a18;
    margin-bottom: 4px;
  }
  .tool-desc {
    font-size: 13px;
    color: #888780;
    margin-bottom: 0;
  }
  .tool-tag {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    background: #f5f4f0;
    color: #888780;
    padding: 3px 8px;
    border-radius: 4px;
    margin-bottom: 8px;
  }
  .divider {
    border: none;
    border-top: 1px solid #e8e6e0;
    margin: 32px 0;
  }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="eyebrow">Internal tools</div>', unsafe_allow_html=True)
st.markdown('<div class="title">Welcome 👋</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Select a tool from the sidebar or the list below.</div>', unsafe_allow_html=True)

# ── Tool directory ─────────────────────────────────────────────────────────────
tools = [
    {
        "tag": "Finance",
        "name": "Remittance Converter",
        "desc": "Convert network remittance files (Vivid, StubHub, SeatGeek, Gametime, and more) into TicketVault-ready CSVs.",
        "page": "Remittance_Converter",
    },
    # Add more tools here as you build them, e.g.:
    # {
    #     "tag": "Reporting",
    #     "name": "Sales Dashboard",
    #     "desc": "View and export sales data across all networks.",
    #     "page": "Sales_Dashboard",
    # },
]

for tool in tools:
    st.markdown(f"""
    <div class="tool-card">
      <div class="tool-tag">{tool['tag']}</div>
      <div class="tool-name">{tool['name']}</div>
      <div class="tool-desc">{tool['desc']}</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link(f"pages/{tool['page']}.py", label=f"Open {tool['name']} →")
    st.markdown("")

st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div style="font-size:12px;color:#bbb;font-family:\'DM Mono\',monospace;">More tools coming soon.</div>', unsafe_allow_html=True)
