// --- 1. DATASET: 核心数据库 ---

// ⚠️ 重要：请用 Python 脚本生成的完整数据替换下面这个数组
const billionaireDatabase = [
    // 示例数据 (格式已更新为 15 维向量: 10个十神 + 5个五行)
    { 
        name: "Elon Musk (Example)", 
        industry: "Technology", 
        source: "Tesla", 
        // 向量顺序: [DR, IR, Fr, RW, EG, HO, DW, IW, DO, 7K, Wood, Fire, Earth, Metal, Water]
        vector: [1, 0, 2, 0, 1, 0, 1, 2, 0, 0,  2, 3, 1, 1, 0], 
        dayMaster: "Wood" 
    },
    // ... 在这里粘贴你的 306 条数据 ...
];

// 行业特征 (也可以根据需要更新向量长度，这里暂时只用于展示)
const industries = [
    { name: "Tech & Innovation (科技)", desc: "Requires innovation (Fire) and execution (Metal)." },
    { name: "Real Estate & Resources (房地产)", desc: "Requires stability and trust (Earth)." },
    { name: "Finance & Investment (金融)", desc: "Requires precision (Metal) and flow (Water)." },
    { name: "Media & Arts (传媒)", desc: "Requires creativity (Wood) and visibility (Fire)." },
    { name: "Logistics & Trade (贸易)", desc: "Requires movement and wisdom (Water)." }
];

// --- 2. HELPER: 基础定义 ---
const elementMap = {
    '甲': 0, '乙': 0, '寅': 0, '卯': 0, // Wood
    '丙': 1, '丁': 1, '巳': 1, '午': 1, // Fire
    '戊': 2, '己': 2, '辰': 2, '戌': 2, '丑': 2, '未': 2, // Earth
    '庚': 3, '辛': 3, '申': 3, '酉': 3, // Metal
    '壬': 4, '癸': 4, '亥': 4, '子': 4  // Water
};

const elementNames = ['Wood (木)', 'Fire (火)', 'Earth (土)', 'Metal (金)', 'Water (水)'];
const elementColors = ['#4caf50', '#f44336', '#ff9800', '#9e9e9e', '#2196f3'];
const tenGodsNames = ['DR', 'IR', 'Fr', 'RW', 'EG', 'HO', 'DW', 'IW', 'DO', '7K'];

// 五行生克关系 (0->1->2->3->4->0)
const generates = {0: 1, 1: 2, 2: 3, 3: 4, 4: 0};
const controls = {0: 2, 2: 4, 4: 1, 1: 3, 3: 0};

let myChart = null;

// --- 3. CORE LOGIC: 高级算法移植 ---

// 计算十神 (移植自 Python)
function calculateTenGods(dm, other) {
    if (dm === undefined || other === undefined) return -1;
    
    // 简化的极性逻辑 (基于 app_careerpath.py)
    const dmPol = dm % 2;
    const otherPol = other % 2;
    const samePolarity = (dmPol === otherPol);

    if (dm === other) return samePolarity ? 2 : 3; // Fr / RW
    if (generates[dm] === other) return samePolarity ? 4 : 5; // EG / HO
    if (controls[dm] === other) return samePolarity ? 7 : 6; // IW / DW (注意: Python代码中 7 是 IW)
    if (generates[other] === dm) return samePolarity ? 0 : 1; // DR / IR
    if (controls[other] === dm) return samePolarity ? 9 : 8; // 7K / DO
    return -1;
}

// 生成 15 维特征向量
function engineerFeatures(pillars) {
    const dm = elementMap[pillars.dS]; // 日主
    
    // 1. 十神计数 (10维)
    // Python 逻辑中对比了: 年干, 月干, 年支, 月支, 日支 (共5个位置)
    // 我们这里加入 时干, 时支 (如果用户填了) 以获得更精确的个人画像
    const targets = [
        pillars.yS, pillars.mS, 
        pillars.yB, pillars.mB, pillars.dB,
        pillars.hS, pillars.hB 
    ];
    
    let tgCount = Array(10).fill(0);
    targets.forEach(char => {
        const elem = elementMap[char];
        if (elem !== undefined) {
            const tg = calculateTenGods(dm, elem);
            if (tg >= 0) tgCount[tg]++;
        }
    });

    // 2. 五行计数 (5维)
    let eCount = Array(5).fill(0);
    const allChars = [pillars.yS, pillars.yB, pillars.mS, pillars.mB, pillars.dS, pillars.dB, pillars.hS, pillars.hB];
    allChars.forEach(char => {
        const type = elementMap[char];
        if (type !== undefined) eCount[type]++;
    });

    // 合并向量
    return [...tgCount, ...eCount];
}

