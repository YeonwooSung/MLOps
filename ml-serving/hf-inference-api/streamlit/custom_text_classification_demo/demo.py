import streamlit as st
import requests


def set_page_config():
    st.set_page_config(
        page_title="HF Inference API Demo",
        page_icon=":robot_face:",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    st.latex(r"""
    \begin{align}
    \text{Inference API} &= \text{Model} + \text{Tokenizers} + \text{Preprocessing} + \text{Postprocessing} \\
    \end{align}
    """)


def set_up_api_key():
    st.sidebar.title("API Key")
    api_key = st.sidebar.text_input("Enter your API key", type="password")
    return api_key


def set_up_model():
    st.sidebar.title("Language Model")
    model_name = st.sidebar.selectbox(
        "Select a model",
        (
            'valhalla/distilbart-mnli-12-3',
            'valhalla/distilbart-mnli-12-1',
        ),
    )
    return model_name

def set_up_text():
    st.sidebar.title("Text")
    text = st.sidebar.text_area("Enter text to classify", height=200)
    return text

def set_up_possible_labels():
    st.sidebar.title("Possible Labels")
    possible_labels = st.sidebar.text_area("Enter possible labels", height=200)
    return possible_labels


def query_api(api_key, model_name, text, possible_labels):
    headers = { 'Authorization': f'Bearer {api_key}' }
    api_url = f'https://api-inference.huggingface.co/models/{model_name}'
    response = requests.post(api_url, headers=headers, json={
        'inputs': text,
        'parameters': {
            'candidate_labels': possible_labels,
        },
    })
    return response.json()

def main():
    set_page_config()
    api_key = set_up_api_key()
    model_name = set_up_model()
    text = set_up_text()
    possible_labels = set_up_possible_labels()

    if st.sidebar.button("Classify"):
        output = query_api(api_key, model_name, text, possible_labels)
        st.title("Classification")
        st.write(f"Model: {model_name}")
        st.write(f"Text: {text}")
        st.write(f"Possible Labels: {possible_labels}")
        st.write(f"Output: {output}")


if __name__ == "__main__":
    main()
