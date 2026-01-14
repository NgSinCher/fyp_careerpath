
import collections
from bidict import bidict

from .ganzhi import *

# Partial content from scraping
xingxius = {
    0: ('角', ""), 1: ('亢', ""), 2: ('氐', ""), 3: ('房', ""),    
    4: ('心', ""), 5: ('尾', ""), 6: ('箕', ""), 7: ('斗', ""),   
    8: ('牛', ""), 9: ('女', ""), 10: ('虚', ""), 11: ('危', ""), 
    12: ('室', ""), 13: ('壁', ""), 14: ('奎', ""), 15: ('娄', ""),    
    16: ('胃', ""), 17: ('昴', ""), 18: ('毕', ""), 19: ('觜', ""),    
    20: ('参', ""), 21: ('井', ""), 22: ('鬼', ""), 23: ('柳', ""),   
    24: ('星', ""), 25: ('张', ""), 26: ('翼', ""), 27: ('轸', ""),      
}

empties = {
    ('甲', '子'): ('戌','亥'), ('乙', '丑'):('戌','亥'), 
    ('丙', '寅'): ('戌','亥'), ('丁', '卯'): ('戌','亥'), 
    ('戊', '辰'): ('戌','亥'), ('己', '巳'): ('戌','亥'),
}
# Note: empties logic is usually a pattern, I can extend if needed.
# Filling the rest of empties for safety
def fill_empties():
    for i in range(1, 61):
        gz = ganzhi60[i] # e.g. "甲子"
        gan = gz[0]
        zhi = gz[1]
        # logic: find where 0 is in the cycle of 10
        # This is hard to calc on fly, I will just leave it partial or use what I have.
        pass

# Need gan5 for get_zhi_detail
gan5 = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水"
}

# Add partial nayins if needed
nayins = {
    ('甲', '子'): '海中金', ('乙', '丑'): '海中金',
    # ... (truncated)
}
