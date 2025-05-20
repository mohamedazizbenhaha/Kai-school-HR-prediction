FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy necessary files
COPY app.py .
COPY hr_turnover_model.joblib .
COPY scaler.joblib .
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]