import pandas as pd
import io


def _read(file) -> bytes:
    """Read a file-like object, seeking to start first (handles Streamlit's UploadedFile)."""
    if hasattr(file, 'seek'):
        file.seek(0)
    return file.read()


def _clean_amount(val):
    """Strip $, commas, whitespace and return float."""
    if pd.isna(val):
        return 0.0
    return float(str(val).replace("$", "").replace(",", "").strip() or 0)


# ── Vivid Seats ───────────────────────────────────────────────────────────────
def parse_vivid(file) -> pd.DataFrame:
    content = _read(file).decode("utf-8", errors="replace")
    lines = content.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("po #") or line.strip().lower().startswith("po#"):
            header_idx = i
            break
    if header_idx is None:
        return None
    csv_str = "\n".join(lines[header_idx:])
    df = pd.read_csv(io.StringIO(csv_str))
    df.columns = [c.strip() for c in df.columns]
    order_col = next((c for c in df.columns if c.strip().lower().replace(" ", "") == "order#"), None)
    amt_col   = next((c for c in df.columns if c.strip().lower() == "amount"), None)
    if not order_col or not amt_col:
        return None
    out = pd.DataFrame()
    out["order#"]          = df[order_col].astype(str).str.strip()
    out["amount"]          = df[amt_col].apply(_clean_amount)
    out["chargebackreason"] = ""
    return out.dropna(subset=["order#"]).reset_index(drop=True)


# ── Gametime ──────────────────────────────────────────────────────────────────
def parse_gametime(file) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(_read(file)))
    df.columns = [c.strip() for c in df.columns]
    out = pd.DataFrame()
    out["order#"]          = df["#"].astype(str).str.strip()
    out["amount"]          = df["Payout"].apply(_clean_amount)
    out["chargebackreason"] = df["Reason"].fillna("").astype(str).str.strip() if "Reason" in df.columns else ""
    return out.dropna(subset=["order#"]).reset_index(drop=True)


# ── GoTickets ─────────────────────────────────────────────────────────────────
def parse_gotickets(file) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(_read(file)))
    df.columns = [c.strip() for c in df.columns]
    out = pd.DataFrame()
    out["order#"]          = df["Order ID"].astype(str).str.strip()
    out["amount"]          = df["Amount"].apply(_clean_amount)
    out["chargebackreason"] = ""
    return out.dropna(subset=["order#"]).reset_index(drop=True)


# ── SeatGeek ──────────────────────────────────────────────────────────────────
def parse_seatgeek(file) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(_read(file)))
    df.columns = [c.strip().strip('"') for c in df.columns]
    out = pd.DataFrame()
    out["order#"]          = df["Order ID"].astype(str).str.strip().str.strip('"')
    out["amount"]          = df["Amount"].apply(_clean_amount)
    out["chargebackreason"] = df["Reason"].fillna("").astype(str).str.strip().str.strip('"') if "Reason" in df.columns else ""
    return out.dropna(subset=["order#"]).reset_index(drop=True)


# ── TicketsNow ────────────────────────────────────────────────────────────────
def parse_ticketsnow(file) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(_read(file)))
    df.columns = [c.strip() for c in df.columns]
    out = pd.DataFrame()
    out["order#"]          = df["Web Order #"].astype(str).str.strip()
    out["amount"]          = df["Amount"].apply(_clean_amount)
    out["chargebackreason"] = ""
    return out.dropna(subset=["order#"]).reset_index(drop=True)


# ── TickPick (xlsx) ───────────────────────────────────────────────────────────
def parse_tickpick(file) -> pd.DataFrame:
    df = pd.read_excel(io.BytesIO(_read(file)))
    df.columns = [c.strip() for c in df.columns]
    out = pd.DataFrame()
    out["order#"]          = df["Order Number"].astype(str).str.strip()
    out["amount"]          = df["Amount"].apply(_clean_amount)
    out["chargebackreason"] = ""
    return out.dropna(subset=["order#"]).reset_index(drop=True)


