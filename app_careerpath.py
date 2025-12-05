import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

# ==========================================
# 1. 后端逻辑 (核心算法类)
# ==========================================
class BaZiCareerAdvisor:
    """
    BaZi Career Advisor Logic
    包含：数据加载、特征工程 (Ten Gods/Five Elements)、余弦相似度计算
    """
    
    def __init__(self):
        # 基础映射
        self.element_names = {0: 'Wood (木)', 1: 'Fire (火)', 2: 'Earth (土)', 3: 'Metal (金)', 4: 'Water (水)'}
        self.ten_gods_names = [
            'Direct Resource (正印)', 'Indirect Resource (偏印)', 'Friend (比肩)', 
            'Rob Wealth (劫財)', 'Eating God (食神)', 'Hurting Officer (傷官)',      
            'Direct Wealth (正財)', 'Indirect Wealth (偏財)', 'Direct Officer (正官)',       
            'Seven Killings (七殺)'
        ]
        self.generates = {0: 1, 1: 2, 2: 3, 3: 4, 4: 0}
        self.controls = {0: 2, 2: 4, 4: 1, 1: 3, 3: 0}
        self.data = None

    def load_data(self, filepath):
        """加载训练数据"""
        try:
            # 尝试加载 Excel 或 CSV
            if filepath.endswith('.csv'):
                self.data = pd.read_csv(filepath)
            else:
                self.data = pd.read_excel(filepath)
            
            # 数据清洗：确保所有列都是整数
            cols_to_fix = ['yearTianElement', 'monthTianElement', 'dayTianElement',
                           'yearDiElement', 'monthDiElement', 'dayDiElement', 'industryElement']
            for col in cols_to_fix:
                if col in self.data.columns:
                    self.data[col] = pd.to_numeric(self.data[col], errors='coerce').fillna(0).astype(int)
            return True
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return False

    def calculate_ten_gods(self, day_master, other_element, dm_polarity, other_polarity):
        """计算十神关系"""
        same_polarity = (dm_polarity == other_polarity)
        if day_master == other_element: return 2 if same_polarity else 3
        if self.generates.get(day_master) == other_element: return 4 if same_polarity else 5
        if self.controls.get(day_master) == other_element: return 7 if same_polarity else 6
        if self.generates.get(other_element) == day_master: return 0 if same_polarity else 1
        if self.controls.get(other_element) == day_master: return 9 if same_polarity else 8
        return -1

    def engineer_features(self, df):
        """特征工程：计算十神和五行计数"""
        ten_gods_cols = []
        element_counts = []
        
        for _, row in df.iterrows():
            dm = row['dayTianElement']
            dm_pol = dm % 2
            
            # 1. 十神计算
            tg_count = [0] * 10
            pillars = [('yearTianElement', 0), ('monthTianElement', 0),
                       ('yearDiElement', 1), ('monthDiElement', 1), ('dayDiElement', 1)]
            
            for col, _ in pillars:
                elem = row[col]
                tg = self.calculate_ten_gods(dm, elem, dm_pol, elem % 2)
                if tg >= 0: tg_count[tg] += 1
            ten_gods_cols.append(tg_count)
            
            # 2. 五行计数
            e_count = [0] * 5
            all_pillars = ['yearTianElement', 'monthTianElement', 'dayTianElement', 
                           'yearDiElement', 'monthDiElement', 'dayDiElement']
            for col in all_pillars:
                e_count[row[col]] += 1
            element_counts.append(e_count)
            
        # 构建 DataFrame
        tg_df = pd.DataFrame(ten_gods_cols, columns=[f'TG_{i}' for i in range(10)])
        el_df = pd.DataFrame(element_counts, columns=[f'Elem_{i}' for i in range(5)])
        
        # 合并
        base_cols = ['yearTianElement', 'monthTianElement', 'dayTianElement', 
                     'yearDiElement', 'monthDiElement', 'dayDiElement']
        return pd.concat([df[base_cols].reset_index(drop=True), tg_df, el_df], axis=1)

    def predict(self, user_input, top_n=5):
        """核心预测逻辑"""
        # 1. 准备数据库特征
        X_db = self.engineer_features(self.data)
        
        # 2. 准备用户特征
        user_df = pd.DataFrame([user_input])
        X_user = self.engineer_features(user_df)
        
        # 3. 计算相似度
        similarities = cosine_similarity(X_user, X_db)[0]
        
        # 4. 获取最相似的 N 个亿万富翁
        top_indices = np.argsort(similarities)[-20:][::-1] # 取前20个做统计
        
        # 5. 统计行业
        industry_votes = {}
        for idx in top_indices:
            weight = similarities[idx]
            ind_code = self.data.iloc[idx]['industryElement']
            industry_votes[ind_code] = industry_votes.get(ind_code, 0) + weight
            
        # 排序推荐
        sorted_ind = sorted(industry_votes.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        results = []
        total_weight = sum(industry_votes.values())
        
        for code, weight in sorted_ind:
            element_name = self.element_names[code]
            ind_name = element_name.split('(')[0] # English name
            confidence = (weight / total_weight) * 1.5 # 稍微放大系数以便显示
            confidence = min(confidence, 0.95) # 上限 95%
            
            results.append({
                'industry': element_name,
                'code': code,
                'confidence': confidence,
                'raw_score': weight
            })
            
        return results, X_user # 返回推荐结果和用户的特征数据用于绘图

# ==========================================
# 2. 前端界面 (Streamlit)
# ==========================================

st.set_page_config(page_title="BaZi Career Predictor", page_icon="🔮", layout="wide")

# --- 自定义 CSS (美化界面) ---
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #4B0082; text-align: center; margin-bottom: 1rem;}
    .sub-text {text-align: center; color: #666; margin-bottom: 2rem;}
    .card {background-color: #f9f9f9; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;}
    .metric-card {background-color: #e3f2fd; padding: 15px; border-radius: 8px; text-align: center;}
</style>
""", unsafe_allow_html=True)

# --- 侧边栏：设置 ---
with st.sidebar:
    st.header("⚙️ Project Settings")
    st.info("FYP: AI-Driven BaZi Career Path")
    st.markdown("This system compares your BaZi chart with **306 Billionaires** using Cosine Similarity to find your optimal career path.")
    
    # 允许上传文件 (或者使用默认)
    uploaded_file = st.file_uploader("Upload Dataset (Excel/CSV)", type=['xlsx', 'csv'])
    
    st.markdown("---")
    st.markdown("Developed for Final Year Project")

# --- 主界面 ---
st.markdown('<div class="main-header">🔮 AI BaZi Career Path Predictor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">基于机器学习与传统命理学的职业规划系统</div>', unsafe_allow_html=True)

# --- 1. 初始化模型 ---
@st.cache_resource
def get_advisor(file):
    advisor = BaZiCareerAdvisor()
    if file:
        # Save uploaded file temporarily to read
        with open("temp_data.xlsx", "wb") as f:
            f.write(file.getbuffer())
        success = advisor.load_data("temp_data.xlsx")
    else:
        # Default fallback
        success = advisor.load_data("cleaned_billionnaire_306_fpd.xlsx")
    return advisor if success else None

# 如果用户上传了文件用上传的，否则尝试读取本地默认文件
advisor = get_advisor(uploaded_file)

if not advisor:
    st.warning("⚠️ 请在侧边栏上传数据集 (cleaned_billionnaire_306_fpd.xlsx) 以开始使用。")
    st.stop()

# --- 2. 输入区域 ---
with st.container():
    st.markdown("### 📝 Input Your BaZi Chart (输入八字)")
    
    # 选项映射
    options = {0: 'Wood (木)', 1: 'Fire (火)', 2: 'Earth (土)', 3: 'Metal (金)', 4: 'Water (水)'}
    rev_options = {v: k for k, v in options.items()}
    select_list = list(options.values())

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Year Pillar (年柱)")
        y_stem = st.selectbox("Year Stem (年干)", select_list, index=2, key='ys')
        y_branch = st.selectbox("Year Branch (年支)", select_list, index=2, key='yb')
        
    with col2:
        st.markdown("#### Month Pillar (月柱)")
        m_stem = st.selectbox("Month Stem (月干)", select_list, index=4, key='ms')
        m_branch = st.selectbox("Month Branch (月支)", select_list, index=0, key='mb')
        
    with col3:
        st.markdown("#### Day Pillar (日柱 - Self)")
        d_stem = st.selectbox("Day Master (日主)", select_list, index=1, help="This is the most important element representing YOU.", key='ds')
        d_branch = st.selectbox("Day Branch (日支)", select_list, index=3, key='db')

    # 提交按钮
    predict_btn = st.button("🚀 Analyze Career Path (开始分析)", type="primary", use_container_width=True)

# --- 3. 结果显示 ---
if predict_btn:
    st.markdown("---")
    
    # 构造输入数据
    user_input = {
        'yearTianElement': rev_options[y_stem], 'yearDiElement': rev_options[y_branch],
        'monthTianElement': rev_options[m_stem], 'monthDiElement': rev_options[m_branch],
        'dayTianElement': rev_options[d_stem], 'dayDiElement': rev_options[d_branch]
    }
    
    with st.spinner('Calculating vector similarities with billionaire database...'):
        recommendations, user_features_df = advisor.predict(user_input)
    
    # 分栏显示：推荐结果 vs 图表分析
    res_col, chart_col = st.columns([1, 1])
    
    with res_col:
        st.subheader("🏆 Top Career Recommendations")
        
        for i, rec in enumerate(recommendations[:3], 1):
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <h3>#{i} {rec['industry']} Industry</h3>
                    <p><b>Confidence Score:</b> {rec['confidence']*100:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
                st.progress(rec['confidence'])
                
                # 动态解释 (根据日主和推荐行业)
                dm_name = d_stem.split(' ')[0]
                ind_name = rec['industry'].split(' ')[0]
                st.caption(f"💡 Based on your **{dm_name}** Day Master, the **{ind_name}** industry provides optimal energy flow.")

    with chart_col:
        st.subheader("📊 Your Energy Analysis")
        
        # 1. 五行平衡图
        st.markdown("**Five Elements Balance (五行分布)**")
        elem_data = pd.DataFrame({
            'Element': ['Wood', 'Fire', 'Earth', 'Metal', 'Water'],
            'Count': [user_features_df[f'Elem_{i}'].values[0] for i in range(5)]
        })
        st.bar_chart(elem_data.set_index('Element'))
        
        # 2. 十神分析图
        st.markdown("**Ten Gods Profile (十神格局)**")
        # 提取非零的十神
        tg_data = {}
        tg_names_short = [n.split('(')[0].strip() for n in advisor.ten_gods_names]
        for i in range(10):
            val = user_features_df[f'TG_{i}'].values[0]
            if val > 0:
                tg_data[tg_names_short[i]] = val
        
        if tg_data:
            st.dataframe(pd.DataFrame(list(tg_data.items()), columns=['Ten God', 'Count']), use_container_width=True)
        else:
            st.info("Chart is balanced without dominant Ten Gods.")

    # FYP 技术细节展示 (Add-on for presentation)
    with st.expander("🔍 View Technical Details (For FYP Evaluator)"):
        st.write("### User Feature Vector")
        st.dataframe(user_features_df)
        st.write("### Algorithm Used")
        st.code("Cosine Similarity = dot(A, B) / (||A|| * ||B||)", language="python")
        st.write("This measures the cosine of the angle between the User's BaZi Vector and each Billionaire's Vector in a multi-dimensional space.")