async function calculate() {
    const dob = document.getElementById('dob').value;
    const tob = document.getElementById('tob').value;
    const gender = document.getElementById('gender').value;
    const state = document.getElementById('state').value;

    if (!dob || !tob) {
        alert("Please select Date and Time of Birth");
        return;
    }

    // Show sections if previously hidden
    document.getElementById('pillarsCard').style.display = 'block';
    document.getElementById('col2').style.display = 'block';
    document.getElementById('col3').style.display = 'block';

    // Scroll to visualization part
    document.getElementById('pillarsCard').scrollIntoView({ behavior: 'smooth' });

    const aiContainer = document.getElementById('aiContent');
    aiContainer.innerHTML = '<div class="loading">🤖 AI is analyzing your destiny...<br>(Fetching Real-time Billionaire Data)</div>';

    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dob, tob, gender, state })
        });

        handleResponse(response);
    } catch (error) {
        console.error(error);
        alert('An error occurred');
    }
}

async function handleResponse(response) {
    if (response.status === 401) {
        window.location.href = 'login.html';
        return;
    }
    const data = await response.json();
    if (data.error) {
        alert(data.error);
        return;
    }
    renderResults(data);
}

// Element Mapping
const GAN_ZHI_ELEMENTS = {
    '甲': 'wood', '乙': 'wood', '寅': 'wood', '卯': 'wood',
    '丙': 'fire', '丁': 'fire', '巳': 'fire', '午': 'fire',
    '戊': 'earth', '己': 'earth', '辰': 'earth', '戌': 'earth', '丑': 'earth', '未': 'earth',
    '庚': 'metal', '辛': 'metal', '申': 'metal', '酉': 'metal',
    '壬': 'water', '癸': 'water', '亥': 'water', '子': 'water'
};

const IND_COLORS = {
    'Tech': 'fire', 'Technology': 'fire', 'Internet': 'fire', 'Energy': 'fire',
    'Real Estate': 'earth', 'Construction': 'earth', 'Insurance': 'earth',
    'Finance': 'metal', 'Investments': 'metal', 'Jewelry': 'metal',
    'Retail': 'wood', 'Fashion': 'wood', 'Education': 'wood', 'Furniture': 'wood',
    'Logistics': 'water', 'Shipping': 'water', 'Trading': 'water', 'Beverage': 'water'
};

function getElemClass(char) {
    const el = GAN_ZHI_ELEMENTS[char] || '';
    return el ? `elem-${el}` : '';
}

function getIndClass(ind) {
    for (const [key, val] of Object.entries(IND_COLORS)) {
        if (ind.includes(key)) return `elem-${val}`;
    }
    return 'elem-metal'; // Default gold
}

function renderResults(data) {
    renderPillars(data.bazi.pillars, data.bazi.shishen);
    renderRadar(data.bazi.wuxing);
    renderMatches(data.matches);
    renderCareer(data.careers);
    document.getElementById('aiContent').innerHTML = marked.parse(data.ai_analysis);
}

function renderCareer(careers) {
    const div = document.getElementById('careerDisplay');
    if (!careers || careers.length === 0) {
        div.innerHTML = '<p>No specific data trends found.</p>';
        return;
    }

    let html = '';
    careers.forEach((c, i) => {
        let indName = c[0];
        let percent = 90 - (i * 10);
        let colorClass = getIndClass(indName);

        html += `
            <div style="margin-bottom:15px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="${colorClass}" style="font-weight:bold; font-size:1.1rem;">${indName}</span>
                    <span style="color:#fff; font-size:0.9rem;">${percent}% Match</span>
                </div>
                <div style="height:6px; background:rgba(255,255,255,0.1); border-radius:3px; margin-top:5px;">
                    <div style="height:100%; width:${percent}%; background:linear-gradient(90deg, currentColor, transparent); border-radius:3px; color:inherit;" class="${colorClass}"></div>
                </div>
            </div>
        `;
    });
    div.innerHTML = html;
}

function renderPillars(pillars, shishen) {
    const display = document.getElementById('pillarsDisplay');
    const labels = ['Year Pillar', 'Month Pillar', 'Day Pillar', 'Time Pillar'];
    const keys = ['year', 'month', 'day', 'time'];

    let html = '';
    keys.forEach((k, i) => {
        const gan = pillars[k][0];
        const zhi = pillars[k][1];
        const ganClass = getElemClass(gan);
        const zhiClass = getElemClass(zhi);

        const ganShen = shishen[k + '_gan'] || '-';
        const zhiShen = shishen[k + '_zhi']?.[0] || '-';

        html += `
            <div class="pillar-box" style="display:flex; flex-direction:column; align-items:center;">
                <div class="pillar-label" style="margin-bottom:5px; font-weight:bold;">${labels[i]}</div>
                <div class="shen" style="font-size:0.8rem; margin-bottom:5px;">${ganShen}</div>
                <div class="gan ${ganClass}" style="margin-bottom:5px;">${gan}</div>
                <div class="zhi ${zhiClass}" style="margin-bottom:5px;">${zhi}</div>
                <div class="shen" style="font-size:0.8rem;">${zhiShen}</div>
            </div>
        `;
    });
    display.innerHTML = html;
}

