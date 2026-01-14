
import datetime
from lunar_python import Lunar, Solar
from bazi_lib.ganzhi import ten_deities, Gan, Zhi, wuhangs, zhi5
from bazi_lib.common import get_zhi_detail

def calculate_bazi(year, month, day, time_hour, gender='M'):
    # Create Solar date
    solar = Solar.fromYmdHms(int(year), int(month), int(day), int(time_hour), 0, 0)
    lunar = solar.getLunar()
    
    # Get Four Pillars (Ba Zi)
    # lunar_python gives us the pillars
    bazi = lunar.getEightChar()
    
    year_gan = bazi.getYearGan()
    year_zhi = bazi.getYearZhi()
    month_gan = bazi.getMonthGan()
    month_zhi = bazi.getMonthZhi()
    day_gan = bazi.getDayGan()
    day_zhi = bazi.getDayZhi()
    time_gan = bazi.getTimeGan()
    time_zhi = bazi.getTimeZhi()
    
    pillars = {
        'year': f"{year_gan}{year_zhi}",
        'month': f"{month_gan}{month_zhi}",
        'day': f"{day_gan}{day_zhi}",
        'time': f"{time_gan}{time_zhi}"
    }

    # Calculate Ten Gods (Shi Shen) relative to Day Master (Day Gan)
    me = day_gan
    
    shishen = {
        'year_gan': ten_deities[me][year_gan],
        'month_gan': ten_deities[me][month_gan],
        'time_gan': ten_deities[me][time_gan],
        # Zhis hidden stems
        'year_zhi': [ten_deities[me][g] for g in zhi5[year_zhi]],
        'month_zhi': [ten_deities[me][g] for g in zhi5[month_zhi]],
        'day_zhi': [ten_deities[me][g] for g in zhi5[day_zhi]],
        'time_zhi': [ten_deities[me][g] for g in zhi5[time_zhi]],
    }
    
    # Wu Xing Count
    wuxing_count = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    
    def add_wuxing(char):
        for wx, chars in wuhangs.items():
            if char in chars:
                wuxing_count[wx] += 1
                
    add_wuxing(year_gan)
    add_wuxing(year_zhi)
    add_wuxing(month_gan)
    add_wuxing(month_zhi)
    add_wuxing(day_gan)
    add_wuxing(day_zhi)
    add_wuxing(time_gan)
    add_wuxing(time_zhi)
    
    return {
        'pillars': pillars,
        'shishen': shishen,
        'wuxing': wuxing_count,
        'me': me,
        'gender': gender,
        'solar_date': f"{year}-{month}-{day} {time_hour}:00"
    }
