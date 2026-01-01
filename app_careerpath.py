import pandas as pd
import json

# === 1. 把你的 Python 核心逻辑复制过来 ===
class BaZiLogic:
    def __init__(self):
        self.generates = {0: 1, 1: 2, 2: 3, 3: 4, 4: 0}
        self.controls = {0: 2, 2: 4, 4: 1, 1: 3, 3: 0}
        # 0:Wood, 1:Fire, 2:Earth, 3:Metal, 4:Water

    def calculate_ten_gods(self, day_master, other_element):
        # 简化的极性计算 (基于 app_careerpath.py 的逻辑)
        dm_pol = day_master % 2
        other_pol = other_element % 2
        same_polarity = (dm_pol == other_pol)

        if day_master == other_element: return 2 if same_polarity else 3 # Friend/Rob Wealth
        if self.generates.get(day_master) == other_element: return 4 if same_polarity else 5 # Output
        if self.controls.get(day_master) == other_element: return 7 if same_polarity else 6 # Wealth
        if self.generates.get(other_element) == day_master: return 0 if same_polarity else 1 # Resource
        if self.controls.get(other_element) == day_master: return 9 if same_polarity else 8 # Power
        return -1

    def get_vector(self, row):
        # 1. 十神计数 (10维)
        tg_count = [0] * 10
        dm = int(row['dayTianElement'])
        # Python代码里只用了这几柱做特征
        pillars = [row['yearTianElement'], row['monthTianElement'], 
                   row['yearDiElement'], row['monthDiElement'], row['dayDiElement']]
        
        for elem in pillars:
            tg = self.calculate_ten_gods(dm, int(elem))
            if tg >= 0: tg_count[tg] += 1
            
        # 2. 五行计数 (5维)
        e_count = [0] * 5
        all_pillars = [row['yearTianElement'], row['monthTianElement'], row['dayTianElement'], 
                       row['yearDiElement'], row['monthDiElement'], row['dayDiElement']]
        for elem in all_pillars:
            e_count[int(elem)] += 1
            
        return tg_count + e_count # 返回 15 维向量

# === 2. 读取 Excel 并转换 ===
try:
    df = pd.read_excel("cleaned_billionnaire_306_fpd.xlsx")
    
    # 清洗数据，确保是数字
    cols = ['yearTianElement', 'monthTianElement', 'dayTianElement', 
            'yearDiElement', 'monthDiElement', 'dayDiElement']
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    logic = BaZiLogic()
    export_data = []
    
    # 提取行业名称的简单映射 (假设 industryElement 是代码)
    # 这里的映射需要根据你 Excel 的实际情况调整，这里做个示例
    # 假设 Excel 里有一列 'industry' 是文字，或者 'industryElement' 是数字
    
    for _, row in df.iterrows():
        vector = logic.get_vector(row)
        
        # 尝试获取名字和行业，如果没有则用默认值
        name = row.get('Name', row.get('name', 'Unknown'))
        industry = row.get('Industry', row.get('industry', 'General'))
        source = row.get('Source', row.get('source', ''))
        dm_val = int(row['dayTianElement'])
        dm_names = ['Wood', 'Fire', 'Earth', 'Metal', 'Water']
        
        export_data.append({
            "name": name,
            "industry": industry,
            "source": str(source),
            "vector": vector,  # 这里的 vector 现在是 15 维的了！
            "dayMaster": dm_names[dm_val]
        })

    # === 3. 输出为 JS 格式 ===
    print("转换成功！请复制下面的内容替换 script.js 里的 billionaireDatabase 变量：")
    print("-" * 50)
    print(f"const billionaireDatabase = {json.dumps(export_data, indent=4)};")
    print("-" * 50)
    
    # 顺便存个文件
    with open("db_output.js", "w", encoding='utf-8') as f:
        f.write(f"const billionaireDatabase = {json.dumps(export_data, indent=4)};")

except Exception as e:
    print(f"错误: {e}")
    print("请确保 'cleaned_billionnaire_306_fpd.xlsx' 文件在当前目录下。")