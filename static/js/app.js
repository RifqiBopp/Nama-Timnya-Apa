/* ========================================
   ECONOMIC RESILIENCE INTELLIGENCE
   Main Application Logic — Azure AI Theme
   ======================================== */

// --- TAB NAVIGATION ---
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.mob-btn').forEach(b => b.classList.remove('active'));
    
    document.getElementById(tabId).classList.add('active');
    document.querySelectorAll(`[data-tab="${tabId}"]`).forEach(b => b.classList.add('active'));
}

// --- COUNTER ANIMATION ---
function animateCounters() {
    document.querySelectorAll('[data-count]').forEach(el => {
        const target = parseFloat(el.getAttribute('data-count'));
        const decimals = el.getAttribute('data-decimals') ? parseInt(el.getAttribute('data-decimals')) : 0;
        const duration = 1200;
        const start = performance.now();
        
        function update(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = (eased * target).toFixed(decimals);
            if (progress < 1) requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
    });
}

// --- PLOTLY AZURE DARK THEME ---
const plotlyDarkLayout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Inter, Segoe UI, sans-serif', color: '#9aa0b4', size: 11 },
    margin: { l: 50, r: 20, t: 10, b: 40 },
    xaxis: {
        gridcolor: 'rgba(255,255,255,0.03)',
        zerolinecolor: 'rgba(255,255,255,0.05)',
        tickfont: { size: 10 }
    },
    yaxis: {
        gridcolor: 'rgba(255,255,255,0.03)',
        zerolinecolor: 'rgba(255,255,255,0.05)',
        tickfont: { size: 10 }
    },
    hoverlabel: {
        bgcolor: '#1c1c24',
        bordercolor: 'rgba(0,120,212,0.3)',
        font: { family: 'Inter, Segoe UI', size: 11, color: '#e8eaed' }
    },
    showlegend: false
};

const plotlyConfig = { responsive: true, displayModeBar: false };

// --- AZURE COLOR PALETTE ---
const azureColors = {
    tangguh: '#00C48C',
    transisi: '#E6A817',
    rentan: '#E34856',
    blue: '#0078D4',
    light: '#4BA4E8',
    purple: '#7B68EE',
    cyan: '#0097A7'
};

// --- DASHBOARD: BAR CHART ---
function renderBarChart(data) {
    const sorted = [...data].sort((a, b) => b.Economic_Resilience_Index - a.Economic_Resilience_Index).slice(0, 12);
    const colors = sorted.map(d => {
        if (d.Status === 'Tangguh') return azureColors.tangguh;
        if (d.Status === 'Transisi') return azureColors.transisi;
        return azureColors.rentan;
    });

    const trace = {
        x: sorted.map(d => d.Provinsi),
        y: sorted.map(d => d.Economic_Resilience_Index),
        type: 'bar',
        marker: {
            color: colors,
            line: { color: 'rgba(255,255,255,0.06)', width: 1 },
            cornerradius: 4
        },
        hovertemplate: '<b>%{x}</b><br>Skor: %{y:.2f}<extra></extra>'
    };

    const layout = {
        ...plotlyDarkLayout,
        margin: { l: 45, r: 16, t: 8, b: 75 },
        xaxis: { ...plotlyDarkLayout.xaxis, tickangle: -35, tickfont: { size: 10, family: 'Inter', color: '#9aa0b4' } },
        yaxis: { ...plotlyDarkLayout.yaxis, title: { text: 'Indeks Ketahanan', font: { size: 10 } }, range: [0, 11] },
        bargap: 0.35
    };

    Plotly.newPlot('chart-bar', [trace], layout, plotlyConfig);
}

