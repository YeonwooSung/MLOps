import streamlit as st
import requests
import json


# Define the Streamlit app title and description
st.title("Machine Learning Model Deployment")
st.write("Use this app to make predictions with the deployed model.")

# Create input fields for user to enter data
st.header("Input Data")
feature1 = st.number_input("Feature 1", value=5.1, step=0.1)
feature2 = st.number_input("Feature 2", value=3.5, step=0.1)
feature3 = st.number_input("Feature 3", value=1.4, step=0.1)
feature4 = st.number_input("Feature 4", value=0.2, step=0.1)

# Create a button to trigger predictions
if st.button("Predict"):
    # Define the input data as a dictionary
    input_data = {
        "feature1": feature1,
        "feature2": feature2,
        "feature3": feature3,
        "feature4": feature4
    }

    # Make a POST request to the FastAPI model
    model_url = "http://your-fastapi-model-url/predict/"  # Replace with your FastAPI model URL
    response = requests.post(model_url, json=input_data)

    if response.status_code == 200:
        prediction = json.loads(response.text)["prediction"]
        st.success(f"Model Prediction: {prediction}")
    else:
        st.error("Failed to get a prediction. Please check your input data and try again.")
