# Internal Tools

A multi-page Streamlit app for internal operations tooling.

## Current tools
- **Remittance Converter** — converts network payout files into TicketVault-ready CSVs

## Supported networks (Remittance Converter)
Gametime, GoTickets, SeatGeek, StubHub, Ticket Evolution, TicketsNow, TickPick, Vivid Seats
*(Mercury, TicketNetwork — coming soon)*

## Project structure
```
app.py                        ← Landing page (home)
pages/
  1_Remittance_Converter.py   ← Remittance converter tool
parsers.py                    ← All network file parsers
keep_alive.py                 ← Prevents Streamlit from sleeping
requirements.txt
```

## Setup

### 1. Clone & install
```bash
git clone https://github.com/YOUR_USERNAME/internal-tools.git
cd internal-tools
pip install -r requirements.txt
```

### 2. Run locally
```bash
streamlit run app.py
```

### 3. Deploy to Streamlit Cloud
1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo → set **Main file** to `app.py`
4. Deploy

### 4. Adding a new tool
1. Create `pages/N_Tool_Name.py`
2. Add an entry to the `tools` list in `app.py`

## Keep-alive
```bash
export STREAMLIT_URL=https://your-app.streamlit.app
python keep_alive.py
```
