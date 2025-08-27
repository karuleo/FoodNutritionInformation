from flask import Flask, request, jsonify, render_template
import pandas as pd
import os, sys


# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'FoodNutritionInformation')
EXCEL_PATH = os.path.join(BASE_DIR, 'food_info.xlsx')


app = Flask(__name__, template_folder=TEMPLATES_DIR)


# --- Data Loading with helpful logs ---
def load_dataframe(path):
    if not os.path.exists(path):
        print(f"[ERROR] Excel not found: {path}", file=sys.stderr)
        return None
    try:
        df = pd.read_excel(path, engine='openpyxl')
        # Tidy up headers
        df.columns = df.columns.map(lambda c: str(c).strip())
        print(f"[INFO] Loaded Excel rows={len(df)}, cols={list(df.columns)}", file=sys.stderr)
        if '식품명' not in df.columns:
            similar = [c for c in df.columns if '식품' in c or '명' in c]
            print(f"[ERROR] Column '식품명' not found. Similar: {similar}", file=sys.stderr)
            return None
        return df
    except Exception as e:
        print(f"[ERROR] Failed to read Excel: {e}", file=sys.stderr)
        return None




df = load_dataframe(EXCEL_PATH)


# --- Health check ---
@app.route('/health')
def health():
    ok = (df is not None) and os.path.exists(TEMPLATES_DIR) and os.path.exists(EXCEL_PATH)
    return {
        'ok': ok,
        'templates_dir': TEMPLATES_DIR,
        'excel_path': EXCEL_PATH,
        'df_loaded': df is not None
    }, (200 if ok else 500)




# --- API: exact match info ---
@app.route('/get_food_info', methods=['GET'])
def get_food_info():
    if df is None:
        return jsonify({"error": "DataFrame not loaded. Check server logs."}), 500
    food_name = (request.args.get('food_name') or '').strip()
    info = df[df['식품명'].astype(str) == food_name].to_dict(orient='records')
    return (jsonify(info[0]) if info else (jsonify({"error": "Food not found"}), 404))




# --- API: search by substring (case-insensitive) ---
@app.route('/search_foods', methods=['GET'])
def search_foods():
    if df is None:
        return jsonify({'food_names': [], 'error': 'DataFrame not loaded'}), 500


    query = (request.args.get('query') or '').strip()
    if query:
        results = df[df['식품명'].astype(str).str.contains(query, case=False, na=False)]
    else:
    # When query is empty, return a small default list
        results = df.head(100)


    names = results['식품명'].dropna().astype(str).tolist()
    return jsonify({'food_names': names})




# --- Page ---
@app.route('/')
def index():
    if df is None:
        return "데이터를 불러오지 못했습니다. 서버 로그를 확인하세요.", 500
    return render_template('index.html')




if __name__ == '__main__':
    print(f"[INFO] Templates dir exists: {os.path.exists(TEMPLATES_DIR)} -> {TEMPLATES_DIR}", file=sys.stderr)
    print(f"[INFO] Excel exists: {os.path.exists(EXCEL_PATH)} -> {EXCEL_PATH}", file=sys.stderr)
    app.run(debug=True, port=8000)