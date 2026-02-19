# Pattern Scanner

A Flask-based stock pattern scanner that detects bullish patterns (Cup & Handle, Double Bottoms, Ascending Triangles, Bull Flags) with advanced charting, technical analysis, DCF valuation, and options strategies.

## Features

### Pattern Detection
- **Cup & Handle**: Classic U-shaped pattern with handle pullback
- **Double Bottoms**: W-shaped reversal with neckline breakout
- **Ascending Triangles**: Rising support with flat resistance
- **Bull Flags**: Strong pole followed by consolidation

### Charting
- **CTO Larsson Lines**: Two EMAs of (High+Low)/2 at 15 & 29 periods with color-coded fill (yellow bullish, blue bearish)
- **Moving Averages**: 13, 26, 40, 50, 200 SMAs with customizable display
- **Pattern Overlays**: Visual indicators for detected patterns (resistance lines, pole lines, necklines, markers)
- **Golden/Death Cross Markers**: Gold/red markers when 50 SMA crosses 200 SMA

### Analysis
- **Technical Indicators**: RSI, MACD, ADX, Volume analysis
- **DCF Valuation**: Intrinsic value estimates with margin of safety
- **Breakout Criteria**: 8-point checklist for entry signals
- **Options Strategies**: Bull Call Spread recommendations with P&L analysis
- **External Links**: Quick access to Yahoo Finance, Seeking Alpha, and SEC EDGAR filings

### UI
- Dark theme with interactive controls
- Stock search and detailed analysis pages
- Chart toggles for SMAs and CTO lines

## Installation

### Prerequisites
- Docker and Docker Compose
- Python 3.12 (for local development)

Access at http://localhost:5002

### Quick Start with Docker
git clone <your-repo-url>
cd pattern_scanner_extended
docker compose up -d --build

### Local Development
```bash
pip install -r requirements.txt
python pattern_scanner.py
```
Access at http://127.0.0.1:5002

## Usage

1. **Scan Markets**: Use the dropdown to scan S&P 500, NASDAQ, or All US stocks
2. **View Details**: Click "View" on any detected pattern for full analysis
3. **Customize Charts**:
   - Toggle SMAs: 50 & 200, All, Short-term, None
   - Enable CTO Larsson Lines
4. **Analyze Patterns**: Review technical indicators, DCF, and options plays

## API Endpoints

- `GET /`: Main scanner page
- `GET /chart/<symbol>`: Detailed chart with toggles
- `POST /scan`: Bulk market scan (JSON response)
- `GET /api/scan?market=sp500`: API scan endpoint

## Configuration

- **SMA Options**: ?sma=50,200 or ?sma=all
- **CTO Lines**: ?cto=1
- **EDGAR Financials**: ?edgar=1
- **Budget for Options**: ?budget=500

## Technical Details

- Built with Flask, yfinance, pandas-ta, matplotlib
- Docker containerized for easy deployment
- Responsive dark UI with HTML/CSS/JS
- Real-time data from Yahoo Finance

## Disclaimer

For educational purposes only. Not financial advice. Patterns are probabilistic—always do your own research.

## License

MIT License