// --- CHOROPLETH MAP ---
function renderMap(data) {
    const trace = {
        type: 'scattergeo',
        lat: getProvinceLat(data),
        lon: getProvinceLon(data),
        text: data.map(d => `<b>${d.Provinsi}</b><br>Skor: ${d.Economic_Resilience_Index}<br>Status: ${d.Status}`),
        hoverinfo: 'text',
        marker: {
            size: data.map(d => Math.max(7, d.Economic_Resilience_Index * 3.2)),
            color: data.map(d => d.Economic_Resilience_Index),
            colorscale: [[0, '#E34856'], [0.35, '#E6A817'], [0.65, '#0078D4'], [1, '#00C48C']],
            cmin: 1, cmax: 10,
            opacity: 0.85,
            line: { color: 'rgba(255,255,255,0.2)', width: 1 },
            colorbar: {
                title: { text: 'ERI', font: { color: '#9aa0b4', size: 10 } },
                tickfont: { color: '#9aa0b4', size: 9 },
                bgcolor: 'rgba(0,0,0,0)',
                bordercolor: 'rgba(255,255,255,0.04)',
                len: 0.5, thickness: 10
            }
        }
    };

    const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { l: 0, r: 0, t: 0, b: 0 },
        geo: {
            scope: 'asia',
            resolution: 50,
            center: { lat: -2.5, lon: 118 },
            projection: { type: 'natural earth', scale: 3.8 },
            showland: true, landcolor: 'rgba(28,28,36,0.7)',
            showocean: true, oceancolor: 'rgba(15,15,19,0.9)',
            showcoastlines: true, coastlinecolor: 'rgba(255,255,255,0.06)',
            showframe: false,
            bgcolor: 'rgba(0,0,0,0)',
            showlakes: false,
            showcountries: true, countrycolor: 'rgba(255,255,255,0.04)'
        },
        hoverlabel: {
            bgcolor: '#1c1c24',
            bordercolor: 'rgba(0,120,212,0.3)',
            font: { family: 'Inter', size: 11, color: '#e8eaed' }
        }
    };

    Plotly.newPlot('chart-map', [trace], layout, plotlyConfig);
}

// --- SCATTER (CLUSTERING) ---
function renderScatter(data) {
    const clusters = [
        { name: 'Tangguh', color: azureColors.tangguh, status: 'Tangguh' },
        { name: 'Transisi', color: azureColors.transisi, status: 'Transisi' },
        { name: 'Rentan', color: azureColors.rentan, status: 'Rentan' }
    ];

    const traces = clusters.map(c => {
        const filtered = data.filter(d => d.Status === c.status);
        return {
            x: filtered.map(d => d.Volume_QRIS_Juta),
            y: filtered.map(d => d.PDRB_Triliun),
            text: filtered.map(d => d.Provinsi),
            mode: 'markers',
            name: c.name,
            marker: {
                size: filtered.map(d => Math.max(9, d.Economic_Resilience_Index * 3.5)),
                color: c.color,
                opacity: 0.8,
                line: { color: 'rgba(255,255,255,0.15)', width: 1 }
            },
            hovertemplate: '<b>%{text}</b><br>QRIS: %{x} Juta<br>PDRB: Rp%{y} T<extra>' + c.name + '</extra>'
        };
    });

    const layout = {
        ...plotlyDarkLayout,
        showlegend: true,
        legend: { font: { size: 10 }, bgcolor: 'rgba(0,0,0,0)', x: 0.02, y: 0.98 },
        xaxis: {
            ...plotlyDarkLayout.xaxis,
            title: { text: 'Volume QRIS (Juta Transaksi)', font: { size: 11 } },
            type: 'log'
        },
        yaxis: {
            ...plotlyDarkLayout.yaxis,
            title: { text: 'PDRB (Triliun Rupiah)', font: { size: 11 } },
            type: 'log'
        },
        margin: { l: 55, r: 16, t: 8, b: 45 }
    };

    Plotly.newPlot('chart-scatter', traces, layout, plotlyConfig);
}

// --- TREND LINE CHART ---
function renderTrendChart(trendData, provinces) {
    const top5 = [...provinces].sort((a, b) => b.Economic_Resilience_Index - a.Economic_Resilience_Index).slice(0, 5);
    const lineColors = [azureColors.tangguh, azureColors.light, azureColors.blue, azureColors.purple, azureColors.transisi];
    
    const traces = top5.map((prov, i) => {
        const provTrend = trendData.filter(t => t.Provinsi === prov.Provinsi);
        return {
            x: provTrend.map(t => t.Quarter),
            y: provTrend.map(t => t.Volume_QRIS_Juta),
            name: prov.Provinsi,
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: lineColors[i], width: 2, shape: 'spline' },
            marker: { size: 4, color: lineColors[i] },
            hovertemplate: '<b>' + prov.Provinsi + '</b><br>%{x}<br>QRIS: %{y:.1f} Juta<extra></extra>'
        };
    });

    const layout = {
        ...plotlyDarkLayout,
        showlegend: true,
        legend: { font: { size: 9, color: '#9aa0b4' }, bgcolor: 'rgba(0,0,0,0)', orientation: 'h', y: -0.22 },
        margin: { l: 45, r: 16, t: 8, b: 55 },
        xaxis: { ...plotlyDarkLayout.xaxis, tickfont: { size: 9 } },
        yaxis: { ...plotlyDarkLayout.yaxis, title: { text: 'Volume QRIS (Juta)', font: { size: 10 } } }
    };

    Plotly.newPlot('chart-trend', traces, layout, plotlyConfig);
}

