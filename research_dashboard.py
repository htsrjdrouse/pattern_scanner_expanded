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
            table-layout: fixed;
        }
        th, td {
            padding: 12px 8px;
            text-align: center;
            border-bottom: 1px solid #3a3a52;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        th:first-child, td:first-child {
            text-align: left;
            font-weight: 600;
        }
        th {
            background: #3a3a52;
            color: #4fc3f7;
            font-weight: 600;
            position: sticky;
            top: 0;
        }
        tr:hover {
            background: #3a3a52;
        }
        .metric {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            margin: 0;
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
            min-width: 60px;
            text-align: center;
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
                        <label>Signals (Ctrl+Click for multiple)</label>
                        <select name="signal_names" multiple size="8" required>
                            {% for name in signals.keys() %}
                            <option value="{{ name }}">{{ name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Sector <button type="button" onclick="showSectorManager()" style="padding: 4px 8px; font-size: 0.85em; margin-left: 10px;">Manage</button></label>
                        <select id="sectorSelect" name="sector">
                            <option value="">Custom Symbols</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Symbols (comma-separated)</label>
                        <input type="text" id="symbolsInput" name="symbols" value="AAPL,MSFT,GOOGL,AMZN,NVDA" required>
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

        <div id="sectorModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; overflow-y: auto;">
            <div style="max-width: 900px; margin: 50px auto; background: #2a2a3e; padding: 30px; border-radius: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2 style="margin: 0; color: #4fc3f7;">Sector Manager</h2>
                    <button onclick="hideSectorManager()" style="background: #ef5350;">Close</button>
                </div>
                
                <div style="margin-bottom: 30px;">
                    <h3 style="color: #4fc3f7;">Create New Sector</h3>
                    <form id="createSectorForm">
                        <div class="form-group">
                            <label>Sector ID (lowercase, underscores)</label>
                            <input type="text" id="newSectorId" placeholder="e.g., tech_giants" required>
                        </div>
                        <div class="form-group">
                            <label>Sector Name</label>
                            <input type="text" id="newSectorName" placeholder="e.g., Tech Giants" required>
                        </div>
                        <div class="form-group">
                            <label>Tickers (comma-separated)</label>
                            <textarea id="newSectorTickers" rows="3" placeholder="AAPL,MSFT,GOOGL,AMZN,META" required></textarea>
                        </div>
                        <button type="submit">Create Sector</button>
                    </form>
                </div>

                <div>
                    <h3 style="color: #4fc3f7;">Existing Sectors</h3>
                    <div id="sectorList"></div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📈 Signal Correlation Analysis</h2>
            <p style="color: #9e9e9e;">Compare multiple signals to identify redundancy and diversification opportunities.</p>
            <form id="correlationForm">
                <div class="grid">
                    <div class="form-group">
                        <label>Select Signals (Ctrl+Click for multiple)</label>
                        <select name="signal_names" multiple size="8" required>
                            {% for name in signals.keys() %}
                            <option value="{{ name }}">{{ name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Sector <button type="button" onclick="showSectorManager()" style="padding: 4px 8px; font-size: 0.85em; margin-left: 10px;">Manage</button></label>
                        <select id="corrSectorSelect" name="sector">
                            <option value="">Custom Symbols</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Symbols (comma-separated)</label>
                        <input type="text" id="corrSymbolsInput" name="symbols" value="AAPL,MSFT,GOOGL,AMZN,NVDA" required>
                    </div>
                </div>
                <button type="submit">Compute Correlation</button>
            </form>
            <div id="corrResults" style="margin-top: 20px;"></div>
        </div>
    </div>

    <script>
        let sectorsData = {};

        async function loadSectors() {
            try {
                const response = await fetch('/signals/sectors');
                sectorsData = await response.json();
                populateSectorDropdown();
            } catch (error) {
                console.error('Failed to load sectors:', error);
            }
        }

        function populateSectorDropdown() {
            const select = document.getElementById('sectorSelect');
            const corrSelect = document.getElementById('corrSectorSelect');
            
            select.innerHTML = '<option value="">Custom Symbols</option>';
            corrSelect.innerHTML = '<option value="">Custom Symbols</option>';
            
            const sectors = sectorsData.sectors || {};
            Object.keys(sectors).sort().forEach(id => {
                const sector = sectors[id];
                const option1 = document.createElement('option');
                option1.value = id;
                option1.textContent = sector.name;
                select.appendChild(option1);
                
                const option2 = document.createElement('option');
                option2.value = id;
                option2.textContent = sector.name;
                corrSelect.appendChild(option2);
            });
        }

        function showSectorManager() {
            document.getElementById('sectorModal').style.display = 'block';
            renderSectorList();
        }

        function hideSectorManager() {
            document.getElementById('sectorModal').style.display = 'none';
        }

        function renderSectorList() {
            const container = document.getElementById('sectorList');
            const sectors = sectorsData.sectors || {};
            
            if (Object.keys(sectors).length === 0) {
                container.innerHTML = '<p style="color: #9e9e9e;">No sectors yet. Create one above.</p>';
                return;
            }

            let html = '';
            Object.keys(sectors).sort().forEach(id => {
                const sector = sectors[id];
                html += `
                    <div style="background: #3a3a52; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div style="flex: 1;">
                                <h4 style="margin: 0 0 10px 0; color: #4fc3f7;">${sector.name}</h4>
                                <p style="margin: 0; color: #9e9e9e; font-size: 0.9em;">ID: ${id}</p>
                                <p style="margin: 5px 0 0 0; color: #b0b0b0; font-size: 0.9em;">${sector.tickers.length} tickers: ${sector.tickers.join(', ')}</p>
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <button onclick="editSector('${id}')" style="padding: 8px 15px; background: #4fc3f7;">Edit</button>
                                <button onclick="deleteSector('${id}')" style="padding: 8px 15px; background: #ef5350;">Delete</button>
                            </div>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        async function deleteSector(sectorId) {
            if (!confirm(`Delete sector "${sectorsData.sectors[sectorId].name}"?`)) return;
            
            try {
                const response = await fetch(`/signals/sectors/${sectorId}`, { method: 'DELETE' });
                const result = await response.json();
                
                if (result.success) {
                    await loadSectors();
                    renderSectorList();
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Failed to delete sector: ' + error.message);
            }
        }

        function editSector(sectorId) {
            const sector = sectorsData.sectors[sectorId];
            const newName = prompt('Sector Name:', sector.name);
            if (!newName) return;
            
            const newTickers = prompt('Tickers (comma-separated):', sector.tickers.join(','));
            if (!newTickers) return;
            
            updateSector(sectorId, newName, newTickers.split(',').map(t => t.trim()));
        }

        async function updateSector(sectorId, name, tickers) {
            try {
                const response = await fetch(`/signals/sectors/${sectorId}`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ name, tickers })
                });
                const result = await response.json();
                
                if (result.success) {
                    await loadSectors();
                    renderSectorList();
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Failed to update sector: ' + error.message);
            }
        }

        document.getElementById('createSectorForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const id = document.getElementById('newSectorId').value.trim();
            const name = document.getElementById('newSectorName').value.trim();
            const tickers = document.getElementById('newSectorTickers').value.split(',').map(t => t.trim()).filter(t => t);
            
            try {
                const response = await fetch('/signals/sectors', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ id, name, tickers })
                });
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('createSectorForm').reset();
                    await loadSectors();
                    renderSectorList();
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Failed to create sector: ' + error.message);
            }
        });

        document.getElementById('sectorSelect').addEventListener('change', (e) => {
            const sectorId = e.target.value;
            if (sectorId && sectorsData.sectors && sectorsData.sectors[sectorId]) {
                const tickers = sectorsData.sectors[sectorId].tickers;
                document.getElementById('symbolsInput').value = tickers.join(',');
            }
        });

        document.getElementById('corrSectorSelect').addEventListener('change', (e) => {
            const sectorId = e.target.value;
            if (sectorId && sectorsData.sectors && sectorsData.sectors[sectorId]) {
                const tickers = sectorsData.sectors[sectorId].tickers;
                document.getElementById('corrSymbolsInput').value = tickers.join(',');
            }
        });

        // Load sectors on page load
        loadSectors();

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
            
            const signalNames = Array.from(formData.getAll('signal_names'));
            const symbols = formData.get('symbols').split(',').map(s => s.trim());
            const horizonDays = parseInt(formData.get('horizon_days'));
            const startDateStr = startDate.toISOString().split('T')[0];
            const endDateStr = endDate.toISOString().split('T')[0];
            
            document.getElementById('results').innerHTML = `<p>Running backtest for ${signalNames.length} signal(s)...</p>`;
            
            try {
                // Run all backtests in parallel
                const promises = signalNames.map(signalName => 
                    fetch('/signals/backtest', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            signal_name: signalName,
                            symbols: symbols,
                            horizon_days: horizonDays,
                            start_date: startDateStr,
                            end_date: endDateStr
                        })
                    }).then(r => r.json())
                );
                
                const results = await Promise.all(promises);
                
                // Check for errors
                const errors = results.filter(r => r.error);
                if (errors.length > 0) {
                    document.getElementById('results').innerHTML = `<p style="color: #ef5350;">Errors: ${errors.map(e => e.error).join(', ')}</p>`;
                    return;
                }
                
                const formatPct = (val) => val === null || val === undefined ? 'N/A' : (val * 100).toFixed(2) + '%';
                const formatNum = (val) => val === null || val === undefined ? 'N/A' : val.toFixed(2);
                
                // Build comparison table
                let html = '<h3>Backtest Results Comparison</h3>';
                html += '<div style="overflow-x: auto;">';
                html += '<table><thead><tr>';
                html += '<th style="min-width: 120px;">Signal</th>';
                html += '<th style="min-width: 80px;">IC</th>';
                html += '<th style="min-width: 80px;">Hit Rate</th>';
                html += '<th style="min-width: 90px;">Long Ret</th>';
                html += '<th style="min-width: 90px;">L/S Ret</th>';
                html += '<th style="min-width: 90px;">L/S Sharpe</th>';
                html += '<th style="min-width: 70px;">Obs</th>';
                html += '</tr></thead><tbody>';
                
                results.forEach(result => {
                    html += `<tr>
                        <td style="text-align: left;"><strong>${result.signal_name}</strong></td>
                        <td><span class="metric ${result.ic_pearson_mean > 0 ? 'positive' : 'negative'}">${formatPct(result.ic_pearson_mean)}</span></td>
                        <td><span class="metric ${result.hit_rate > 0.5 ? 'positive' : 'negative'}">${formatPct(result.hit_rate)}</span></td>
                        <td><span class="metric ${result.long_only_return > 0 ? 'positive' : 'negative'}">${formatPct(result.long_only_return)}</span></td>
                        <td><span class="metric ${result.long_short_return > 0 ? 'positive' : 'negative'}">${formatPct(result.long_short_return)}</span></td>
                        <td><span class="metric ${result.long_short_sharpe > 0 ? 'positive' : 'negative'}">${formatNum(result.long_short_sharpe)}</span></td>
                        <td>${result.n_observations}</td>
                    </tr>`;
                });
                
                html += '</tbody></table></div>';
                html += '<p style="margin-top: 15px; color: #9e9e9e; font-size: 0.9em;">💡 Tip: Higher IC and Sharpe ratios indicate better signals. Hit rate > 50% means the signal works more often than not.</p>';
                
                document.getElementById('results').innerHTML = html;
            } catch (error) {
                document.getElementById('results').innerHTML = `<p style="color: #ef5350;">Error: ${error.message}</p>`;
            }
        });

        document.getElementById('correlationForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = {
                signal_names: Array.from(formData.getAll('signal_names')),
                symbols: document.getElementById('corrSymbolsInput').value.split(',').map(s => s.trim()),
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
                    const signals = Object.keys(result);
                    let html = '<h3>Signal Correlation Matrix</h3>';
                    html += '<div style="overflow-x: auto;">';
                    html += '<table style="table-layout: auto;"><thead><tr>';
                    html += '<th style="min-width: 120px; text-align: left;">Signal</th>';
                    signals.forEach(s => html += `<th style="min-width: 80px;">${s}</th>`);
                    html += '</tr></thead><tbody>';
                    
                    signals.forEach(s1 => {
                        html += `<tr><td style="text-align: left;"><strong>${s1}</strong></td>`;
                        signals.forEach(s2 => {
                            const corr = result[s1][s2];
                            const color = Math.abs(corr) > 0.7 ? (corr > 0 ? 'positive' : 'negative') : 'neutral';
                            html += `<td><span class="metric ${color}">${corr.toFixed(2)}</span></td>`;
                        });
                        html += '</tr>';
                    });
                    html += '</tbody></table></div>';
                    
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
