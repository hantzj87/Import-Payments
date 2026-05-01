# CSV Import to TV

Remittance file converter — transforms network payout files into TicketVault-ready CSVs.

## Supported Networks
- Gametime
- GoTickets
- SeatGeek
- StubHub / Viagogo
- Ticket Evolution
- TicketsNow
- TickPick
- Vivid Seats
- *(Mercury, TicketNetwork — coming soon)*

## Output columns
`order#`, `amount`, `remittancedate`, `chargebackreason`

---

## Setup

### 1. Clone & install
```bash
git clone https://github.com/YOUR_USERNAME/csv-import-to-tv.git
cd csv-import-to-tv
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

---

## Keep-alive

Streamlit Community Cloud sleeps apps after ~1 hour of inactivity.
Run `keep_alive.py` on any always-on machine to prevent this:

```bash
# Update APP_URL in keep_alive.py or set the env var:
export STREAMLIT_URL=https://your-app-name.streamlit.app
python keep_alive.py
```

Or as a background process:
```bash
nohup python keep_alive.py &
```

Or as a cron job (every 10 minutes):
```
*/10 * * * * /usr/bin/python3 /path/to/keep_alive.py >> /tmp/keep_alive.log 2>&1
```
