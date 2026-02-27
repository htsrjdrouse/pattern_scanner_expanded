"""
Flask API endpoints for alpha research platform.
Extends existing pattern_scanner.py without breaking current functionality.
"""
from flask import Blueprint, jsonify, request
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import signals
import backtest
import analytics

research_bp = Blueprint('research', __name__, url_prefix='/signals')


def fetch_price_data(symbols, start_date, end_date):
    """Fetch price data for symbols."""
    data = []
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            if df.empty:
                continue
            df = df.reset_index()
            df['symbol'] = symbol
            df.columns = [c.lower() for c in df.columns]
            # Remove timezone to avoid comparison issues
            if 'date' in df.columns and hasattr(df['date'].dtype, 'tz') and df['date'].dt.tz is not None:
                df['date'] = df['date'].dt.tz_localize(None)
            data.append(df[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']])
        except:
            continue
    
    if not data:
        return pd.DataFrame()
    
    return pd.concat(data, ignore_index=True)


@research_bp.route('/list', methods=['GET'])
def list_signals():
    """List all available signals with metadata."""
    signal_list = signals.list_signals()
    return jsonify(signal_list)


@research_bp.route('/backtest', methods=['POST'])
def run_backtest():
    """
    Run backtest for a signal.
    
    Request JSON:
    {
        "signal_name": "rsi_14",
        "symbols": ["AAPL", "MSFT", ...],
        "horizon_days": 20,
        "start_date": "2024-01-01",
        "end_date": "2025-12-31"
    }
    """
    data = request.get_json()
    
    signal_name = data.get('signal_name')
    symbols = data.get('symbols', [])
    horizon_days = data.get('horizon_days', 20)
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not signal_name or not symbols:
        return jsonify({'error': 'signal_name and symbols required'}), 400
    
    # Get signal
    signal = signals.get_signal(signal_name)
    if not signal:
        return jsonify({'error': f'Signal {signal_name} not found'}), 404
    
    # Fetch price data
    df_prices = fetch_price_data(symbols, start_date, end_date)
    if df_prices.empty:
        return jsonify({'error': 'No price data available', 'details': 'yfinance returned no data'}), 400
    
    # Compute signal
    df_signals = signal.compute(df_prices)
    if df_signals.empty:
        return jsonify({'error': 'Signal computation failed', 'details': 'No signal values generated'}), 400
    
    # Run backtest
    results = backtest.run_signal_backtest(df_signals, df_prices, horizon_days, start_date, end_date)
    
    # Check for error
    if 'error' in results:
        return jsonify(results), 400
    
    # Convert non-serializable objects
    response = {k: v for k, v in results.items() if k not in ['ic_series', 'quantile_returns']}
    response['date_range'] = [str(d) for d in results.get('date_range', [])]
    
    # Replace NaN with None for JSON serialization
    import math
    for key, value in response.items():
        if isinstance(value, float) and math.isnan(value):
            response[key] = None
    
    return jsonify(response)


@research_bp.route('/decay', methods=['POST'])
def run_decay_analysis():
    """
    Run decay analysis for a signal.
    
    Request JSON:
    {
        "signal_name": "rsi_14",
        "symbols": ["AAPL", "MSFT", ...],
        "horizons": [1, 5, 10, 20, 60],
        "start_date": "2024-01-01",
        "end_date": "2025-12-31"
    }
    """
    data = request.get_json()
    
    signal_name = data.get('signal_name')
    symbols = data.get('symbols', [])
    horizons = data.get('horizons', [1, 5, 10, 20, 60])
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not signal_name or not symbols:
        return jsonify({'error': 'signal_name and symbols required'}), 400
    
    # Get signal
    signal = signals.get_signal(signal_name)
    if not signal:
        return jsonify({'error': f'Signal {signal_name} not found'}), 404
    
    # Fetch price data
    df_prices = fetch_price_data(symbols, start_date, end_date)
    if df_prices.empty:
        return jsonify({'error': 'No price data available'}), 400
    
    # Compute signal
    df_signals = signal.compute(df_prices)
    
    # Run decay analysis
    decay_df = backtest.run_decay_analysis(df_signals, df_prices, horizons, start_date, end_date)
    
    return jsonify(decay_df.to_dict(orient='records'))


@research_bp.route('/correlation', methods=['POST'])
def compute_correlation():
    """
    Compute correlation matrix of signals.
    
    Request JSON:
    {
        "signal_names": ["rsi_14", "macd", "momentum_20"],
        "symbols": ["AAPL", "MSFT", ...],
        "start_date": "2024-01-01",
        "end_date": "2025-12-31"
    }
    """
    data = request.get_json()
    
    signal_names = data.get('signal_names', [])
    symbols = data.get('symbols', [])
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not signal_names or not symbols:
        return jsonify({'error': 'signal_names and symbols required'}), 400
    
    # Fetch price data
    df_prices = fetch_price_data(symbols, start_date, end_date)
    if df_prices.empty:
        return jsonify({'error': 'No price data available'}), 400
    
    # Compute all signals
    all_signals = []
    for signal_name in signal_names:
        signal = signals.get_signal(signal_name)
        if signal:
            df_sig = signal.compute(df_prices)
            all_signals.append(df_sig)
    
    if not all_signals:
        return jsonify({'error': 'No valid signals computed'}), 400
    
    df_all_signals = pd.concat(all_signals, ignore_index=True)
    
    # Compute correlation matrix
    corr_matrix = analytics.signal_correlation_matrix(df_all_signals)
    
    return jsonify(corr_matrix.to_dict())


@research_bp.route('/composite', methods=['POST'])
def build_composite():
    """
    Build composite signal from multiple signals.
    
    Request JSON:
    {
        "signal_names": ["rsi_14", "macd", "momentum_20"],
        "signal_weights": {"rsi_14": 0.4, "macd": 0.3, "momentum_20": 0.3},
        "symbols": ["AAPL", "MSFT", ...],
        "start_date": "2024-01-01",
        "end_date": "2025-12-31"
    }
    """
    data = request.get_json()
    
    signal_names = data.get('signal_names', [])
    signal_weights = data.get('signal_weights')
    symbols = data.get('symbols', [])
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not signal_names or not symbols:
        return jsonify({'error': 'signal_names and symbols required'}), 400
    
    # Fetch price data
    df_prices = fetch_price_data(symbols, start_date, end_date)
    if df_prices.empty:
        return jsonify({'error': 'No price data available'}), 400
    
    # Compute all signals
    all_signals = []
    for signal_name in signal_names:
        signal = signals.get_signal(signal_name)
        if signal:
            df_sig = signal.compute(df_prices)
            all_signals.append(df_sig)
    
    if not all_signals:
        return jsonify({'error': 'No valid signals computed'}), 400
    
    df_all_signals = pd.concat(all_signals, ignore_index=True)
    
    # Build composite
    df_composite = analytics.build_composite_signal(df_all_signals, signal_weights, start_date, end_date)
    
    # Run backtest on composite
    horizon_days = data.get('horizon_days', 20)
    results = backtest.run_signal_backtest(df_composite, df_prices, horizon_days, start_date, end_date)
    
    response = {k: v for k, v in results.items() if k not in ['ic_series', 'quantile_returns']}
    response['date_range'] = [str(d) for d in results.get('date_range', [])]
    
    return jsonify(response)


@research_bp.route('/regime', methods=['POST'])
def analyze_regime():
    """
    Analyze signal performance by market regime.
    
    Request JSON:
    {
        "signal_names": ["rsi_14", "macd"],
        "symbols": ["AAPL", "MSFT", ...],
        "index_symbol": "SPY",
        "horizon_days": 20,
        "start_date": "2024-01-01",
        "end_date": "2025-12-31"
    }
    """
    data = request.get_json()
    
    signal_names = data.get('signal_names', [])
    symbols = data.get('symbols', [])
    index_symbol = data.get('index_symbol', 'SPY')
    horizon_days = data.get('horizon_days', 20)
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not signal_names or not symbols:
        return jsonify({'error': 'signal_names and symbols required'}), 400
    
    # Fetch price data (including index)
    all_symbols = list(set(symbols + [index_symbol]))
    df_prices = fetch_price_data(all_symbols, start_date, end_date)
    if df_prices.empty:
        return jsonify({'error': 'No price data available'}), 400
    
    # Detect regimes
    df_regimes = analytics.detect_market_regime(df_prices, index_symbol)
    
    # Compute all signals
    all_signals = []
    for signal_name in signal_names:
        signal = signals.get_signal(signal_name)
        if signal:
            df_sig = signal.compute(df_prices)
            all_signals.append(df_sig)
    
    if not all_signals:
        return jsonify({'error': 'No valid signals computed'}), 400
    
    df_all_signals = pd.concat(all_signals, ignore_index=True)
    
    # Compute regime-conditional IC
    regime_ic = analytics.compute_regime_conditional_ic(df_all_signals, df_prices, df_regimes, horizon_days)
    
    return jsonify(regime_ic.to_dict(orient='records'))


@research_bp.route('/turnover', methods=['POST'])
def analyze_turnover_endpoint():
    """
    Analyze turnover for a signal.
    
    Request JSON:
    {
        "signal_name": "rsi_14",
        "symbols": ["AAPL", "MSFT", ...],
        "rebalance_freq": 20,
        "top_pct": 0.2,
        "start_date": "2024-01-01",
        "end_date": "2025-12-31"
    }
    """
    data = request.get_json()
    
    signal_name = data.get('signal_name')
    symbols = data.get('symbols', [])
    rebalance_freq = data.get('rebalance_freq', 20)
    top_pct = data.get('top_pct', 0.2)
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not signal_name or not symbols:
        return jsonify({'error': 'signal_name and symbols required'}), 400
    
    # Get signal
    signal = signals.get_signal(signal_name)
    if not signal:
        return jsonify({'error': f'Signal {signal_name} not found'}), 404
    
    # Fetch price data
    df_prices = fetch_price_data(symbols, start_date, end_date)
    if df_prices.empty:
        return jsonify({'error': 'No price data available'}), 400
    
    # Compute signal
    df_signals = signal.compute(df_prices)
    
    # Analyze turnover
    turnover_metrics = analytics.analyze_turnover(df_signals, rebalance_freq, top_pct)
    
    return jsonify(turnover_metrics)