// 余弦相似度
function cosineSim(vecA, vecB) {
    let dot = 0, normA = 0, normB = 0;
    // 确保长度一致，Python 生成的是 15 维
    const len = Math.min(vecA.length, vecB.length);
    for(let i=0; i<len; i++) { 
        dot += vecA[i] * vecB[i]; 
        normA += vecA[i]**2; 
        normB += vecB[i]**2; 
    }
    return dot / ((Math.sqrt(normA) * Math.sqrt(normB)) || 1);
}

// --- 4. MAIN FLOW: 交互逻辑 ---
function analyzeProfile() {
    const dateStr = document.getElementById('birthDate').value;
    const timeStr = document.getElementById('birthTime').value;
    
    if (!dateStr || !timeStr) { alert("Please fill in all fields."); return; }

    // 排盘 (Lunar.js)
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

    // 核心差异：现在使用 15 维向量计算
    const userVector = engineerFeatures(pillars);
    const dayMasterVal = elementMap[pillars.dS];
    const dayMasterName = elementNames[dayMasterVal];

    // UI 更新
    renderChartDisplay(pillars);
    document.getElementById('dayMasterDisplay').innerHTML = `<span style="color:${elementColors[dayMasterVal]}">${dayMasterName}</span>`;

    // 匹配计算
    const match = findBillionaireMatch(userVector, dayMasterName);
    renderMatch(match);
    
    // 推荐职业 (这里稍微简化，根据匹配到的亿万富翁的行业来推荐)
    recommendCareerFromMatch(match);
    
    // 渲染图表 (只显示五行部分，前10维是十神，后5维是五行)
    const elementVector = userVector.slice(10, 15); 
    renderRadarChart(elementVector);

    // 切换面板
    const introNotice = document.getElementById('introNotice');
    if (introNotice) introNotice.classList.add('hidden');
    
    const resultPanel = document.getElementById('resultPanel');
    resultPanel.classList.remove('hidden');
    setTimeout(() => resultPanel.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
}

function findBillionaireMatch(userVec, userDM) {
    let bestMatch = null, highestScore = -1;
    
    // 如果数据库为空，防止报错
    if (!billionaireDatabase || billionaireDatabase.length === 0) {
        alert("请先填充 billionaireDatabase 数据！");
        return { name: "No Data", industry: "N/A", score: 0 };
    }

    billionaireDatabase.forEach(bill => {
        let score = cosineSim(userVec, bill.vector);
        // 如果日主相同，给予额外加分 (保留你之前的逻辑)
        if (userDM.startsWith(bill.dayMaster)) score += 0.15;
        
        if (score > highestScore) { 
            highestScore = score; 
            bestMatch = bill; 
        }
    });
    return { ...bestMatch, score: highestScore };
}

// 根据匹配结果反推推荐
function recommendCareerFromMatch(match) {
    const list = document.getElementById('careerList');
    list.innerHTML = '';
    
    // 这里简单地展示匹配到的行业作为首选
    // 实际项目中可以统计前 5 名匹配者的行业分布
    list.innerHTML += `
        <div class="flex items-center justify-between bg-white/80 p-3 rounded-xl border border-slate-100 hover:shadow-md transition group border-l-4 border-indigo-500">
            <div>
                <div class="font-bold text-slate-800">#1 ${match.industry}</div>
                <div class="text-xs text-slate-500">Top Match based on Ten Gods Structure</div>
            </div>
            <div class="text-indigo-600 font-black text-lg">Recommended</div>
        </div>
    `;
    
    // 补充其他的通用推荐
    industries.slice(0, 2).forEach((ind, i) => {
        if (ind.name.includes(match.industry)) return; // 避免重复
        list.innerHTML += `
            <div class="flex items-center justify-between bg-white/80 p-3 rounded-xl border border-slate-100 hover:shadow-md transition group">
                <div>
                    <div class="font-bold text-slate-800">Alternative: ${ind.name}</div>
                    <div class="text-xs text-slate-500">${ind.desc}</div>
                </div>
            </div>
        `;
    });
}

// --- Helper Functions (UI渲染保持不变) ---
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

function renderMatch(match) {
    document.getElementById('matchName').innerText = match.name;
    document.getElementById('matchIndustry').innerText = match.industry;
    document.getElementById('matchBio').innerText = match.source;
    const pct = Math.min(Math.round(match.score * 100), 98);
    document.getElementById('matchScoreVal').innerText = pct;
    document.getElementById('matchScoreBar').style.width = `${pct}%`;
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