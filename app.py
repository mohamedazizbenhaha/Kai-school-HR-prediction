import pandas as pd
import joblib
from flask import Flask, request, jsonify
from sklearn.preprocessing import StandardScaler

# Initialize Flask app
app = Flask(__name__)

# Load the trained model and scaler
model = joblib.load('hr_turnover_model.joblib')
scaler = joblib.load('scaler.joblib')

# Define feature order and mappings (from notebook)
FEATURES = ['satisfaction_level', 'last_evaluation', 'number_project', 
            'average_monthly_hours', 'time_spend_company', 'work_accident', 
            'promotion_last_5years', 'department', 'salary', 
            'investment', 'reward', 'sanity', 'experience', 'efficiency']
DEPARTMENT_MAPPING = {'hr': 0, 'accounting': 1, 'technical': 2, 'support': 3, 
                      'sales': 4, 'marketing': 5, 'IT': 6, 'product_mng': 7, 
                      'RandD': 8, 'management': 9}
SALARY_MAPPING = {'low': 0, 'medium': 1, 'high': 2}

def preprocess_input(data):
    """Preprocess input data (single or multiple) to match training format."""
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        df = pd.DataFrame(data)
    
    # Encode categorical features
    df['department'] = df['department'].map(DEPARTMENT_MAPPING)
    df['salary'] = df['salary'].map(SALARY_MAPPING)
    
    # Create engineered features
    df['investment'] = df['number_project'] * df['average_monthly_hours']
    df['reward'] = df['promotion_last_5years'] + df['salary']
    df['sanity'] = (1 + df['satisfaction_level']) / (
        (1 + df['work_accident']) * (1 + (df['investment'] - 790.286752)**2))
    df['experience'] = df['number_project'] * df['time_spend_company']
    df['efficiency'] = df['number_project'] / df['average_monthly_hours']
    
    # Ensure all features are present
    for col in FEATURES:
        if col not in df.columns:
            df[col] = 0
    
    # Reorder and normalize
    df = df[FEATURES]
    df_normalized = scaler.transform(df)
    return df_normalized

@app.route('/predict', methods=['POST'])
def predict_post():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400
        
        # Preprocess input
        processed_data = preprocess_input(data)
        
        # Predict
        predictions = model.predict(processed_data)
        probabilities = model.predict_proba(processed_data)
        
        # Format output
        results = []
        for pred, prob in zip(predictions, probabilities):
            result = {
                'prediction': 'Turnover' if pred == 1 else 'No Turnover',
                'probability': {
                    'No Turnover': float(prob[0]),
                    'Turnover': float(prob[1])
                }
            }
            results.append(result)
        
        return jsonify(results[0] if isinstance(data, dict) else results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['GET'])
def predict_get():
    try:
        data = {key: float(request.args.get(key)) if key not in ['department', 'salary'] 
                else request.args.get(key) for key in FEATURES if request.args.get(key)}
        if not data:
            return jsonify({'error': 'No input parameters provided'}), 400
        
        processed_data = preprocess_input(data)
        prediction = model.predict(processed_data)[0]
        prob = model.predict_proba(processed_data)[0]
        
        return jsonify({
            'prediction': 'Turnover' if prediction == 1 else 'No Turnover',
            'probability': {
                'No Turnover': float(prob[0]),
                'Turnover': float(prob[1])
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return "OK", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