# ── StubHub / Viagogo ─────────────────────────────────────────────────────────
def parse_stubhub(file) -> pd.DataFrame:
    raw = _read(file)
    content = None
    for enc in ("utf-16", "utf-8", "latin-1", "cp1252"):
        try:
            content = raw.decode(enc)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    # The Venue column sometimes contains unquoted commas which confuses pandas.
    # Parse using fixed column positions from the right:
    # EventName, Venue, EventDate, TransactionID, Proceeds, Charges, Credit, Description
    rows_out = []
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if i == 0:
            continue
        if not line.strip():
            continue
        parts = line.split(",")
        if len(parts) < 8:
            continue
        description = parts[-1].strip().strip('"')
        credit      = _clean_amount(parts[-2])
        charges     = _clean_amount(parts[-3])
        proceeds    = _clean_amount(parts[-4])
        transaction = parts[-5].strip().strip('"')
        if not transaction:
            continue
        amount     = proceeds + charges + credit
        chargeback = "" if description.lower() == "proceeds" else description
        rows_out.append({"order#": transaction, "amount": round(amount, 2), "chargebackreason": chargeback})

    if not rows_out:
        return None
    return pd.DataFrame(rows_out).reset_index(drop=True)


# ── Ticket Evolution ──────────────────────────────────────────────────────────
def parse_ticket_evolution(file, date_start=None, date_end=None) -> pd.DataFrame:
    raw = _read(file)
    content = raw.decode("utf-8", errors="replace")
    lines = content.splitlines()

    # Find header row
    header_idx = None
    for i, line in enumerate(lines):
        if "order - po #" in line.lower():
            header_idx = i
            break
    if header_idx is None:
        return None

    csv_str = "\n".join(lines[header_idx:])
    df = pd.read_csv(io.StringIO(csv_str))
    df.columns = [c.strip().strip('"') for c in df.columns]

    # Skip withdrawals
    df = df[df["Type"].str.strip().str.lower() != "withdrawal"].copy()

    # Filter by date range if provided
    # Date format in file: "04-30-2026 04:02 pm"
    if date_start or date_end:
        date_col = next((c for c in df.columns if c.strip().lower() == "date created"), None)
        if date_col:
            df["_date"] = pd.to_datetime(
                df[date_col].astype(str).str.strip().str.strip('"'),
                format="%m-%d-%Y %I:%M %p",
                errors="coerce"
            ).dt.date
            if date_start:
                df = df[df["_date"] >= date_start]
            if date_end:
                df = df[df["_date"] <= date_end]

    po_col = next((c for c in df.columns if "po #" in c.lower()), None)
    if not po_col:
        return None

    df["_credit"] = df["Credit"].apply(_clean_amount)
    df["_debit"]  = df["Debit"].apply(_clean_amount)
    df["_net"]    = df["_credit"] - df["_debit"]
    df["_po"]     = df[po_col].astype(str).str.strip()

    grouped = df.groupby("_po")["_net"].sum().reset_index()
    grouped["_net"] = grouped["_net"].round(2)

    out = pd.DataFrame()
    out["order#"]           = grouped["_po"]
    out["amount"]           = grouped["_net"]
    out["chargebackreason"] = ""
    return out.reset_index(drop=True)


# ── Router ────────────────────────────────────────────────────────────────────
def parse_file(file, network: str, **kwargs) -> pd.DataFrame:
    parsers = {
        "Vivid":            parse_vivid,
        "Gametime":         parse_gametime,
        "GoTickets":        parse_gotickets,
        "SeatGeek":         parse_seatgeek,
        "TicketsNow":       parse_ticketsnow,
        "TickPick":         parse_tickpick,
        "StubHub":          parse_stubhub,
        "Ticket Evolution": parse_ticket_evolution,
    }
    parser = parsers.get(network)
    if parser is None:
        return None
    return parser(file, **kwargs)
