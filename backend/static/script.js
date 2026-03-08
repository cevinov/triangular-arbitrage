const API_BASE = '/api/bot';
const API_URL = '/api';

async function fetchStatus() {
    try {
        // Binance
        const binRes = await fetch(`${API_BASE}/binance/status`);
        const binData = await binRes.json();
        updateCard('binance', binData);

        // Indodax
        const indRes = await fetch(`${API_BASE}/indodax/status`);
        const indData = await indRes.json();
        updateCard('indodax', indData);

        // System Status
        const sysIndicator = document.getElementById('status-indicator');
        sysIndicator.querySelector('div').className = 'w-3 h-3 rounded-full bg-green-500 animate-pulse';
        sysIndicator.querySelector('span').innerText = 'System Online';
        sysIndicator.querySelector('span').className = 'text-sm font-medium text-green-400';

    } catch (e) {
        console.error("Error fetching status:", e);
        const sysIndicator = document.getElementById('status-indicator');
        sysIndicator.querySelector('div').className = 'w-3 h-3 rounded-full bg-red-500';
        sysIndicator.querySelector('span').innerText = 'System Offline';
        sysIndicator.querySelector('span').className = 'text-sm font-medium text-red-400';
    }
}

function updateCard(exchange, data) {
    const statusEl = document.getElementById(`${exchange}-status`);
    const msgEl = document.getElementById(`${exchange}-msg`);
    const amountEl = document.getElementById(`${exchange}-amount`);
    const feeEl = document.getElementById(`${exchange}-fee`);

    if (data.running) {
        statusEl.innerText = 'RUNNING';
        statusEl.className = 'text-xs font-mono text-green-400 mt-1 block font-bold';
    } else {
        statusEl.innerText = 'STOPPED';
        statusEl.className = 'text-xs font-mono text-red-400 mt-1 block font-bold';
    }

    msgEl.innerText = data.message;

    // Only update input if not focused (to avoid overwriting user typing)
    if (document.activeElement !== amountEl) {
        if (exchange === 'binance') {
            amountEl.value = data.initial_amount;
            if (feeEl && document.activeElement !== feeEl) {
                feeEl.value = data.fee * 100; // Convert to percentage
            }
        } else {
            amountEl.value = data.initial_amount;
            if (feeEl && document.activeElement !== feeEl && data.fee !== null) {
                feeEl.value = data.fee * 100; // Convert to percentage if available
            }
        }
    }
}

async function controlBot(exchange, action) {
    try {
        const res = await fetch(`${API_BASE}/${exchange}/${action}`, { method: 'POST' });
        const data = await res.json();
        alert(data.message || data.error);
        fetchStatus();
    } catch (e) {
        alert("Error sending command");
    }
}

let pendingConfig = null;

async function updateConfig(exchange) {
    const amountEl = document.getElementById(`${exchange}-amount`);
    const amount = parseFloat(amountEl.value);

    let fee = 0;
    const feeEl = document.getElementById(`${exchange}-fee`);
    if (feeEl) {
        fee = parseFloat(feeEl.value) / 100;
    }

    // Show confirmation modal for all exchanges
    showConfirmModal(exchange, amount, fee);
}

function showConfirmModal(exchange, amount, fee) {
    const modal = document.getElementById('confirm-modal');
    const amountDisplay = document.getElementById('modal-amount');
    const feeDisplay = document.getElementById('modal-fee');
    const confirmBtn = document.getElementById('modal-confirm-btn');

    if (exchange === 'binance') {
        amountDisplay.innerText = `$${amount}`;
    } else {
        amountDisplay.innerText = `${amount.toLocaleString()} IDR`;
    }

    feeDisplay.innerText = `${(fee * 100).toFixed(2)}%`;

    // Store config for execution
    pendingConfig = { exchange, amount, fee };

    // Set up confirm button
    confirmBtn.onclick = () => {
        if (pendingConfig) {
            executeSave(pendingConfig.exchange, pendingConfig.amount, pendingConfig.fee);
            closeModal();
        }
    };

    modal.classList.remove('hidden');
}

function closeModal() {
    document.getElementById('confirm-modal').classList.add('hidden');
    pendingConfig = null;
}

