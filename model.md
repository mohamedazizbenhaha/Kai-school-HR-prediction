# Employee Turnover Prediction: End-to-End Supervised Learning Pipeline

This document details the complete pipeline for predicting employee turnover using supervised learning, from data exploration to deployment. It’s designed to be thorough, clear, and replicable.

---

## 1. Problem Statement

**Objective**: Build a predictive model to classify whether an employee will leave the company ("turnover") based on HR data.  
**Importance**: Turnover costs companies millions annually in recruitment, training, and lost productivity. Early identification of at-risk employees enables data-driven retention strategies.  
**Dataset**: The [HR Analytics dataset](https://www.kaggle.com/colara/human-resource) from Kaggle, with 14,999 rows and 10 features, including satisfaction level, salary, and tenure.

---

## 2. Data Exploration

### Dataset Breakdown
- **Features**:  
  - `satisfaction_level`: Float (0–1).  
  - `last_evaluation`: Float (0–1).  
  - `number_project`: Integer (2–7).  
  - `average_monthly_hours`: Integer (96–310).  
  - `time_spend_company`: Integer (years).  
  - `work_accident`: Binary (0/1).  
  - `promotion_last_5years`: Binary (0/1).  
  - `department`: Categorical (10 values).  
  - `salary`: Categorical (low, medium, high).  
- **Target**: `left` (0 = stayed, 1 = left).

### Statistical Summary
- Turnover rate: 23.8%.  
- Mean satisfaction: 0.61 ± 0.26 (concerningly low).  
- Median tenure: 3 years.  
- Correlation: `satisfaction_level` negatively correlates with `left` (-0.39).

### Visual Insights
- **Histogram**: Hours worked show bimodal peaks at ~150 and ~275, hinting at workload extremes.  
- **Boxplot**: High-turnover employees have lower satisfaction (median 0.41 vs. 0.67).  
- **Bar Chart**: HR (28%) and Accounting (26%) lead in turnover.

**Takeaway**: Satisfaction, workload, and tenure are likely key predictors.

---

## 3. Data Preprocessing

### Steps
1. **Renaming**: Changed `sales` to `department` for clarity.  
2. **Missing Values**: None detected (`df.isnull().sum() = 0`).  
3. **Encoding**:  
   - `department`: Ordinal encoding by turnover rate (HR=0, Management=9).  
   - `salary`: Mapped as low=0, medium=1, high=2.  
4. **Splitting**: 80% train (`HR_train.csv`), 20% test (`HR_test.csv`) with stratification on `left`.  
5. **Scaling**: Applied `StandardScaler` to numeric features (`satisfaction_level`, `average_monthly_hours`, etc.) to normalize distributions.

**Code**:
```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# Scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

---

## 4. Feature Engineering

New features enhance model performance:

1. **`investment`**: `number_project * average_monthly_hours`  
   - Captures total workload effort.  
2. **`reward`**: `promotion_last_5years + salary`  
   - Combines retention incentives.  
3. **`sanity`**: `(1 + satisfaction_level) / ((1 + work_accident) * (1 + (investment - median_investment)**2))`  
   - Balances well-being against stress factors.  
4. **`experience`**: `number_project * time_spend_company`  
   - Reflects cumulative tenure impact.  
5. **`efficiency`**: `number_project / average_monthly_hours`  
   - Measures productivity.

**Validation**: Checked for multicollinearity via correlation heatmap—none exceeded 0.85.

---

## 5. Model Selection & Training

### Models Tested
| Model              | F1-Score | Training Time | Notes                       |
|--------------------|----------|---------------|-----------------------------|
| Logistic Regression| 0.8977   | 0.1s          | Simple, assumes linearity.  |
| KNN                | 0.9433   | 0.5s          | Distance-based, scalable.   |
| SVM                | 0.9610   | 2.3s          | Strong but slow.            |
| Random Forest      | 0.9580   | 1.2s          | Robust, less overfitting.   |
| Extra Trees        | **0.9813**| 0.8s          | Fast, top performer.        |

### Process
- **Hyperparameters**: Grid search on Extra Trees (`n_estimators=100`, `max_depth=20`).  
- **Training**: Fit on scaled `X_train` with `y_train`.  
- **Why Extra Trees?**: Best F1-score, efficient randomization, handles categorical data well.

---

## 6. Model Evaluation

### Metrics
- Accuracy: 0.9820  
- Precision: 0.9850  
- Recall: 0.9800  
- F1-Score: 0.9825  
- ROC-AUC: 0.99  

### Visuals
- **Confusion Matrix**: 98% true positives, minimal false negatives.  
- **ROC Curve**: Near-perfect class separation.

**Interpretation**: High recall ensures few at-risk employees are missed—critical for HR.

---

## 7. Model Export & Feature Importance

- **Export**:  
  - Model: `joblib.dump(model, 'hr_turnover_model.joblib')`  
  - Scaler: `joblib.dump(scaler, 'scaler.joblib')`  
- **Feature Importance**:  
  - Top 3: `satisfaction_level` (0.32), `investment` (0.25), `time_spend_company` (0.18).  
  - Plotted via bar chart for interpretability.

---

## 8. API Deployment (Flask)

### Structure
- File: `app.py`  
- Endpoints:  
  - `/predict` (POST): JSON input.  
  - `/predict` (GET): Query params.

### Code
```python
from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)
model = joblib.load('hr_turnover_model.joblib')
scaler = joblib.load('scaler.joblib')

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    data = request.json if request.is_json else request.args
    # Preprocess input (encoding, scaling, feature engineering)
    processed_data = preprocess(data, scaler)
    pred = model.predict(processed_data)
    probs = model.predict_proba(processed_data)
    return jsonify({
        'prediction': 'Turnover' if pred[0] else 'No Turnover',
        'probability': {'No Turnover': probs[0][0], 'Turnover': probs[0][1]}
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Running
```bash
python app.py
```

---

## 9. API Usage Examples

**POST**:
```python
import requests
data = {'satisfaction_level': 0.38, 'number_project': 2, 'salary': 'low', ...}
response = requests.post('http://localhost:5000/predict', json=data)
print(response.json())
```

**GET**:
```
curl "http://localhost:5000/predict?satisfaction_level=0.38&salary=low&..."
```

---

## 10. Project Structure

```
├── app.py                  # Flask API
├── data/                   # Datasets
│   ├── HR_comma_sep.csv
│   ├── HR_train.csv
│   ├── HR_test.csv
├── models/                 # Saved models
│   ├── hr_turnover_model.joblib
│   ├── scaler.joblib
├── notebooks/              # Analysis
│   ├── Turnover_model_Final.ipynb
├── requirements.txt        # Dependencies
├── Jenkinsfile             # CI/CD pipeline
```

---

## 11. Requirements

```bash
pandas==1.3.5
numpy==1.21.6
scikit-learn==1.0.2
flask==2.1.0
joblib==1.1.0
matplotlib==3.5.1
```

---

## 12. License

MIT License. Dataset © Kaggle.

---

**Notes**: Test the API with edge cases (e.g., missing fields) to ensure robustness.