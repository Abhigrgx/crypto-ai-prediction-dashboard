from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model

# Initialize the Flask App
app = Flask(__name__)
CORS(app)

# Load the AI Brain once when the server turns on
print("Loading AI Brain... Please wait.")
try:
    model = load_model("crypto_ai_brain.keras")
    print("✅ AI Brain loaded successfully!")
except Exception as e:
    print("❌ Error loading model! Make sure 'crypto_ai_brain.keras' is in the folder.")
    model = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_crypto():
    data = request.json
    selected_coin = data.get('coin')
    print(f"Received request to predict: {selected_coin}")

    if model is None:
        return jsonify({"error": "AI Model is missing!"}), 500

    try:
        # 1. Fetch live data (Pulling from further back to ensure we have 360+ days)
        df = yf.download(selected_coin, start='2019-01-01')

        # 2. Add simulated sentiment (matching your training data)
        np.random.seed(42)
        df['Sentiment_Score'] = np.clip(np.random.normal(loc=0.05, scale=0.4, size=len(df)), -1, 1)

        # 3. Prepare and Scale features
        features = ['Close', 'Volume', 'Sentiment_Score']
        final_df = df[features].copy()
        
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(final_df)

        # 4. Format for the AI (Now looking back 360 days!)
        LOOKBACK = 360
        last_360_days = scaled_data[-LOOKBACK:]
        X_predict = last_360_days.reshape(1, LOOKBACK, len(features))

        # 5. The AI predicts!
        predicted_scaled = model.predict(X_predict)

        # 6. Un-scale back to real US Dollars
        dummy = np.zeros((1, len(features)))
        dummy[0, 0] = predicted_scaled[0][0]
        predicted_real = float(scaler.inverse_transform(dummy)[0, 0])

        # 7. Extract last actual price and yesterday's price safely
        try:
            last_actual = float(final_df['Close'].iloc[-1].item())
            yesterday_actual = float(final_df['Close'].iloc[-2].item())
        except:
            last_actual = float(final_df['Close'].iloc[-1])
            yesterday_actual = float(final_df['Close'].iloc[-2])

        # CALCULATE THE 24H PERCENTAGE CHANGE
        pct_change = ((last_actual - yesterday_actual) / yesterday_actual) * 100

        trend = "UPWARD TREND 📈" if predicted_real > last_actual else "DOWNWARD TREND 📉"

        # 8. Send the real math back to the HTML page
        return jsonify({
            "status": "success",
            "coin": selected_coin,
            "current_price": round(last_actual, 2),
            "pct_change_24h": round(pct_change, 2),
            "predicted_price": round(predicted_real, 2),
            "trend": trend
        })

    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)