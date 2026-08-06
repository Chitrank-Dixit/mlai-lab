# GPU Price Forecasting Workspace (NVIDIA RTX 50 Series)

A self-contained, notebook-first workspace inside the `basic-ml` environment for tracking, analyzing, and forecasting NVIDIA RTX 50 series GPU prices (specifically focusing on Indian retailer data, offline vendor quotes, and strict SKU/VRAM isolation).

---

## 📌 Features & Capabilities

- **Strict SKU & VRAM Isolation**: Never mixes 8GB and 16GB variants (e.g., RTX 5060 Ti 8GB vs 16GB).
- **Indian Retailer & Quote Ingestion**: Pre-configured for MDComputers, PrimeABGB, Vedant Computers, and Nehru Place local vendor quote CSVs.
- **Modular Pipeline Utilities**:
  - SKU validation & catalog integrity (`validate_skus.py`)
  - Price cleaning & shipping normalization (`clean_prices.py`, `normalize_prices.py`)
  - Lag & rolling volatility feature generation (`feature_builder.py`)
  - Baseline Moving Median & EWMA forecasters (`baseline_forecast.py`)
  - Supervised ML price forecaster (`ml_forecast.py`)
  - 30-Day Daywise Monthly Forecaster (`daywise_forecaster.py`)
  - Buy/Wait signal engine (`signal_rules.py`)
- **7 Executable Jupyter Notebooks**: End-to-end flow from data audit to buy/wait recommendations and 30-day daywise monthly forecasting.
- **PostgreSQL Schema & Views**: Optional schema DDL and views (`schema.sql`, `views.sql`).

---

## 📂 Workspace Folder Structure

```text
gpu_price_forecasting/
├── configs/
│   ├── products.yaml         # RTX 50 series catalog, MSRP, and specifications
│   ├── retailers.yaml        # Indian retailer metadata and shipping defaults
│   └── model_config.yaml     # Feature window, baseline, ML, & signal parameters
├── data/
│   ├── raw/                  # Drop location for scraped raw HTML or quotes
│   ├── processed/            # Location for exported feature tables
│   ├── external/             # Macro signal drops (USD-INR, silicon index)
│   └── sample/               # Plausible sample datasets (CSV format)
│       ├── products.csv
│       ├── retailers.csv
│       ├── product_listings.csv
│       ├── daily_price_observations.csv
│       └── external_market_signals.csv
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_eda_price_trends.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_baseline_forecast.ipynb
│   ├── 05_ml_forecast.ipynb
│   ├── 06_buy_wait_analysis.ipynb
│   └── 07_gpu_monthly_daywise_forecaster.ipynb
├── src/
│   ├── __init__.py
│   ├── io_utils.py           # Config & dataset loading helpers
│   ├── validate_skus.py      # SKU consistency & VRAM separation rules
│   ├── clean_prices.py       # Data cleaning & numeric conversion
│   ├── normalize_prices.py   # MSRP premium & effective price logic
│   ├── feature_builder.py    # Lag & rolling feature calculations
│   ├── baseline_forecast.py # Moving Median & EWMA forecasters
│   ├── ml_forecast.py       # Supervised Ridge / Tabular ML pipeline
│   ├── daywise_forecaster.py# 30-Day daywise price forecaster engine
│   └── signal_rules.py      # Buy / Wait decision logic
├── sql/
│   ├── schema.sql            # PostgreSQL table DDL
│   └── views.sql             # PostgreSQL analytical views
└── README.md
```

---


## 🚀 How to Run Notebooks

Launch the `basic-ml` lab container via Docker:

```bash
make basic
```

Or open JupyterLab directly at `http://localhost:8888` (default token: `antigravity`). Navigate to `gpu_price_forecasting/notebooks/` and execute notebooks in numerical order:

1. **`01_data_audit.ipynb`**: Audit CSVs, verify schema, and check 8GB vs 16GB separation.
2. **`02_eda_price_trends.ipynb`**: Plot historical price trends, retailer spreads, and local vendor quotes.
3. **`03_feature_engineering.ipynb`**: Generate lags, rolling medians, volatility, and save `featured_gpu_prices.csv`.
4. **`04_baseline_forecast.ipynb`**: Benchmark Moving Median and EWMA 7-day lookahead baselines.
5. **`05_ml_forecast.ipynb`**: Train tabular ML regression model and evaluate against ground truth.
6. **`06_buy_wait_analysis.ipynb`**: Review target-price reach probabilities and recommended actions (`BUY_NOW`, `WAIT`, `STRONG_BUY`).
7. **`07_gpu_monthly_daywise_forecaster.ipynb`**: Supply GPU name (e.g. Gigabyte Eagle Max 5060 Ti 16GB) and generate 30-day daywise price forecast table.


---

## 🔌 Extending to Real Retailer Scrapers & Data Streams

To integrate live scraping or automated offline quote ingestion:

1. **Web Scrapers (Playwright / BeautifulSoup)**:
   - Create scrapers under `src/scrapers/` to output daily CSV observations matching the schema in `data/sample/daily_price_observations.csv`.
2. **Local Vendor PDF Quote Parser (OCR / Tabula)**:
   - Parse vendor quote PDFs or WhatsApp price sheets into `daily_price_observations.csv` with `is_local_quote=True`.
3. **Database Integration**:
   - Run `sql/schema.sql` and `sql/views.sql` on a PostgreSQL database instance to store observations long-term.

---

## ⚠️ Assumptions & Limitations

- **Local File Execution**: Designed to execute standalone without requiring outbound internet calls during notebook runs.
- **Sample Data Provenance**: Sample CSVs contain realistic Indian market pricing based on actual market vendor quotes from late July 28, 2026:
  - **ASUS Dual GeForce RTX 5060 Ti 16GB GDDR7 OC**: ~₹88,200 (MSRP ₹49,999; ~1.76x MSRP premium)
  - **MSI Shadow GeForce RTX 5060 Ti 16GB GDDR7 2X OC**: ~₹88,800 (MSRP ₹48,999; ~1.81x MSRP premium)
  - **Gigabyte Eagle Max GeForce RTX 5060 Ti 16GB GDDR7 OC Triple Fan**: ~₹80,600 (MSRP ₹51,999; ~1.55x MSRP premium)

