# 📊 AI Data Visualization Agent

A Streamlit application that acts as your personal data visualization expert, powered by LLMs. Simply upload your dataset and ask questions in natural language - the AI agent will analyze your data, generate appropriate visualizations, and provide insights through a combination of charts, statistics, and explanations.

## Features
#### Natural Language Data Analysis
- Ask questions about your data in plain English
- Get instant visualizations and statistical analysis
- Receive explanations of findings and insights
- Interactive follow-up questioning

#### Intelligent Visualization Selection
- Automatic choice of appropriate chart types
- Dynamic visualization generation
- Statistical visualization support
- Custom plot formatting and styling

#### AI Model Support
- Gemini 2.5 Flash for fast and accurate analysis
- Google's advanced language model for code generation

## How It Works

### Workflow

1. **User Uploads Dataset**
   - User uploads a CSV file through the Streamlit interface
   - The dataset is displayed in the UI with an option to view full dataset or preview

2. **User Enters Query**
   - User types a natural language question about the data in the text area
   - Example: "Can you compare the average cost for two people between different categories?"

3. **AI Processing**
   - The query is sent to Google Gemini API along with a system prompt
   - The system prompt instructs the AI to:
     - Analyze the dataset at the specified path
     - Generate Python code wrapped in ```python code blocks
     - Always create visualizations (mandatory requirement)
     - Use appropriate chart types based on the analysis

4. **Code Extraction**
   - The AI response is parsed using regex to extract Python code blocks
   - The `match_code_blocks()` function searches for code between ```python markers

5. **Code Execution**
   - The extracted Python code is executed in an E2B sandbox environment
   - The dataset file is uploaded to the sandbox before execution
   - Code runs safely in isolation with access to data science libraries (pandas, matplotlib, plotly, etc.)

6. **Result Display**
   - The AI's text response is displayed explaining the analysis
   - Visualizations are extracted from execution results:
     - PNG images (matplotlib plots)
     - Matplotlib figure objects
     - Plotly charts
     - DataFrames and statistical summaries
   - All visualizations are rendered in the Streamlit interface

### Technical Logic

#### Core Components

1. **`code_interpret()` Function**
   - Executes Python code in E2B sandbox
   - Captures stdout and stderr for debugging
   - Returns execution results (visualizations, data, etc.)
   - Handles errors gracefully

2. **`match_code_blocks()` Function**
   - Uses regex pattern `r"```python\n(.*?)\n```"` to extract code
   - Returns the Python code string for execution
   - Handles cases where no code is found

3. **`chat_with_llm()` Function**
   - Configures Gemini API with user's API key
   - Constructs system prompt with:
     - Dataset path information
     - Mandatory visualization requirements
     - Code formatting instructions
   - Sends query to selected Gemini model
   - Extracts and returns both code and text response

4. **`upload_dataset()` Function**
   - Writes uploaded CSV file to E2B sandbox
   - Returns the dataset path for use in generated code
   - Handles upload errors

5. **Visualization Rendering**
   - Checks execution results for different visualization types:
     - PNG images (base64 decoded)
     - Matplotlib figures (with dark theme styling)
     - Plotly charts
     - Pandas DataFrames
   - Applies custom styling to match the futuristic UI theme

#### System Prompt Strategy

The system prompt is carefully crafted to ensure:
- **Mandatory Visualizations**: Every response must include visualizations
- **Multiple Chart Types**: Encourages diverse visualization approaches
- **Code Formatting**: Ensures code is properly wrapped for extraction
- **Dataset Path Usage**: Uses the correct file path variable
- **Professional Output**: Clear titles, labels, and formatting

#### Security & Isolation

- Code execution happens in E2B sandbox (isolated environment)
- No direct access to user's system
- Safe execution of arbitrary Python code
- Automatic cleanup after execution

## How to Use

### Prerequisites

Before running the application, you need to obtain API keys:

1. **Gemini API Key**
   - Visit [Google AI Studio](https://aistudio.google.com/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy the API key for use in the application

2. **E2B API Key**
   - Visit [E2B Documentation](https://e2b.dev/docs/legacy/getting-started/api-key)
   - Sign up for a free account
   - Generate an API key from the dashboard
   - Copy the API key for use in the application

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
   cd awesome-llm-apps/starter_ai_agents/ai_data_visualisation_agent
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   This will install:
   - `streamlit` - Web framework for the UI
   - `pandas` - Data manipulation
   - `matplotlib` - Plotting library
   - `plotly` - Interactive visualizations
   - `google-generativeai` - Gemini API client
   - `e2b-code-interpreter` - Code execution sandbox
   - `Pillow` - Image processing

3. **Run the Application**
   ```bash
   streamlit run ai_data_visualisation_agent.py
   ```
   
   The application will open in your default web browser at `http://localhost:8501`

### Usage Instructions

1. **Configure API Keys**
   - In the sidebar, enter your Gemini API Key
   - Enter your E2B API Key
   - Select the Gemini model (currently Gemini 2.5 Flash)

2. **Upload Your Dataset**
   - Click "Choose a CSV file" to upload your dataset
   - The dataset will be displayed in the main area
   - Use the checkbox to toggle between preview and full dataset view

3. **Ask Questions**
   - Type your question in the text area
   - Examples of good questions:
     - "What is the distribution of sales by region?"
     - "Compare average prices across different categories"
     - "Show me trends over time for revenue"
     - "Create a correlation heatmap for all numeric columns"
     - "What are the top 10 items by sales volume?"

4. **View Results**
   - The AI will generate:
     - A text explanation of the analysis
     - One or more visualizations (charts, graphs, plots)
     - Statistical summaries if relevant
   - All results are displayed in the main area

5. **Follow-up Questions**
   - You can ask follow-up questions about the same dataset
   - The dataset remains loaded for the session
   - Each new query generates fresh analysis and visualizations

### Tips for Best Results

- **Be Specific**: More specific questions yield better visualizations
  - Good: "Show me a bar chart comparing sales by region"
  - Better: "Create a bar chart showing total sales by region, sorted in descending order, with different colors for each bar"

- **Request Multiple Visualizations**: The AI can create multiple charts
  - "Show me both a bar chart and a pie chart of category distribution"

- **Ask for Statistics**: Combine visualizations with statistical analysis
  - "What is the average, median, and standard deviation of sales, and show it in a box plot"

- **Time Series Analysis**: For temporal data, ask for trend analysis
  - "Show me how sales have changed over the past year with a line chart"

### Troubleshooting

- **No Visualizations Generated**: 
  - Check that your question is clear and specific
  - Try rephrasing to explicitly request charts or graphs
  - Verify that your dataset has the columns you're asking about

- **API Key Errors**:
  - Ensure both API keys are correctly entered in the sidebar
  - Verify that your Gemini API key has access to the selected model
  - Check that your E2B API key is valid and has available credits

- **Code Execution Errors**:
  - The AI will attempt to fix errors, but complex queries may need refinement
  - Try breaking down complex questions into simpler ones
  - Check the AI response text for error explanations

## Requirements

See `requirements.txt` for the complete list of dependencies. Key packages include:
- Streamlit for the web interface
- Google Generative AI for LLM capabilities
- E2B Code Interpreter for safe code execution
- Pandas, Matplotlib, and Plotly for data analysis and visualization
