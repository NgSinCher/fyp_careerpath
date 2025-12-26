// --- 1. DATASET: 模拟后台数据库 ---
const billionaireDatabase = [
    { name: "Elon Musk", industry: "Technology", source: "Tesla, SpaceX", elements: [1, 2, 1, 3, 1], dayMaster: "Wood" },
    { name: "Bernard Arnault", industry: "Fashion & Retail", source: "LVMH", elements: [2, 1, 3, 1, 1], dayMaster: "Water" },
    { name: "Jeff Bezos", industry: "Technology", source: "Amazon", elements: [1, 1, 2, 3, 1], dayMaster: "Metal" },
    { name: "Warren Buffett", industry: "Finance", source: "Berkshire Hathaway", elements: [1, 1, 3, 2, 1], dayMaster: "Water" },
    { name: "Bill Gates", industry: "Technology", source: "Microsoft", elements: [1, 2, 1, 1, 3], dayMaster: "Water" },
    { name: "Mark Zuckerberg", industry: "Technology", source: "Facebook", elements: [2, 2, 2, 1, 1], dayMaster: "Earth" },
    { name: "Larry Ellison", industry: "Technology", source: "Software", elements: [1, 3, 1, 2, 1], dayMaster: "Fire" },
    { name: "Mukesh Ambani", industry: "Diversified", source: "Petrochemicals", elements: [2, 2, 3, 0, 1], dayMaster: "Earth" },
    { name: "Zhang Yiming", industry: "Media", source: "TikTok", elements: [1, 1, 1, 2, 3], dayMaster: "Metal" },
    { name: "Ma Huateng", industry: "Technology", source: "Internet Media", elements: [2, 1, 1, 3, 1], dayMaster: "Wood" },
    { name: "Jack Ma", industry: "Technology", source: "E-commerce", elements: [1, 2, 2, 2, 1], dayMaster: "Water" }
];

// 行业特征
const industries = [
    { name: "Tech & Innovation (科技)", code: "Fire/Metal", profile: [1, 4, 1, 3, 1], desc: "Requires innovation (Fire) and execution (Metal)." },
    { name: "Real Estate & Resources (房地产)", code: "Earth", profile: [1, 1, 5, 1, 0], desc: "Requires stability and trust (Earth)." },
    { name: "Finance & Investment (金融)", code: "Metal/Water", profile: [0, 1, 2, 4, 2], desc: "Requires precision (Metal) and flow (Water)." },
    { name: "Media & Arts (传媒)", code: "Fire/Wood", profile: [3, 4, 0, 1, 1], desc: "Requires creativity (Wood) and visibility (Fire)." },
    { name: "Logistics & Trade (贸易)", code: "Water", profile: [1, 1, 1, 2, 4], desc: "Requires movement and wisdom (Water)." }
];

// --- 2. HELPER: 五行映射 ---
const elementMap = {
    '甲': 0, '乙': 0, '寅': 0, '卯': 0,
    '丙': 1, '丁': 1, '巳': 1, '午': 1,
    '戊': 2, '己': 2, '辰': 2, '戌': 2, '丑': 2, '未': 2,
    '庚': 3, '辛': 3, '申': 3, '酉': 3,
    '壬': 4, '癸': 4, '亥': 4, '子': 4
};

const elementColors = ['#4caf50', '#f44336', '#ff9800', '#9e9e9e', '#2196f3'];
const elementNames = ['Wood (木)', 'Fire (火)', 'Earth (土)', 'Metal (金)', 'Water (水)'];

let myChart = null;