// --- PDRB TREND ---
function renderPDRBTrend(trendData, provinces) {
    const top5 = [...provinces].sort((a, b) => b.PDRB_Triliun - a.PDRB_Triliun).slice(0, 5);
    const colors = [azureColors.tangguh, azureColors.light, azureColors.blue, azureColors.purple, azureColors.transisi];
    
    const traces = top5.map((prov, i) => {
        const provTrend = trendData.filter(t => t.Provinsi === prov.Provinsi);
        return {
            x: provTrend.map(t => t.Quarter),
            y: provTrend.map(t => t.PDRB_Triliun),
            name: prov.Provinsi,
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: colors[i], width: 2, shape: 'spline' },
            marker: { size: 4 },
            hovertemplate: '<b>' + prov.Provinsi + '</b><br>%{x}<br>PDRB: Rp%{y:.1f} T<extra></extra>'
        };
    });

    const layout = {
        ...plotlyDarkLayout,
        showlegend: true,
        legend: { font: { size: 9, color: '#9aa0b4' }, bgcolor: 'rgba(0,0,0,0)', orientation: 'h', y: -0.22 },
        margin: { l: 55, r: 16, t: 8, b: 55 },
        yaxis: { ...plotlyDarkLayout.yaxis, title: { text: 'PDRB (Triliun Rp)', font: { size: 10 } } }
    };

    Plotly.newPlot('chart-pdrb-trend', traces, layout, plotlyConfig);
}

