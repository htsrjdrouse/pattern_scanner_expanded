"""
Research dashboard routes for signal monitoring and analysis.
"""
from flask import render_template_string, request
import pandas as pd
from datetime import datetime, timedelta


RESEARCH_DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Alpha Research Platform</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
            color: #e0e0e0;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            color: #4fc3f7;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #9e9e9e;
            margin-bottom: 30px;
        }
        .nav {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            justify-content: center;
        }
        .nav a {
            padding: 10px 20px;
            background: #3a3a52;
            color: #4fc3f7;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s;
        }
        .nav a:hover {
            background: #4a4a62;
        }
        .section {
            background: #2a2a3e;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .section h2 {
            color: #4fc3f7;
            margin-top: 0;
            border-bottom: 2px solid #4fc3f7;
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #3a3a52;
        }
        th {
            background: #3a3a52;
            color: #4fc3f7;
            font-weight: 600;
        }
        tr:hover {
            background: #3a3a52;
        }
        .metric {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            margin: 2px;
        }
        .metric.positive {
            background: #1b5e20;
            color: #4caf50;
        }
        .metric.negative {
            background: #b71c1c;
            color: #ef5350;
        }
        .metric.neutral {
            background: #424242;
            color: #9e9e9e;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #b0b0b0;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            background: #3a3a52;
            border: 1px solid #4a4a62;
            border-radius: 5px;
            color: #e0e0e0;
            box-sizing: border-box;
        }
        button {
            padding: 12px 30px;
            background: #4fc3f7;
            color: #1e1e2e;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
        }
        button:hover {
            background: #29b6f6;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 Alpha Research Platform</h1>
        <p class="subtitle">Systematic signal analysis and backtesting</p>
        
        <div class="nav">
            <a href="/">Pattern Scanner</a>
            <a href="/research">Research Dashboard</a>
        </div>

        <div class="section">
            <h2>ℹ️ What This Tool Does</h2>
            <p style="color: #b0b0b0; line-height: 1.6;">
                This platform tests whether technical signals can predict future stock returns. It answers: 
                <strong>"If I buy stocks with high signal values, will they outperform?"</strong>
            </p>
            <details style="margin-top: 15px;">
                <summary style="cursor: pointer; color: #4fc3f7; font-weight: 600;">📖 Metric Explanations</summary>
                <div style="margin-top: 10px; padding: 15px; background: #1e1e2e; border-radius: 5px;">
                    <p><strong style="color: #4fc3f7;">IC (Information Coefficient)</strong> - Correlation between signal values and future returns. Higher = better predictive power. Good signals have IC > 5%.</p>
                    <p><strong style="color: #4fc3f7;">Hit Rate</strong> - Percentage of times high-signal stocks outperformed. Above 50% means the signal works more often than not.</p>
                    <p><strong style="color: #4fc3f7;">Long-Only Return</strong> - Average return from buying top 20% highest-signal stocks. Shows if signal identifies winners.</p>
                    <p><strong style="color: #4fc3f7;">Long-Short Return</strong> - Return from buying top 20% and shorting bottom 20%. Tests if signal ranks stocks correctly.</p>
                    <p><strong style="color: #4fc3f7;">Sharpe Ratio</strong> - Risk-adjusted return (return ÷ volatility). Above 1.0 is good, above 2.0 is excellent.</p>
                    <p><strong style="color: #4fc3f7;">Observations</strong> - Number of signal-return pairs analyzed. More = more reliable results (aim for 100+).</p>
                </div>
            </details>
        </div>

        <div class="section">
            <h2>🧪 Quick Backtest</h2>
            <form id="backtestForm">
                <div class="grid">
                    <div class="form-group">
                        <label>Signal</label>
                        <select name="signal_name" required>
                            {% for name in signals.keys() %}
                            <option value="{{ name }}">{{ name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Symbols (comma-separated)</label>
                        <input type="text" name="symbols" value="AAPL,MSFT,GOOGL,AMZN,NVDA" required>
                    </div>
                    <div class="form-group">
                        <label>Timeframe</label>
                        <select name="timeframe" required>
                            <option value="3m">3 Months</option>
                            <option value="6m" selected>6 Months</option>
                            <option value="1y">1 Year</option>
                            <option value="2y">2 Years</option>
                            <option value="3y">3 Years</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Horizon (days)</label>
                        <input type="number" name="horizon_days" value="10" required>
                    </div>
                </div>
                <button type="submit">Run Backtest</button>
            </form>
            <div id="results" style="margin-top: 20px;"></div>
        </div>

        <div class="section">
            <h2>📈 Signal Correlation Analysis</h2>
            <p style="color: #9e9e9e;">Compare multiple signals to identify redundancy and diversification opportunities.</p>
            <form id="correlationForm">
                <div class="form-group">
                    <label>Select Signals (Ctrl+Click for multiple)</label>
                    <select name="signal_names" multiple size="8" required>
                        {% for name in signals.keys() %}
                        <option value="{{ name }}">{{ name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label>Symbols (comma-separated)</label>
                    <input type="text" name="symbols" value="AAPL,MSFT,GOOGL,AMZN,NVDA" required>
                </div>
                <button type="submit">Compute Correlation</button>
            </form>
            <div id="corrResults" style="margin-top: 20px;"></div>
        </div>
    </div>

    <script>
        document.getElementById('backtestForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            // Calculate dates based on timeframe
            const endDate = new Date();
            const startDate = new Date();
            const timeframe = formData.get('timeframe');
            
            switch(timeframe) {
                case '3m': startDate.setMonth(startDate.getMonth() - 3); break;
                case '6m': startDate.setMonth(startDate.getMonth() - 6); break;
                case '1y': startDate.setFullYear(startDate.getFullYear() - 1); break;
                case '2y': startDate.setFullYear(startDate.getFullYear() - 2); break;
                case '3y': startDate.setFullYear(startDate.getFullYear() - 3); break;
            }
            
            const data = {
                signal_name: formData.get('signal_name'),
                symbols: formData.get('symbols').split(',').map(s => s.trim()),
                horizon_days: parseInt(formData.get('horizon_days')),
                start_date: startDate.toISOString().split('T')[0],
                end_date: endDate.toISOString().split('T')[0]
            };
            
            document.getElementById('results').innerHTML = '<p>Running backtest...</p>';
            
            try {
                const response = await fetch('/signals/backtest', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                
                if (result.error) {
                    document.getElementById('results').innerHTML = `<p style="color: #ef5350;">Error: ${result.error}</p>`;
                } else {
                    const formatValue = (val) => val === null || val === undefined ? 'N/A' : val;
                    const formatPct = (val) => val === null || val === undefined ? 'N/A' : (val * 100).toFixed(2) + '%';
                    const formatNum = (val) => val === null || val === undefined ? 'N/A' : val.toFixed(2);
                    
                    const html = `
                        <h3>Backtest Results: ${result.signal_name}</h3>
                        <table>
                            <tr><th>Metric</th><th>Value</th><th>Interpretation</th></tr>
                            <tr>
                                <td>IC (Pearson)</td>
                                <td class="metric ${result.ic_pearson_mean > 0 ? 'positive' : 'negative'}">${formatPct(result.ic_pearson_mean)}</td>
                                <td style="font-size: 0.9em; color: #9e9e9e;">${result.ic_pearson_mean > 0.05 ? '✓ Good predictive power' : result.ic_pearson_mean > 0 ? '⚠ Weak signal' : '✗ No predictive power'}</td>
                            </tr>
                            <tr>
                                <td>IC (Spearman)</td>
                                <td class="metric ${result.ic_spearman_mean > 0 ? 'positive' : 'negative'}">${formatPct(result.ic_spearman_mean)}</td>
                                <td style="font-size: 0.9em; color: #9e9e9e;">${result.ic_spearman_mean > 0.05 ? '✓ Good rank correlation' : result.ic_spearman_mean > 0 ? '⚠ Weak ranking' : '✗ Poor ranking'}</td>
                            </tr>
                            <tr>
                                <td>Hit Rate</td>
                                <td class="metric ${result.hit_rate > 0.5 ? 'positive' : 'negative'}">${formatPct(result.hit_rate)}</td>
                                <td style="font-size: 0.9em; color: #9e9e9e;">${result.hit_rate > 0.55 ? '✓ Reliable' : result.hit_rate > 0.5 ? '⚠ Slightly better than random' : '✗ Worse than coin flip'}</td>
                            </tr>
                            <tr>
                                <td>Long-Only Return</td>
                                <td class="metric ${result.long_only_return > 0 ? 'positive' : 'negative'}">${formatPct(result.long_only_return)}</td>
                                <td style="font-size: 0.9em; color: #9e9e9e;">${result.long_only_return > 0 ? '✓ Profitable' : '✗ Losing strategy'}</td>
                            </tr>
                            <tr>
                                <td>Long-Only Sharpe</td>
                                <td class="metric ${result.long_only_sharpe > 0 ? 'positive' : 'negative'}">${formatNum(result.long_only_sharpe)}</td>
                                <td style="font-size: 0.9em; color: #9e9e9e;">${result.long_only_sharpe > 1 ? '✓ Good risk-adjusted' : result.long_only_sharpe > 0 ? '⚠ Low risk-adjusted return' : '✗ Negative risk-adjusted'}</td>
                            </tr>
                            <tr>
                                <td>Long-Short Return</td>
                                <td class="metric ${result.long_short_return > 0 ? 'positive' : 'negative'}">${formatPct(result.long_short_return)}</td>
                                <td style="font-size: 0.9em; color: #9e9e9e;">${result.long_short_return > 0 ? '✓ Signal ranks correctly' : '✗ Poor ranking ability'}</td>
                            </tr>
                            <tr>
                                <td>Long-Short Sharpe</td>
                                <td class="metric ${result.long_short_sharpe > 0 ? 'positive' : 'negative'}">${formatNum(result.long_short_sharpe)}</td>
                                <td style="font-size: 0.9em; color: #9e9e9e;">${result.long_short_sharpe > 1 ? '✓ Strong market-neutral' : result.long_short_sharpe > 0 ? '⚠ Weak market-neutral' : '✗ Negative market-neutral'}</td>
                            </tr>
                            <tr><td>Observations</td><td>${result.n_observations}</td><td style="font-size: 0.9em; color: #9e9e9e;">${result.n_observations > 200 ? '✓ Reliable sample' : result.n_observations > 100 ? '⚠ Moderate sample' : '⚠ Small sample'}</td></tr>
                        </table>
                    `;
                    document.getElementById('results').innerHTML = html;
                }
            } catch (error) {
                document.getElementById('results').innerHTML = `<p style="color: #ef5350;">Error: ${error.message}</p>`;
            }
        });

        document.getElementById('correlationForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = {
                signal_names: Array.from(formData.getAll('signal_names')),
                symbols: formData.get('symbols').split(',').map(s => s.trim()),
                start_date: '2024-01-01',
                end_date: '2025-12-31'
            };
            
            document.getElementById('corrResults').innerHTML = '<p>Computing correlations...</p>';
            
            try {
                const response = await fetch('/signals/correlation', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                
                if (result.error) {
                    document.getElementById('corrResults').innerHTML = `<p style="color: #ef5350;">Error: ${result.error}</p>`;
                } else {
                    let html = '<h3>Signal Correlation Matrix</h3><table><thead><tr><th>Signal</th>';
                    const signals = Object.keys(result);
                    signals.forEach(s => html += `<th>${s}</th>`);
                    html += '</tr></thead><tbody>';
                    
                    signals.forEach(s1 => {
                        html += `<tr><td><strong>${s1}</strong></td>`;
                        signals.forEach(s2 => {
                            const corr = result[s1][s2];
                            const color = Math.abs(corr) > 0.7 ? (corr > 0 ? 'positive' : 'negative') : 'neutral';
                            html += `<td class="metric ${color}">${corr.toFixed(2)}</td>`;
                        });
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                    
                    document.getElementById('corrResults').innerHTML = html;
                }
            } catch (error) {
                document.getElementById('corrResults').innerHTML = `<p style="color: #ef5350;">Error: ${error.message}</p>`;
            }
        });
    </script>
</body>
</html>
"""


def add_research_routes(app):
    """Add research dashboard routes to Flask app."""
    
    @app.route('/research')
    def research_dashboard():
        import signals
        signal_list = signals.list_signals()
        return render_template_string(RESEARCH_DASHBOARD_HTML, signals=signal_list)