// --- 3. MAIN LOGIC: 分析函数 ---
function analyzeProfile() {
    const dateStr = document.getElementById('birthDate').value;
    const timeStr = document.getElementById('birthTime').value;
    
    if (!dateStr || !timeStr) { alert("Please fill in all fields."); return; }

    // Lunar.js 排盘
    const dateParts = dateStr.split('-');
    const timeParts = timeStr.split(':');
    const solar = Solar.fromYmdHms(parseInt(dateParts[0]), parseInt(dateParts[1]), parseInt(dateParts[2]), parseInt(timeParts[0]), parseInt(timeParts[1]), 0);
    const lunar = solar.getLunar();
    const bazi = lunar.getEightChar();
    
    const pillars = {
        yS: bazi.getYearGan(), yB: bazi.getYearZhi(),
        mS: bazi.getMonthGan(), mB: bazi.getMonthZhi(),
        dS: bazi.getDayGan(), dB: bazi.getDayZhi(),
        hS: bazi.getTimeGan(), hB: bazi.getTimeZhi()
    };

    // 计算向量
    const allChars = [pillars.yS, pillars.yB, pillars.mS, pillars.mB, pillars.dS, pillars.dB, pillars.hS, pillars.hB];
    const userVector = [0, 0, 0, 0, 0];
    allChars.forEach(char => { const type = elementMap[char]; if (type !== undefined) userVector[type]++; });

    const dayMasterVal = elementMap[pillars.dS];
    const dayMasterName = elementNames[dayMasterVal];

    // 显示结果
    renderChartDisplay(pillars);
    document.getElementById('dayMasterDisplay').innerHTML = `<span style="color:${elementColors[dayMasterVal]}">${dayMasterName}</span>`;

    const match = findBillionaireMatch(userVector, dayMasterName);
    renderMatch(match);
    recommendCareer(userVector);
    renderRadarChart(userVector);

    const resultPanel = document.getElementById('resultPanel');
    resultPanel.classList.remove('hidden');
    setTimeout(() => resultPanel.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
}

// --- Helper Functions ---
function renderChartDisplay(p) {
    const container = document.getElementById('chartDisplay');
    const labels = ['Year Pillar', 'Month Pillar', 'Day Pillar', 'Hour Pillar'];
    const stems = [p.yS, p.mS, p.dS, p.hS];
    const branches = [p.yB, p.mB, p.dB, p.hB];
    let html = '';
    for(let i=0; i<4; i++) {
        const sColor = getColorClass(stems[i]);
        const bColor = getColorClass(branches[i]);
        html += `
            <div class="bg-white/80 p-3 rounded-xl shadow-sm border border-slate-100 flex flex-col items-center ${i===2 ? 'ring-2 ring-indigo-200 bg-indigo-50/50' : ''}">
                <div class="text-[10px] uppercase tracking-wider text-slate-400 mb-2">${labels[i]}</div>
                <div class="text-2xl font-black ${sColor} leading-none mb-1">${stems[i]}</div>
                <div class="text-2xl font-black ${bColor} leading-none">${branches[i]}</div>
            </div>
        `;
    }
    container.innerHTML = html;
}

function getColorClass(char) {
    const type = elementMap[char];
    if(type === 0) return 'wood-text'; if(type === 1) return 'fire-text';
    if(type === 2) return 'earth-text'; if(type === 3) return 'metal-text';
    if(type === 4) return 'water-text'; return 'text-gray-800';
}

function cosineSim(vecA, vecB) {
    let dot = 0, normA = 0, normB = 0;
    for(let i=0; i<5; i++) { dot += vecA[i] * vecB[i]; normA += vecA[i]**2; normB += vecB[i]**2; }
    return dot / (Math.sqrt(normA) * Math.sqrt(normB) || 1);
}

function findBillionaireMatch(userVec, userDM) {
    let bestMatch = null, highestScore = -1;
    billionaireDatabase.forEach(bill => {
        let score = cosineSim(userVec, bill.elements);
        if (userDM.startsWith(bill.dayMaster)) score += 0.15;
        if (score > highestScore) { highestScore = score; bestMatch = bill; }
    });
    return { ...bestMatch, score: highestScore };
}

function renderMatch(match) {
    document.getElementById('matchName').innerText = match.name;
    document.getElementById('matchIndustry').innerText = match.industry;
    document.getElementById('matchBio').innerText = match.source;
    const pct = Math.min(Math.round(match.score * 100), 98);
    document.getElementById('matchScoreVal').innerText = pct;
    document.getElementById('matchScoreBar').style.width = `${pct}%`;
}

function recommendCareer(userVec) {
    let scoredIndustries = industries.map(ind => ({ ...ind, score: cosineSim(userVec, ind.profile) }));
    scoredIndustries.sort((a,b) => b.score - a.score);
    const list = document.getElementById('careerList');
    list.innerHTML = '';
    scoredIndustries.slice(0, 3).forEach((ind, i) => {
        list.innerHTML += `
            <div class="flex items-center justify-between bg-white/80 p-3 rounded-xl border border-slate-100 hover:shadow-md transition group">
                <div>
                    <div class="font-bold text-slate-800 group-hover:text-indigo-600 transition">#${i+1} ${ind.name}</div>
                    <div class="text-xs text-slate-500">${ind.desc}</div>
                </div>
                <div class="text-indigo-600 font-black text-lg">${Math.round(ind.score*100)}<span class="text-sm">%</span></div>
            </div>
        `;
    });
}

function renderRadarChart(data) {
    const ctx = document.getElementById('radarChart').getContext('2d');
    if(myChart) myChart.destroy();
    myChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: elementNames.map(n => n.split(' ')[1]),
            datasets: [{
                label: 'Energy Structure',
                data: data,
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                borderColor: 'rgba(99, 102, 241, 1)',
                pointBackgroundColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 2
            }]
        },
        options: {
            scales: { r: { angleLines: {color:'rgba(0,0,0,0.05)'}, grid: {color:'rgba(0,0,0,0.05)'}, suggestedMin: 0, suggestedMax: 4, ticks: { display: false } } },
            plugins: { legend: { display: false } },
            maintainAspectRatio: false
        }
    });
}