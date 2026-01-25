import os
import json
import re
import sys
import io
import contextlib
import warnings
from typing import Optional, List, Any, Tuple
from PIL import Image
import streamlit as st
import pandas as pd
import base64
from io import BytesIO
import google.generativeai as genai
from e2b_code_interpreter import Sandbox

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

pattern = re.compile(r"```python\n(.*?)\n```", re.DOTALL)

def code_interpret(e2b_code_interpreter: Sandbox, code: str) -> Optional[List[Any]]:
    with st.spinner('Executing code in E2B sandbox...'):
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                exec = e2b_code_interpreter.run_code(code)

        if stderr_capture.getvalue():
            print("[Code Interpreter Warnings/Errors]", file=sys.stderr)
            print(stderr_capture.getvalue(), file=sys.stderr)

        if stdout_capture.getvalue():
            print("[Code Interpreter Output]", file=sys.stdout)
            print(stdout_capture.getvalue(), file=sys.stdout)

        if exec.error:
            print(f"[Code Interpreter ERROR] {exec.error}", file=sys.stderr)
            return None
        return exec.results

def match_code_blocks(llm_response: str) -> str:
    match = pattern.search(llm_response)
    if match:
        code = match.group(1)
        return code
    return ""

def chat_with_llm(e2b_code_interpreter: Sandbox, user_message: str, dataset_path: str) -> Tuple[Optional[List[Any]], str]:
    # Update system prompt to include dataset path information
    system_prompt = f"""You're a Python data scientist and data visualization expert. You are given a dataset at path '{dataset_path}' and also the user's query.
You need to analyze the dataset and answer the user's query with a response and you run Python code to solve them.

CRITICAL REQUIREMENTS - YOU MUST FOLLOW THESE:
1. Always use the dataset path variable '{dataset_path}' in your code when reading the CSV file.
2. ALWAYS create visualizations (graphs, charts, plots) - this is MANDATORY for every analysis, even if the user doesn't explicitly ask for graphs.
3. Generate MULTIPLE visualizations when appropriate:
   - Always create at least one visualization showing the main data distribution or comparison
   - If comparing categories, create bar charts or grouped visualizations
   - If showing trends, create line plots or time series charts
   - If showing relationships, create scatter plots or correlation heatmaps
   - Always include summary statistics visualizations (box plots, histograms, etc.)
4. For matplotlib: Always call plt.show() or display the figure at the end of your code. Use plt.tight_layout() for better formatting.
5. Use clear, informative titles, axis labels, and legends for all visualizations.
6. Make visualizations colorful and visually appealing - use different colors for different categories.
7. Always wrap your Python code in ```python code blocks so it can be extracted and executed.
8. IMPORTANT: Even if the user only asks a simple question, you MUST create visualizations to help them understand the data better. Visualizations are not optional - they are required."""

    # Configure Gemini API
    genai.configure(api_key=st.session_state.gemini_api_key)
    
    # Format the prompt for Gemini - always emphasize visualizations
    visualization_reminder = "\n\nREMINDER: You MUST create visualizations (graphs, charts, plots) in your response, even if the user's question doesn't explicitly ask for them. Visualizations help users understand the data better and are required for every analysis."
    full_prompt = f"{system_prompt}{visualization_reminder}\n\nUser query: {user_message}"

    with st.spinner('Getting response from Gemini AI model...'):
        try:
            # Create the model with the selected name
            model = genai.GenerativeModel(st.session_state.model_name)
            response = model.generate_content(full_prompt)
            
            # Extract text from response
            if hasattr(response, 'text') and response.text:
                response_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                response_text = response.candidates[0].content.parts[0].text
            else:
                response_text = str(response)
                
        except Exception as e:
            # Return error if model fails - no fallback
            error_msg = str(e)
            st.error(f"Error with model {st.session_state.model_name}: {error_msg}")
            return None, f"Error: {error_msg}. Please select a different model or verify your API key is valid and has access to this model."
        
        python_code = match_code_blocks(response_text)
        
        if python_code:
            code_interpreter_results = code_interpret(e2b_code_interpreter, python_code)
            return code_interpreter_results, response_text
        else:
            st.warning(f"Failed to match any Python code in model's response")
            return None, response_text