// --- PROVINCE DETAIL ---
async function loadProvinceDetail(name) {
    const res = await fetch(`/api/province/${encodeURIComponent(name)}`);
    const d = await res.json();
    if (d.error) return;

    document.getElementById('detail-name').textContent = d.Provinsi;
    document.getElementById('detail-score').innerHTML = d.Economic_Resilience_Index + '<span>/10</span>';
    document.getElementById('detail-pdrb').textContent = 'Rp ' + d.PDRB_Triliun + ' T';
    document.getElementById('detail-qris').textContent = d.Volume_QRIS_Juta + ' Juta';
    document.getElementById('detail-poverty').textContent = d.Tingkat_Kemiskinan_Persen + '%';
    document.getElementById('detail-digital').textContent = d.Digital_Adoption_Score + '/100';

    const badgeEl = document.getElementById('detail-badge');
    const cls = d.Status === 'Tangguh' ? 'badge-tangguh' : d.Status === 'Transisi' ? 'badge-transisi' : 'badge-rentan';
    badgeEl.className = 'badge ' + cls;
    badgeEl.textContent = d.Status;

    // Recommendation
    const rec = d.recommendation;
    const recEl = document.getElementById('detail-recommendation');
    recEl.className = 'recommendation ' + rec.level;
    recEl.innerHTML = `
        <h4>${rec.title}</h4>
        <p>${rec.text}</p>
        <ul>${rec.actions.map(a => `<li><span style="color:var(--azure-light)">&#10003;</span> ${a}</li>`).join('')}</ul>
    `;

    // Radar
    if (d.PDRB_Triliun && d.Volume_QRIS_Juta) {
        renderRadar(d);
    }
}

function renderRadar(d) {
    const maxPDRB = 3900, maxQRIS = 1580, maxPoverty = 30;
    const trace = {
        type: 'scatterpolar',
        r: [
            (d.PDRB_Triliun / maxPDRB) * 100,
            (d.Volume_QRIS_Juta / maxQRIS) * 100,
            ((maxPoverty - d.Tingkat_Kemiskinan_Persen) / maxPoverty) * 100,
            d.Digital_Adoption_Score,
            d.Economic_Resilience_Index * 10
        ],
        theta: ['PDRB', 'Volume QRIS', 'Anti-Kemiskinan', 'Adopsi Digital', 'Ketahanan'],
        fill: 'toself',
        fillcolor: 'rgba(0,120,212,0.12)',
        line: { color: '#4BA4E8', width: 2 },
        marker: { size: 4, color: '#4BA4E8' }
    };

    const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { l: 55, r: 55, t: 35, b: 35 },
        polar: {
            bgcolor: 'rgba(0,0,0,0)',
            radialaxis: {
                visible: true, range: [0, 100],
                gridcolor: 'rgba(255,255,255,0.04)',
                tickfont: { color: '#5a6178', size: 8 },
                linecolor: 'rgba(255,255,255,0.04)'
            },
            angularaxis: {
                gridcolor: 'rgba(255,255,255,0.04)',
                tickfont: { color: '#9aa0b4', size: 9 },
                linecolor: 'rgba(255,255,255,0.04)'
            }
        },
        showlegend: false,
        font: { family: 'Inter, Segoe UI' }
    };

    Plotly.newPlot('chart-radar', [trace], layout, plotlyConfig);
}

// --- TABLE SORTING ---
let sortDir = false;
function sortTable(colIdx, isNumeric) {
    const table = document.getElementById('clusterTable');
    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.rows);
    sortDir = !sortDir;
    rows.sort((a, b) => {
        let va = a.cells[colIdx].innerText.trim();
        let vb = b.cells[colIdx].innerText.trim();
        if (isNumeric) return sortDir ? parseFloat(va) - parseFloat(vb) : parseFloat(vb) - parseFloat(va);
        return sortDir ? va.localeCompare(vb) : vb.localeCompare(va);
    });
    rows.forEach(r => tbody.appendChild(r));
}

// --- PROVINCE COORDINATES ---
function getProvinceLat(data) {
    const coords = {
        'Aceh': 4.7, 'Sumatera Utara': 2.5, 'Sumatera Barat': -0.9, 'Riau': 1.7,
        'Jambi': -1.6, 'Sumatera Selatan': -3.3, 'Bengkulu': -3.8, 'Lampung': -4.7,
        'Kep. Bangka Belitung': -2.7, 'Kep. Riau': 3.9, 'DKI Jakarta': -6.2,
        'Jawa Barat': -6.9, 'Jawa Tengah': -7.15, 'DI Yogyakarta': -7.8,
        'Jawa Timur': -7.5, 'Banten': -6.4, 'Bali': -8.4,
        'Nusa Tenggara Barat': -8.6, 'Nusa Tenggara Timur': -8.7,
        'Kalimantan Barat': -0.0, 'Kalimantan Tengah': -1.5,
        'Kalimantan Selatan': -3.1, 'Kalimantan Timur': 1.0, 'Kalimantan Utara': 3.1,
        'Sulawesi Utara': 0.6, 'Sulawesi Tengah': -1.4, 'Sulawesi Selatan': -3.7,
        'Sulawesi Tenggara': -4.0, 'Gorontalo': 0.5, 'Sulawesi Barat': -2.8,
        'Maluku': -3.2, 'Maluku Utara': 1.6, 'Papua Barat': -1.4, 'Papua': -4.0,
        'Papua Tengah': -3.5, 'Papua Pegunungan': -4.1, 'Papua Selatan': -6.5, 'Papua Barat Daya': -2.0
    };
    return data.map(d => coords[d.Provinsi] || -2.5);
}

function getProvinceLon(data) {
    const coords = {
        'Aceh': 96.7, 'Sumatera Utara': 99.0, 'Sumatera Barat': 100.4, 'Riau': 102.1,
        'Jambi': 103.6, 'Sumatera Selatan': 104.7, 'Bengkulu': 102.3, 'Lampung': 105.0,
        'Kep. Bangka Belitung': 106.4, 'Kep. Riau': 108.0, 'DKI Jakarta': 106.8,
        'Jawa Barat': 107.6, 'Jawa Tengah': 110.4, 'DI Yogyakarta': 110.4,
        'Jawa Timur': 112.7, 'Banten': 106.2, 'Bali': 115.2,
        'Nusa Tenggara Barat': 117.0, 'Nusa Tenggara Timur': 121.0,
        'Kalimantan Barat': 109.3, 'Kalimantan Tengah': 113.5,
        'Kalimantan Selatan': 115.4, 'Kalimantan Timur': 116.4, 'Kalimantan Utara': 117.4,
        'Sulawesi Utara': 124.8, 'Sulawesi Tengah': 121.4, 'Sulawesi Selatan': 120.0,
        'Sulawesi Tenggara': 122.5, 'Gorontalo': 122.4, 'Sulawesi Barat': 119.4,
        'Maluku': 129.0, 'Maluku Utara': 127.8, 'Papua Barat': 133.8, 'Papua': 138.5,
        'Papua Tengah': 137.0, 'Papua Pegunungan': 138.9, 'Papua Selatan': 139.5, 'Papua Barat Daya': 132.0
    };
    return data.map(d => coords[d.Provinsi] || 118);
}
