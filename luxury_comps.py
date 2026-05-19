# ============================================================
#  Analyse comparative de multiples boursiers — Secteur Luxe
#  Auteur : Antoine Vergnaud
#  Description : Récupère les multiples de valorisation
#  (P/E, EV/EBITDA, P/B) via yfinance et permet d'enrichir
#  manuellement les données si besoin.
# ============================================================

import yfinance as yf
from tabulate import tabulate
from datetime import date

# ─────────────────────────────────────────────
#  1. UNIVERS D'ANALYSE — modifiable librement
# ─────────────────────────────────────────────
COMPANIES = [
    {"name": "LVMH",      "ticker": "MC.PA"},
    {"name": "Hermès",    "ticker": "RMS.PA"},
    {"name": "Kering",    "ticker": "KER.PA"},
    {"name": "Richemont", "ticker": "CFR.SW"},
    {"name": "Burberry",  "ticker": "BRBY.L"},
]

# ─────────────────────────────────────────────
#  2. DONNÉES MANUELLES (fallback si API indispo)
#     Source : Bloomberg / Rapports annuels 2024
# ─────────────────────────────────────────────
MANUAL_DATA = {
    "MC.PA":   {"pe": 21.4, "ev_ebitda": 11.8, "pb": 3.9,  "market_cap_bn": 195.0},
    "RMS.PA":  {"pe": 52.1, "ev_ebitda": 35.2, "pb": 18.6, "market_cap_bn": 198.0},
    "KER.PA":  {"pe": 13.2, "ev_ebitda":  7.9, "pb": 1.4,  "market_cap_bn":  28.0},
    "CFR.SW":  {"pe": 18.7, "ev_ebitda": 12.4, "pb": 2.8,  "market_cap_bn":  47.0},
    "BRBY.L":  {"pe": 14.5, "ev_ebitda":  6.8, "pb": 3.1,  "market_cap_bn":   4.5},
}

# ─────────────────────────────────────────────
#  3. RÉCUPÉRATION DES DONNÉES
# ─────────────────────────────────────────────
def fetch_data(ticker: str) -> dict:
    """Tente de récupérer les données via yfinance.
    Si l'API est indisponible, utilise les données manuelles."""
    try:
        info = yf.Ticker(ticker).info
        pe         = info.get("trailingPE")
        ev_ebitda  = info.get("enterpriseToEbitda")
        pb         = info.get("priceToBook")
        mktcap     = info.get("marketCap")
        mktcap_bn  = round(mktcap / 1e9, 1) if mktcap else None

        # Si yfinance renvoie des données valides, on les utilise
        if pe and ev_ebitda and pb:
            return {
                "pe": round(pe, 1),
                "ev_ebitda": round(ev_ebitda, 1),
                "pb": round(pb, 1),
                "market_cap_bn": mktcap_bn,
                "source": "API"
            }
    except Exception:
        pass

    # Sinon, fallback sur les données manuelles
    manual = MANUAL_DATA.get(ticker, {})
    return {
        "pe": manual.get("pe", "N/A"),
        "ev_ebitda": manual.get("ev_ebitda", "N/A"),
        "pb": manual.get("pb", "N/A"),
        "market_cap_bn": manual.get("market_cap_bn", "N/A"),
        "source": "Manuel"
    }

# ─────────────────────────────────────────────
#  4. CONSTRUCTION DU TABLEAU
# ─────────────────────────────────────────────
def build_table() -> list:
    rows = []
    for company in COMPANIES:
        data = fetch_data(company["ticker"])
        rows.append([
            company["name"],
            company["ticker"],
            f"{data['market_cap_bn']} Md€" if data['market_cap_bn'] != "N/A" else "N/A",
            f"{data['pe']}x"        if data['pe'] != "N/A" else "N/A",
            f"{data['ev_ebitda']}x" if data['ev_ebitda'] != "N/A" else "N/A",
            f"{data['pb']}x"        if data['pb'] != "N/A" else "N/A",
            data["source"]
        ])
    return rows

# ─────────────────────────────────────────────
#  5. CALCUL DES MÉDIANES DU SECTEUR
# ─────────────────────────────────────────────
def compute_medians(rows: list) -> list:
    def median(values):
        nums = [float(v.replace("x","")) for v in values if v != "N/A"]
        if not nums: return "N/A"
        nums.sort()
        n = len(nums)
        return f"{(nums[n//2] if n % 2 else (nums[n//2-1]+nums[n//2])/2):.1f}x"

    pe_vals       = [r[3] for r in rows]
    ev_vals       = [r[4] for r in rows]
    pb_vals       = [r[5] for r in rows]

    return ["─" * 10, "MÉDIANE", "─", median(pe_vals), median(ev_vals), median(pb_vals), "─"]

# ─────────────────────────────────────────────
#  6. AFFICHAGE
# ─────────────────────────────────────────────
def display(rows: list):
    headers = ["Entreprise", "Ticker", "Mkt Cap", "P/E", "EV/EBITDA", "P/B", "Source"]
    medians = compute_medians(rows)

    print()
    print("=" * 70)
    print(f"  ANALYSE COMPARATIVE — SECTEUR LUXE  |  {date.today().strftime('%d/%m/%Y')}")
    print("=" * 70)
    print()
    print(tabulate(rows + [medians], headers=headers, tablefmt="rounded_outline"))
    print()
    print("  💡 Observations :")
    print("  • Hermès trade à une prime significative vs ses pairs (P/E >50x)")
    print("  • Kering affiche les multiples les plus bas du secteur")
    print("  • La médiane sectorielle P/E reflète le pricing power du luxe")
    print()
    print("  Source : yfinance (API) ou données manuelles Bloomberg / RA 2024")
    print("=" * 70)
    print()

# ─────────────────────────────────────────────
#  7. MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n⏳ Récupération des données en cours...")
    rows = build_table()
    display(rows)
