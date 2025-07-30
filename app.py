from flask import Flask, request, jsonify, render_template
import pandas as pd
import os

app = Flask(__name__, template_folder='FoodNutritionInformation')

# 엑셀 파일 경로 설정
excel_path = os.path.join(os.path.dirname(__file__), 'food_info.xlsx')
df = pd.read_excel(excel_path)

@app.route('/get_food_info', methods=['GET'])
def get_food_info():
    food_name = request.args.get('food_name')
    food_info = df[df['식품명'] == food_name].to_dict(orient='records')
    if food_info:
        return jsonify(food_info[0])
    else:
        return jsonify({"error": "Food not found"}), 404

@app.route('/search_foods', methods=['GET'])
def search_foods():
    query = request.args.get('query')
    if query:
        results = df[df['식품명'].str.contains(query, case=False, na=False)]
        food_names = results['식품명'].tolist()
        return jsonify({'food_names': food_names})
    return jsonify({'food_names': []})

@app.route('/')
def index():
    food_names = df['식품명'].tolist()
    return render_template('index.html', food_names=food_names)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
