from flask import Flask, request, jsonify, render_template, send_from_directory, session
import mysql.connector
import json
import math
import time
from google import genai
from bazi_logic import calculate_bazi
from config import DB_CONFIG

# Register Auth
from auth import auth_bp

DEFAULT_API_KEY = "AIzaSyBUdc6fJBXleMR976c-LanAEtZZJHzQCqA"

app = Flask(__name__, static_url_path='', static_folder='.')
app.secret_key = 'SUPER_SECRET_KEY_FOR_DEMO' 

app.register_blueprint(auth_bp, url_prefix='/api')

@app.route('/')
def index():
    if 'user_id' not in session:
        return send_from_directory('.', 'login.html')
    return send_from_directory('.', 'index.html')

@app.route('/login.html')
def login_page():
    return send_from_directory('.', 'login.html')

@app.route('/register.html')
def register_page():
    return send_from_directory('.', 'register.html')

@app.route('/forgot_password.html')
def forgot_page():
    return send_from_directory('.', 'forgot_password.html')

def find_similar_billionaires(user_bazi, user_gender):
    matches = []
    top_industries = []
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM billionaires")
        billionaires = cursor.fetchall()
        
        user_me = user_bazi['me']
        user_wuxing = user_bazi['wuxing']
        
        wuxing_order = ['金', '木', '水', '火', '土']
        def get_vec(w_dict):
            return [w_dict.get(k, 0) for k in wuxing_order]

        user_vec = get_vec(user_wuxing)
        
        scored_candidates = []
        for b in billionaires:
            score = 0
            # 1. Day Master (50pts)
            if b['day_master'] == user_me:
                score += 50
                
            # 2. Wuxing Similarity (50pts)
            try:
                b_wuxing = json.loads(b['wuxing_counts'])
                b_vec = get_vec(b_wuxing)
                
                dot_product = sum(u*v for u, v in zip(user_vec, b_vec))
                mag_u = math.sqrt(sum(u*u for u in user_vec))
                mag_v = math.sqrt(sum(v*v for v in b_vec))
                
                if mag_u * mag_v > 0:
                    similarity = dot_product / (mag_u * mag_v)
                else:
                    similarity = 0
                score += similarity * 50
            except:
                pass
            
            scored_candidates.append({
                'name': b['name'],
                'net_worth': b['net_worth'],
                'industry': b['industry'],
                'source': b['source'],
                'day_master': b['day_master'],
                'score': score
            })
            
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        matches = scored_candidates[:5] # Get top 5 matches
        
        # Aggregate Industries from Top 15
        industry_counts = {}
        for c in scored_candidates[:15]: 
            ind = c['industry']
            if ind:
                industry_counts[ind] = industry_counts.get(ind, 0) + 1
        
        top_industries = sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Match error: {e}")
        
    return matches, top_industries

@app.route('/calculate', methods=['POST'])
def calculate():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    dob = data.get('dob') # "2023-01-01"
    tob = data.get('tob') # "14:30"
    
    if not dob or not tob:
        return jsonify({'error': 'Missing Date or Time'}), 400
        
    try:
        year, month, day = map(int, dob.split('-'))
        hour, minute = map(int, tob.split(':'))
    except:
        return jsonify({'error': 'Invalid Date/Time Format'}), 400
        
    gender = data.get('gender')
    state = data.get('state')
    api_key = DEFAULT_API_KEY
    
    try:
        # 1. Calculate Bazi
        bazi_result = calculate_bazi(year, month, day, hour, gender)
        
        # 2. Billionaire Matching & Career Recs
        top_matches, recommended_industries = find_similar_billionaires(bazi_result, gender)
        
        # 3. AI Analysis
        ai_analysis = "⚠️ **AI Not Configured**: Please enter your Google Gemini API Key in `src/app.py` or `config.py` to enable the AI features."
        
        if api_key and "_YOUR_API_KEY_HERE" not in api_key: # Check if key is valid (not placeholder)
            client = genai.Client(api_key=api_key)
            
            # Enrich prompt with detailed billionaire context
            match_context = ""
            if top_matches:
                m = top_matches[0]
                match_context = f"""
                Top Match: {m['name']} 
                - Wealth Source/Company: {m['source']}
                - Industry: {m['industry']}
                """
            
            ind_str = ", ".join([f"{i[0]}" for i in recommended_industries])

            prompt = f"""
            Analyze this Bazi chart with a specific focus on wealth and career alignment.
            
            Day Master: {bazi_result['me']}
            Elements: {bazi_result['wuxing']}
            Ten Gods: {bazi_result['shishen']}
            
            Billionaire Comparison:
            {match_context}
            
            Data-driven Recommendations: {ind_str}
            
            Please provide:
            1. **Four Pillars Analysis**: Briefly decode their structure.
            2. **Billionaire Archetype**: Explain what {m['name']}'s success in '{m['source']}' ({m['industry']}) reveals about this user's potential. Why does this path fit them?
            3. **Industry Strategy**: Why are {ind_str} valid paths? (Connect to elements e.g. Tech=Fire, Real Estate=Earth).
            
            Style: Engaging, professional, and explain 'Why' clearly. Limit 400 words.
            """
            
            model_name = 'gemini-2.5-flash'
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model=model_name, contents=prompt
                    )
                    ai_analysis = response.text
                    break 
                except Exception as e:
                    print(f"AI Error: {e}")
                    time.sleep(1)
                    if attempt == max_retries - 1:
                         # Return the actual error for debugging
                         ai_analysis = f"**AI Error:** {str(e)}\n\n" \
                                       f"**Fallback Analysis:** Your charts show affinity with {ind_str}."
        
        # 4. Save to DB
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO bazi_records (user_id, birth_date, birth_time, gender, state, bazi_json, ai_analysis) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (session['user_id'], dob, tob, gender, state, json.dumps(bazi_result), ai_analysis)
            )
            conn.commit()
            cursor.close()
            conn.close()
        except:
            pass

        return jsonify({
            'bazi': bazi_result,
            'matches': top_matches,
            'careers': recommended_industries,
            'ai_analysis': ai_analysis
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, birth_date, birth_time, state, gender, created_at FROM bazi_records WHERE user_id = %s ORDER BY created_at DESC LIMIT 20", (session['user_id'],))
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for r in records:
            r['birth_date'] = str(r['birth_date'])
            r['birth_time'] = str(r['birth_time'])
            
        return jsonify(records)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/delete/<int:record_id>', methods=['DELETE'])
def delete_history(record_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # Verify ownership before deleting
        cursor.execute("DELETE FROM bazi_records WHERE id = %s AND user_id = %s", (record_id, session['user_id']))
        conn.commit()
        deleted_count = cursor.rowcount
        cursor.close()
        conn.close()
        
        if deleted_count == 0:
            return jsonify({'error': 'Record not found or unauthorized'}), 404
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/load_record/<int:record_id>', methods=['GET'])
def load_record(record_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bazi_records WHERE id = %s AND user_id = %s", (record_id, session['user_id']))
        record = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not record:
            return jsonify({'error': 'Record not found'}), 404
            
        bazi_result = json.loads(record['bazi_json'])
        # Re-calculate matches as they aren't stored fully, or just return existing analysis
        top_matches, recommended_industries = find_similar_billionaires(bazi_result, record['gender'])
        
        return jsonify({
            'bazi': bazi_result,
            'matches': top_matches,
            'careers': recommended_industries,
            'ai_analysis': record['ai_analysis']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
