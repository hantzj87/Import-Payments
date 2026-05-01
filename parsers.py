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
    # We parse using the known fixed column positions instead:
    # EventName, Venue, EventDate, TransactionID, Proceeds, Charges, Credit, Description
    # Strategy: read with engine='python', on_bad_lines='skip', then fall back to
    # positional parsing if needed.
    header = "EventName,Venue,EventDate,TransactionID,Proceeds,Charges,Credit,Description"
    col_names = [c.strip() for c in header.split(",")]
    n_cols = len(col_names)

    rows_out = []
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if i == 0:
            continue  # skip header
        if not line.strip():
            continue
        # Split and take last (n_cols-1) fields from right so venue absorbs commas
        parts = line.split(",")
        if len(parts) < n_cols:
            continue
        # Fixed columns from the right: Description=-1, Credit=-2, Charges=-3,
        # Proceeds=-4, TransactionID=-5, EventDate=-6
        # Everything before that is EventName+Venue merged
        description  = parts[-1].strip().strip('"')
        credit       = _clean_amount(parts[-2])
        charges      = _clean_amount(parts[-3])
        proceeds     = _clean_amount(parts[-4])
        transaction  = parts[-5].strip().strip('"')
        if not transaction:
            continue
        amount = proceeds + charges + credit
        chargeback = "" if description.lower() == "proceeds" else description
        rows_out.append({"order#": transaction, "amount": amount, "chargebackreason": chargeback})

    if not rows_out:
        return None
    return pd.DataFrame(rows_out).reset_index(drop=True)


# ── Ticket Evolution ──────────────────────────────────────────────────────────
def parse_ticket_evolution(file) -> pd.DataFrame:
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
    out["order#"]          = grouped["_po"]
    out["amount"]          = grouped["_net"]
    out["chargebackreason"] = ""
    return out.reset_index(drop=True)


# ── Router ────────────────────────────────────────────────────────────────────
def parse_file(file, network: str) -> pd.DataFrame:
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
    return parser(file)