async function executeSave(exchange, amount, fee) {
    let body = { amount: amount };
    if (fee !== undefined) {
        body.fee = fee;
    }

    try {
        const res = await fetch(`${API_BASE}/${exchange}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        alert(data.message || data.error);
        fetchStatus();
    } catch (e) {
        alert("Error updating config");
    }
}

// Poll status every 2 seconds
setInterval(fetchStatus, 2000);
fetchStatus();

// Real-time Logs
function connectLogs() {
    const logContainer = document.getElementById('logs-container');
    const eventSource = new EventSource('/api/logs');

    eventSource.onmessage = function (event) {
        const msg = event.data;
        const p = document.createElement('p');
        p.innerText = msg;
        p.className = 'break-words'; // Ensure long lines wrap
        logContainer.appendChild(p);

        // Auto-scroll to bottom with a slight delay to ensure DOM update
        requestAnimationFrame(() => {
            logContainer.scrollTop = logContainer.scrollHeight;
        });

        // Limit log history to 1000 lines to prevent memory issues
        if (logContainer.children.length > 1000) {
            logContainer.removeChild(logContainer.firstChild);
        }
    };

    eventSource.onerror = function () {
        console.error("EventSource failed.");
        eventSource.close();
        // Retry connection after 5 seconds
        setTimeout(connectLogs, 5000);
    };
}

// Navigation Logic
function switchView(viewName) {
    // Hide all views
    document.getElementById('view-dashboard').classList.add('hidden');
    document.getElementById('view-logs').classList.add('hidden');
    document.getElementById('view-data').classList.add('hidden');
    document.getElementById('view-analysis').classList.add('hidden');

    // Show selected view
    document.getElementById(`view-${viewName}`).classList.remove('hidden');

    // Update nav styles
    const navs = ['dashboard', 'logs', 'data', 'analysis'];
    navs.forEach(nav => {
        const el = document.getElementById(`nav-${nav}`);
        if (nav === viewName) {
            el.className = 'flex items-center gap-3 px-4 py-3 bg-gray-700 text-white rounded-lg transition-colors';
        } else {
            el.className = 'flex items-center gap-3 px-4 py-3 text-gray-400 hover:bg-gray-700 hover:text-white rounded-lg transition-colors';
        }
    });

    if (viewName === 'data') {
        loadDataFiles();
    }

    // Load analysis if switching to analysis view
    if (viewName === 'analysis') {
        loadAnalysisFileList();
    }
}

function clearLogs() {
    const logContainer = document.getElementById('logs-container');
    logContainer.innerHTML = '<p class="text-gray-500 italic">[SYSTEM] Logs cleared.</p>';
}

// Data Viewer Logic
async function loadDataFiles() {
    try {
        const res = await fetch('/api/data/files');
        const files = await res.json();
        const select = document.getElementById('data-file-select');

        // Save current selection
        const currentVal = select.value;

        select.innerHTML = '<option value="" disabled selected>Select a file...</option>';
        files.forEach(file => {
            const option = document.createElement('option');
            option.value = file.id;
            option.innerText = `${file.name} (${file.last_modified})`;
            select.appendChild(option);
        });

        // Restore selection if valid
        if (currentVal) {
            select.value = currentVal;
        }
    } catch (e) {
        console.error("Error loading data files:", e);
    }
}

async function loadFileContent() {
    const select = document.getElementById('data-file-select');
    const fileId = select.value;
    if (!fileId) return;

    const contentEl = document.getElementById('data-content');
    contentEl.innerText = "Loading...";

    try {
        const res = await fetch(`/api/data/content?file_id=${fileId}`);
        const data = await res.json();
        contentEl.innerText = JSON.stringify(data, null, 2);
    } catch (e) {
        contentEl.innerText = "Error loading file content.";
        console.error(e);
    }
}

// Analysis Logic

// --- HELPERS ---
const fmt = (num, decimals = 2) => num.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
const fmtCrypto = (num) => num.toFixed(8);

async function loadAnalysisFileList() {
    const select = document.getElementById('analysis-file-select');
    // Check if element exists
    if (!select) return;

    // Save current selection if any
    const currentSelection = select.value;

    try {
        const response = await fetch(`${API_BASE.replace('/api/bot', '/api/data/files')}`); // Use correct endpoint
        const files = await response.json();

        // Filter for result files only
        const resultFiles = files.filter(f => f.id.startsWith('result:'));

        select.innerHTML = '<option value="">All Files</option>';

        resultFiles.forEach(file => {
            const filename = file.id.replace('result:', '');
            const option = document.createElement('option');
            option.value = filename;
            option.textContent = `${file.name} (${file.last_modified})`;
            select.appendChild(option);
        });

        // Restore selection if it still exists
        if (currentSelection) {
            select.value = currentSelection;
        }

        // Load analysis
        loadAnalysis();

    } catch (error) {
        console.error('Error loading analysis files:', error);
    }
}

async function loadAnalysis() {
    const select = document.getElementById('analysis-file-select');
    if (!select) return;

    const selectedFile = select.value;

    let url = `${API_URL}/analysis`;
    if (selectedFile) {
        url += `?files=${selectedFile}`;
    }

    try {
        const response = await fetch(url);
        const data = await response.json();

        // We will use the aggregated stats for the top cards and mock the individual trades 
        // OR we need to fetch the actual content of the selected files to render the detailed cards.
        // And try to fetch the file content if a file is selected.

        if (selectedFile) {
            // If a specific file is selected, fetch its content to show detailed cards
            const fileContentRes = await fetch(`${API_URL}/data/content?file_id=result:${selectedFile}`);
            const fileContent = await fileContentRes.json();

            // Ensure it's an array
            const trades = Array.isArray(fileContent) ? fileContent : [fileContent];

            renderStats(data, trades.length);
            renderTradeCards(trades);
        } else {
            // If all files (or no specific file) selected, we might not be able to show all trades efficiently if there are too many.
            renderStats(data, data.binance.trade_count + data.indodax.trade_count);
            document.getElementById('trade-cards-container').innerHTML =
                '<div class="text-center text-gray-500 mt-10">Select a specific file to view detailed trade cards and visualizations.</div>';
        }

    } catch (error) {
        console.error('Error loading analysis:', error);
    }
}

function renderStats(data, totalCount) {
    const statsContainer = document.getElementById('stats-grid');

    // Aggregating Binance and Indodax for the summary
    const totalProfitIDR = data.indodax.total_profit_idr;
    const totalProfitUSD = data.binance.total_profit_usd;

    // Calculate Avg ROI if available (not in current aggregated stats, would need raw data)
    const avgRoi = 0;

    const stats = [
        { label: 'Total Found', value: totalCount, color: 'text-white' },
        { label: 'Indodax Profit', value: `${fmt(totalProfitIDR)} <span class="text-sm font-normal text-slate-500">IDR</span>`, color: 'text-emerald-400', icon: 'trending-up' },
        { label: 'Binance Profit', value: `${fmt(totalProfitUSD)} <span class="text-sm font-normal text-slate-500">USD</span>`, color: 'text-blue-400', icon: 'trending-up' },
        // { label: 'Avg. ROI', value: `${fmt(avgRoi, 4)}%`, color: 'text-white' } // Removed as we don't have this in agg stats yet
    ];

    statsContainer.innerHTML = stats.map(stat => `
        <div class="bg-slate-900 border border-slate-800 p-4 rounded-lg">
            <div class="text-slate-500 text-xs uppercase font-semibold mb-1">${stat.label}</div>
            <div class="text-2xl font-bold ${stat.color} flex items-center gap-1">
                ${stat.icon ? `<i data-lucide="${stat.icon}" class="w-5 h-5"></i>` : ''}
                ${stat.value}
            </div>
        </div>
    `).join('');

    lucide.createIcons();
}

function renderTradeCards(trades) {
    const container = document.getElementById('trade-cards-container');
    container.innerHTML = '';

    trades.forEach((trade, index) => {
        container.innerHTML += createTradeCard(trade, index);
    });

    // Initialize Charts & Icons after DOM update
    setTimeout(() => {
        trades.forEach((trade, index) => {
            initChart(`chart-${index}`, trade);
        });
        lucide.createIcons();
    }, 0);
}

function createTradeCard(data, index) {
    // Handle missing fields gracefully (e.g. if data format differs slightly)
    const foundAt = data.foundAt || data.timestamp || 'N/A';
    const profit = data.profit_loss || 0;
    const roi = data.real_rate_percentage || 0;
    const startAmt = data.starting_amount || 0;
    const finalBal = data.final_balance || 0;

    // Ensure contract arrays exist
    const c1 = data.contract_1 || ['?', '?'];
    const c2 = data.contract_2 || ['?', '?'];
    const c3 = data.contract_3 || ['?', '?'];

    return `
    <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-lg mb-8">
        <!-- Header -->
        <div class="p-6 border-b border-slate-700 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/50">
            <div>
                <div class="flex items-center gap-2 text-emerald-400 mb-1">
                    <i data-lucide="activity" class="w-4 h-4"></i>
                    <span class="font-bold tracking-wider text-sm uppercase">Triangular Arbitrage Executed</span>
                </div>
                <div class="text-slate-400 text-sm flex items-center gap-2">
                    <i data-lucide="clock" class="w-3.5 h-3.5"></i>
                    ${foundAt}
                </div>
            </div>
            <div class="flex gap-4">
                <div class="text-right">
                    <div class="text-slate-400 text-xs uppercase font-semibold">Net Profit</div>
                    <div class="text-emerald-400 font-bold text-xl flex items-center justify-end gap-1">
                        +${fmt(profit)}
                        <i data-lucide="trending-up" class="w-4 h-4"></i>
                    </div>
                </div>
                <div class="text-right pl-4 border-l border-slate-700">
                    <div class="text-slate-400 text-xs uppercase font-semibold">ROI</div>
                    <div class="text-emerald-400 font-bold text-xl">${fmt(roi, 4)}%</div>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
            
            <!-- Left Column: The Flow Visualization -->
            <div class="lg:col-span-2 space-y-6">
                <h3 class="text-slate-200 font-semibold mb-4 flex items-center gap-2">
                    <i data-lucide="activity" class="text-blue-400 w-5 h-5"></i> Trade Cycle Execution
                </h3>
                
                <!-- Step 1 -->
                <div class="relative pl-8 pb-8 border-l-2 border-slate-700 last:border-0 last:pb-0">
                    <div class="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-blue-500 ring-4 ring-slate-800"></div>
                    <div class="bg-slate-700/30 p-4 rounded-lg border border-slate-700/50 hover:border-blue-500/50 transition-colors">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-blue-400 font-bold text-sm">STEP 1: ENTRY</span>
                            <span class="text-xs bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded uppercase">${data.contract_direction_1 || 'N/A'}</span>
                        </div>
                        <div class="flex items-center gap-3 text-slate-200">
                            <span class="font-mono text-lg">${c1[1]}</span>
                            <i data-lucide="arrow-right" class="text-slate-500 w-4 h-4"></i>
                            <span class="font-mono text-lg font-bold text-white">${c1[0]}</span>
                        </div>
                        <div class="mt-2 text-sm text-slate-400 font-mono">
                            Used <span class="text-slate-300">${fmt(startAmt)}</span> to get <span class="text-yellow-400">${fmtCrypto(data.acquired_coin_t1 || 0)} ${c1[0]}</span>
                        </div>
                    </div>
                </div>

                <!-- Step 2 -->
                <div class="relative pl-8 pb-8 border-l-2 border-slate-700 last:border-0 last:pb-0">
                    <div class="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-purple-500 ring-4 ring-slate-800"></div>
                    <div class="bg-slate-700/30 p-4 rounded-lg border border-slate-700/50 hover:border-purple-500/50 transition-colors">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-purple-400 font-bold text-sm">STEP 2: CONVERSION</span>
                            <span class="text-xs bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded uppercase">${data.contract_direction_2 || 'N/A'}</span>
                        </div>
                        <div class="flex items-center gap-3 text-slate-200">
                            <span class="font-mono text-lg">${c2[0]}</span>
                            <i data-lucide="arrow-right" class="text-slate-500 w-4 h-4"></i>
                            <span class="font-mono text-lg font-bold text-white">${c2[1]}</span>
                        </div>
                        <div class="mt-2 text-sm text-slate-400 font-mono">
                            Converted ${c2[0]} to <span class="text-green-400">${fmt(data.acquired_coin_t2 || 0)} ${c2[1]}</span>
                        </div>
                    </div>
                </div>

                <!-- Step 3 -->
                <div class="relative pl-8 border-l-2 border-transparent">
                    <div class="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-emerald-500 ring-4 ring-slate-800"></div>
                    <div class="bg-slate-700/30 p-4 rounded-lg border border-slate-700/50 hover:border-emerald-500/50 transition-colors">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-emerald-400 font-bold text-sm">STEP 3: EXIT</span>
                            <span class="text-xs bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded uppercase">${data.contract_direction_3 || 'N/A'}</span>
                        </div>
                        <div class="flex items-center gap-3 text-slate-200">
                            <span class="font-mono text-lg">${c3[0]}</span>
                            <i data-lucide="arrow-right" class="text-slate-500 w-4 h-4"></i>
                            <span class="font-mono text-lg font-bold text-white">${c3[1]}</span>
                        </div>
                        <div class="mt-2 text-sm text-slate-400 font-mono">
                            Sold ${c3[0]} to acquire <span class="text-emerald-400 font-bold">${fmt(data.acquired_coin_t3 || 0)} ${c3[1]}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Column: Visual Summary -->
            <div class="flex flex-col gap-6">
                <!-- Visual Triangle -->
                <div class="bg-slate-900 p-6 rounded-xl border border-slate-700 flex flex-col items-center justify-center relative overflow-hidden h-[300px]">
                    <h4 class="absolute top-4 left-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Route Visualizer</h4>
                    
                    <div class="relative w-48 h-48 mt-4">
                        <!-- Node 1: Start/End -->
                        <div class="absolute bottom-0 left-0 transform -translate-x-1/4 translate-y-1/4 bg-blue-900/80 border border-blue-500 text-blue-100 w-16 h-16 rounded-full flex items-center justify-center font-bold z-10 shadow-[0_0_15px_rgba(59,130,246,0.5)] text-xs">
                            ${c1[1]}
                        </div>
                        
                        <!-- Node 2 -->
                        <div class="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/4 bg-yellow-900/80 border border-yellow-500 text-yellow-100 w-16 h-16 rounded-full flex items-center justify-center font-bold z-10 shadow-[0_0_15px_rgba(234,179,8,0.5)] text-xs">
                            ${c1[0]}
                        </div>
                        
                        <!-- Node 3 -->
                        <div class="absolute bottom-0 right-0 transform translate-x-1/4 translate-y-1/4 bg-green-900/80 border border-green-500 text-green-100 w-16 h-16 rounded-full flex items-center justify-center font-bold z-10 shadow-[0_0_15px_rgba(34,197,94,0.5)] text-xs">
                            ${c2[1]}
                        </div>

                        <!-- Connecting Lines (SVG) -->
                        <svg class="absolute inset-0 w-full h-full pointer-events-none overflow-visible">
                            <defs>
                                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                                    <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
                                </marker>
                            </defs>
                            <!-- 1 -> 2 -->
                            <line x1="20%" y1="80%" x2="40%" y2="25%" stroke="#475569" stroke-width="2" class="dash-line" marker-end="url(#arrowhead)" />
                            <!-- 2 -> 3 -->
                            <line x1="60%" y1="25%" x2="80%" y2="80%" stroke="#475569" stroke-width="2" class="dash-line" marker-end="url(#arrowhead)" />
                            <!-- 3 -> 1 -->
                            <line x1="70%" y1="90%" x2="30%" y2="90%" stroke="#10b981" stroke-width="2" marker-end="url(#arrowhead)" />
                        </svg>
                    </div>
                </div>

                <!-- Start vs End Chart -->
                <div class="bg-slate-900 p-4 rounded-xl border border-slate-700 flex-1 min-h-[200px] flex flex-col">
                     <h4 class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Capital Growth</h4>
                     <div class="flex-1 w-full relative">
                        <canvas id="chart-${index}"></canvas>
                     </div>
                </div>
            </div>
        </div>

        <!-- Raw JSON Toggle -->
        <div class="border-t border-slate-700">
            <button 
                onclick="toggleRawData('raw-${index}', this)"
                class="w-full p-3 flex items-center justify-center gap-2 text-slate-500 hover:text-slate-300 hover:bg-slate-800/50 transition-all text-sm font-medium"
            >
                <i data-lucide="database" class="w-3.5 h-3.5"></i>
                <span class="btn-text">Show Raw JSON</span>
                <i data-lucide="chevron-down" class="w-3.5 h-3.5 icon-state"></i>
            </button>
            
            <div id="raw-${index}" class="hidden bg-slate-950 p-6 overflow-x-auto border-t border-black transition-all">
                <pre class="text-xs font-mono text-emerald-400 whitespace-pre-wrap">${JSON.stringify(data, null, 2)}</pre>
            </div>
        </div>
    </div>
    `;
}

function initChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Start', 'End'],
            datasets: [{
                label: 'Amount',
                data: [data.starting_amount, data.final_balance],
                backgroundColor: [
                    'rgba(100, 116, 139, 0.8)', // Slate-500
                    'rgba(16, 185, 129, 0.8)'   // Emerald-500
                ],
                borderColor: [
                    '#64748b',
                    '#10b981'
                ],
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleColor: '#f8fafc',
                    bodyColor: '#f8fafc',
                    borderColor: '#334155',
                    borderWidth: 1,
                    callbacks: {
                        label: function (context) {
                            return context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                y: {
                    display: false,
                    // min: data.starting_amount * 0.999 // Zoom in slightly
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}

function toggleRawData(id, btn) {
    const el = document.getElementById(id);
    const isHidden = el.classList.contains('hidden');
    const btnText = btn.querySelector('.btn-text');
    const icon = btn.querySelector('.icon-state');

    if (isHidden) {
        el.classList.remove('hidden');
        btnText.textContent = "Hide Raw Data";
        icon.setAttribute('data-lucide', 'chevron-up');
    } else {
        el.classList.add('hidden');
        btnText.textContent = "Show Raw JSON";
        icon.setAttribute('data-lucide', 'chevron-down');
    }
    lucide.createIcons();
}

connectLogs();
