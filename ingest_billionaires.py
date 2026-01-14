
import pandas as pd
import mysql.connector
import json
import traceback
from config import DB_CONFIG
from bazi_logic import calculate_bazi

def ingest_data():
    print("Starting ingestion...")
    
    # 1. Connect to DB
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
    except Exception as e:
        print(f"DB Connection failed: {e}")
        return

    # 2. Read Excel
    excel_path = "c:/Users/IvanLow/OneDrive/Documents/ANTIGRAVITY_专用/dataset/updated_billionnaire.xlsx"
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"Excel read failed: {e}")
        return

    # 3. Iterate and Insert
    count = 0
    for index, row in df.iterrows():
        try:
            name = row.get('Name')
            if pd.isna(name): continue
            
            # Extract Date
            try:
                raw_month = row.get('Month')
                if pd.isna(raw_month): raw_month = row.get('month')
                
                # Month Mapping
                month_map = {
                    'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                    'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
                }
                
                if isinstance(raw_month, int):
                    month = raw_month
                elif isinstance(raw_month, str) and raw_month in month_map:
                    month = month_map[raw_month]
                else:
                    # Try direct int conversion if string is '1'
                    month = int(raw_month)

                year = int(row.get('Year'))
                day = int(row.get('Day'))
            except Exception as e:
                # If date is invalid, skip
                print(f"Skipping {name}: Date error {e} Row: {row.get('Year')}-{row.get('Month')}-{row.get('Day')}")
                continue

            gender = row.get('Gender', 'M') # Default M if missing, adjust if needed
            if gender == 'Female': gender = 'F'
            else: gender = 'M' # Simplification

            # Calculate Bazi (Assume time is 12:00 for generic)
            # Using the bazi_logic from our app
            bazi_result = calculate_bazi(year, month, day, 12, gender)
            
            day_master = bazi_result['me']
            wuxing = bazi_result['wuxing'] # {'金': 2, ...}
            
            # Map Wuxing Keys to standard if needed (Logic uses Chinese chars)
            
            # Prepare Insert
            sql = """
                INSERT INTO billionaires 
                (name, gender, birth_year, birth_month, birth_day, 
                 net_worth, industry, country, source,
                 day_master, bazi_json, wuxing_counts)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            val = (
                name, gender, year, month, day,
                str(row.get('NetWorth(billions)', '')),
                str(row.get('industryElemet1', '')), # Using industry columns
                str(row.get('Citizenship', '')),
                str(row.get('Source of Wealth', '')),
                day_master,
                json.dumps(bazi_result),
                json.dumps(wuxing)
            )
            
            cursor.execute(sql, val)
            count += 1
            if count % 10 == 0:
                print(f"Processed {count} records...")
                conn.commit()
                
        except Exception as e:
            print(f"Error processing row {index}: {e}")
            traceback.print_exc()
            continue

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Ingestion complete! Total {count} billionaires imported.")

if __name__ == "__main__":
    ingest_data()