let chartInstance = null;
function renderRadar(wuxing) {
    const chartDom = document.getElementById('radarChart');
    if (chartInstance) {
        chartInstance.dispose();
    }
    chartInstance = echarts.init(chartDom, 'dark');

    const keys = ['金', '木', '水', '火', '土'];
    const values = keys.map(k => wuxing[k]);
    const maxVal = Math.max(...values, 5);

    const option = {
        backgroundColor: 'transparent',
        radar: {
            indicator: [
                { name: 'Metal (金)', max: maxVal, color: '#d4af37' },
                { name: 'Wood (木)', max: maxVal, color: '#00fa9a' },
                { name: 'Water (水)', max: maxVal, color: '#00bfff' },
                { name: 'Fire (火)', max: maxVal, color: '#ff4500' },
                { name: 'Earth (土)', max: maxVal, color: '#8b4513' }
            ],
            splitArea: {
                areaStyle: {
                    color: ['rgba(255, 255, 255, 0.05)', 'rgba(0,0,0,0)'],
                }
            },
            axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
            splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
        },
        series: [
            {
                type: 'radar',
                data: [
                    {
                        value: values,
                        name: 'Balance',
                        itemStyle: { color: '#d4af37' },
                        areaStyle: { color: 'rgba(212, 175, 55, 0.4)' },
                        lineStyle: { width: 2, type: 'solid' }
                    }
                ]
            }
        ]
    };

    chartInstance.setOption(option);
    window.addEventListener('resize', () => chartInstance.resize());
}

function renderMatches(matches) {
    const div = document.getElementById('matchDisplay');
    if (!matches || matches.length === 0) {
        div.innerHTML = '<p>No close matches found in database.</p>';
        return;
    }

    let html = '';
    matches.forEach(m => {
        html += `
            <div class="billionaire-match">
                <div class="match-score" style="min-width:60px;">${Math.round(m.score)}%</div>
                <div style="flex-grow:1;">
                    <h3 style="margin:0; font-size:1.1rem; color:#fff;">${m.name}</h3>
                    <div style="display:flex; justify-content:space-between; margin-top:5px;">
                        <span style="font-size:0.9rem; color:var(--primary);">🏢 ${m.source}</span>
                        <span style="font-size:0.85rem; color:#aaa; font-style:italic;">${m.industry}</span>
                    </div>
                </div>
            </div>
        `;
    });
    div.innerHTML = html;
}

// History Functions
async function showHistory() {
    const modal = document.getElementById('historyModal');
    const list = document.getElementById('historyList');
    modal.style.display = 'block';

    try {
        const res = await fetch('/api/history');
        const records = await res.json();

        if (records.length === 0) {
            list.innerHTML = '<p style="color:#aaa;">No history found.</p>';
            return;
        }

        let html = '<ul style="list-style:none; padding:0;">';
        records.forEach(r => {
            html += `
                <li style="padding:10px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">
                    <div onclick="loadRecord(${r.id})" style="cursor:pointer; flex-grow:1;">
                        <div style="color:#fff; font-weight:bold;">${r.birth_date}</div>
                        <div style="font-size:0.8rem; color:#888;">${r.birth_time} • ${r.state}</div>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <button onclick="loadRecord(${r.id})" style="background:var(--primary); border:none; border-radius:5px; padding:5px 10px; cursor:pointer;" title="View">👁️</button>
                        <button onclick="deleteRecord(${r.id})" style="background:rgba(255, 69, 0, 0.2); color:#ff4500; border:1px solid #ff4500; border-radius:5px; padding:5px 10px; cursor:pointer;" title="Delete">🗑️</button>
                    </div>
                </li>
            `;
        });
        html += '</ul>';
        list.innerHTML = html;

    } catch (e) {
        list.innerHTML = '<p>Error loading history.</p>';
    }
}

async function deleteRecord(id) {
    if (!confirm("Are you sure you want to delete this record forever?")) return;

    try {
        const res = await fetch(`/api/history/delete/${id}`, { method: 'DELETE' });
        if (res.ok) {
            showHistory(); // Refresh list
        } else {
            alert("Failed to delete.");
        }
    } catch (e) {
        alert("Error deleting record.");
    }
}

function closeHistory() {
    document.getElementById('historyModal').style.display = 'none';
}

async function loadRecord(id) {
    closeHistory();
    try {
        const res = await fetch(`/api/load_record/${id}`);
        handleResponse(res);
    } catch (e) {
        alert("Failed to load record");
    }
}