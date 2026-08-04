from flask import Flask, request, render_template
import pickle
import numpy as np

# 1. Initialize the Flask application
app = Flask(__name__)

# 2. Load the Pickled Model and Scaler
# 'rb' stands for read-binary
with open('model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

with open('scaler.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

# 3. Route for the Home Page
@app.route('/')
def home():
    # This will load your index.html file from the 'templates' folder
    return render_template('index.html')

# 4. Route to handle the Prediction when the form is submitted
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract the values submitted from the HTML form
        float_features = [float(x) for x in request.form.values()]
        
        # Convert to a 2D numpy array for the model
        features_array = np.array([float_features])
        
        # Scale the data EXACTLY as we did in the Jupyter notebook
        scaled_features = scaler.transform(features_array)
        
        # Make the prediction using the loaded model
        prediction = model.predict(scaled_features)
        
        # Determine the result (0 = No Diabetes, 1 = Diabetes)
        if prediction[0] == 1:
            result_text = "The model predicts: High Risk of Diabetes"
        else:
            result_text = "The model predicts: Low Risk of Diabetes"
            
        # Send the result back to the HTML page
        return render_template('index.html', prediction_text=result_text)
        
    except Exception as e:
        return render_template('index.html', prediction_text=f"Error: Make sure all inputs are valid numbers.")

# 5. Run the application
if __name__ == "__main__":
    app.run(debug=True)