def upload_dataset(code_interpreter: Sandbox, uploaded_file) -> str:
    dataset_path = f"./{uploaded_file.name}"
    
    try:
        code_interpreter.files.write(dataset_path, uploaded_file)
        return dataset_path
    except Exception as error:
        st.error(f"Error during file upload: {error}")
        raise error


def main():
    """Main Streamlit application."""
    # Add custom CSS for futuristic AI-themed background with image-like effect
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0a1929 0%, #1a1a3e 25%, #2d1b4e 50%, #1a1a3e 75%, #0a1929 100%);
        background-attachment: fixed;
    }
    .stApp > header {
        background-color: rgba(10, 25, 41, 0.95) !important;
        border-bottom: 1px solid rgba(0, 255, 255, 0.2);
    }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a1929 0%, #1a1a3e 25%, #2d1b4e 50%, #1a1a3e 75%, #0a1929 100%);
    }
    .main .block-container {
        background-color: rgba(10, 25, 41, 0.7) !important;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid rgba(0, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }
    h1, h2, h3, p, label, .stMarkdown {
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
    }
    h1 {
        color: #00ffff !important;
        text-shadow: 0 0 20px rgba(0, 255, 255, 0.8), 0 0 40px rgba(0, 255, 255, 0.4);
    }
    .stDataFrame {
        background-color: rgba(10, 25, 41, 0.6);
        border: 1px solid rgba(0, 255, 255, 0.3);
        border-radius: 8px;
    }
    .stDataFrame table {
        font-size: 14px !important;
    }
    .stDataFrame th {
        padding: 12px !important;
        font-size: 15px !important;
    }
    .stDataFrame td {
        padding: 10px !important;
        font-size: 14px !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #00aaff, #0088ff);
        color: white;
        border: 1px solid rgba(0, 255, 255, 0.5);
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0, 170, 255, 0.4),
                    inset 0 0 10px rgba(0, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #00ccff, #0099ff);
        box-shadow: 0 6px 20px rgba(0, 255, 255, 0.6),
                    inset 0 0 15px rgba(0, 255, 255, 0.3);
        transform: translateY(-2px);
    }
    .stTextInput > div > div > input {
        background-color: rgba(10, 25, 41, 0.7);
        color: white;
        border: 1px solid rgba(0, 255, 255, 0.3);
        border-radius: 5px;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(0, 255, 255, 0.6);
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
    }
    .stTextArea > div > div > textarea {
        background-color: rgba(10, 25, 41, 0.7);
        color: white;
        border: 1px solid rgba(0, 255, 255, 0.3);
        border-radius: 5px;
    }
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(0, 255, 255, 0.6);
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
    }
    .stSelectbox > div > div > select {
        background-color: rgba(10, 25, 41, 0.7);
        color: white;
        border: 1px solid rgba(0, 255, 255, 0.3);
        border-radius: 5px;
    }
    .stCheckbox > label {
        color: white !important;
        text-shadow: 0 0 5px rgba(0, 255, 255, 0.3);
    }
    .stSidebar {
        background: linear-gradient(180deg, rgba(10, 25, 41, 0.95) 0%, rgba(26, 26, 62, 0.95) 100%);
        border-right: 1px solid rgba(0, 255, 255, 0.2);
    }
    .stImage {
        border: 2px solid rgba(0, 255, 255, 0.3);
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("📊 AI Data Visualization Agent")
    st.markdown("### Upload your dataset and ask questions about it!")
    st.markdown("---")

    # Initialize session state variables
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = ''
    if 'e2b_api_key' not in st.session_state:
        st.session_state.e2b_api_key = ''
    if 'model_name' not in st.session_state:
        st.session_state.model_name = 'gemini-1.5-flash'

    with st.sidebar:
        st.header("API Keys and Model Configuration")
        st.session_state.gemini_api_key = st.sidebar.text_input("Gemini API Key", type="password")
        st.sidebar.info("💡 Get your free Gemini API key from Google AI Studio")
        st.sidebar.markdown("[Get Gemini API Key](https://aistudio.google.com/apikey)")
        
        st.session_state.e2b_api_key = st.sidebar.text_input("Enter E2B API Key", type="password")
        st.sidebar.markdown("[Get E2B API Key](https://e2b.dev/docs/legacy/getting-started/api-key)")
        
        # Add model selection dropdown for Gemini models
        model_options = {
            "Gemini 2.5 Flash": "gemini-2.5-flash"
        }
        selected_model = st.selectbox(
            "Select Gemini Model",
            options=list(model_options.keys()),
            index=0  
        )
        st.session_state.model_name = model_options[selected_model]

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        # Display dataset with toggle
        df = pd.read_csv(uploaded_file)
        st.write("Dataset:")
        show_full = st.checkbox("Show full dataset")
        if show_full:
            st.dataframe(df, height=600, use_container_width=True)
        else:
            st.write("Preview (first 5 rows):")
            st.dataframe(df.head(), height=400, use_container_width=True)
        # Query input
        query = st.text_area("What would you like to know about your data?",
                            "Can you compare the average cost for two people between different categories?")
        
        if st.button("Analyze"):
            if not st.session_state.gemini_api_key or not st.session_state.e2b_api_key:
                st.error("Please enter both API keys in the sidebar.")
            else:
                with Sandbox(api_key=st.session_state.e2b_api_key) as code_interpreter:
                    # Upload the dataset
                    dataset_path = upload_dataset(code_interpreter, uploaded_file)
                    
                    # Pass dataset_path to chat_with_llm
                    code_results, llm_response = chat_with_llm(code_interpreter, query, dataset_path)
                    
                    # Display LLM's text response
                    st.write("AI Response:")
                    st.write(llm_response)
                    
                    # Display results/visualizations - ALWAYS show visualizations section
                    st.subheader("📈 Visualizations and Results")
                    if code_results:
                        visualization_count = 0
                        for idx, result in enumerate(code_results):
                            # Check for PNG images (matplotlib/other libraries)
                            if hasattr(result, 'png') and result.png:
                                try:
                                    visualization_count += 1
                                    # Decode the base64-encoded PNG data
                                    png_data = base64.b64decode(result.png)
                                    # Convert PNG data to an image and display it
                                    image = Image.open(BytesIO(png_data))
                                    st.image(image, caption=f"Visualization {visualization_count}", use_container_width=True)
                                except Exception as e:
                                    st.warning(f"Could not display image {idx + 1}: {str(e)}")
                            
                            # Check for matplotlib figures
                            elif hasattr(result, 'figure'):
                                try:
                                    visualization_count += 1
                                    fig = result.figure
                                    # Set dark background for matplotlib figures to match theme
                                    fig.patch.set_facecolor('#0a1929')
                                    # Update text colors for better visibility on dark background
                                    for ax in fig.axes:
                                        ax.set_facecolor('#0a1929')
                                        ax.tick_params(colors='cyan', labelsize=10)
                                        ax.xaxis.label.set_color('cyan')
                                        ax.yaxis.label.set_color('cyan')
                                        ax.title.set_color('white')
                                    st.pyplot(fig, use_container_width=True)
                                except Exception as e:
                                    st.warning(f"Could not display matplotlib figure {idx + 1}: {str(e)}")
                            
                            # Check for plotly figures
                            elif hasattr(result, 'show') or (hasattr(result, '__class__') and 'plotly' in str(type(result)).lower()):
                                try:
                                    visualization_count += 1
                                    st.plotly_chart(result, use_container_width=True)
                                except Exception as e:
                                    st.warning(f"Could not display plotly chart {idx + 1}: {str(e)}")
                            
                            # Check for pandas DataFrames or Series
                            elif isinstance(result, (pd.DataFrame, pd.Series)):
                                st.subheader(f"Data Table {idx + 1}")
                                st.dataframe(result, height=500, use_container_width=True)
                            
                            # Check for string outputs
                            elif isinstance(result, str):
                                st.text(result)
                            
                            # Check for numeric results
                            elif isinstance(result, (int, float)):
                                st.metric("Result", result)
                            
                            # For any other type, try to display it
                            else:
                                try:
                                    st.write(f"Result {idx + 1}:")
                                    st.write(result)
                                except Exception as e:
                                    st.warning(f"Could not display result {idx + 1}: {str(e)}")
                        
                        if visualization_count == 0:
                            st.warning("⚠️ No visualizations were generated. The AI should create graphs automatically. Please try again or ask more specifically for visualizations.")
                    else:
                        # If no code results, prompt user that visualizations should have been generated
                        st.warning("⚠️ No visualizations were generated. The AI is configured to always create graphs. Please check the AI response above and try asking again if needed.")  

if __name__ == "__main__":
    main()