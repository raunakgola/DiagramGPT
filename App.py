import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
import os
import streamlit_mermaid as stmd
import re

# Set up the page configuration
st.set_page_config(
    page_title="Mermaid Diagram Generator",
    page_icon="🧩",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5em;
        margin-bottom: 1px;
    }
    .description {
        text-align: center;
        color: #666;
        font-size: 1.1em;
        margin-bottom: 1px;
    }
    .mermaid-container {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_llm():
    """
    Initialize the Google Generative AI model through LangChain.
    This function sets up the connection to Google's Gemini model.
    """
    try:
        # Initialize the ChatGoogleGenerativeAI model
        # You'll need to set your GOOGLE_API_KEY environment variable
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # Using Gemini Pro model
            temperature=0.3,     # Lower temperature for more consistent diagram generation
        )
        return llm
    except Exception as e:
        st.error(f"Error initializing LLM: {str(e)}")
        return None

def create_mermaid_prompt():
    """
    Create a structured prompt template for generating Mermaid diagrams.
    This template guides the LLM to produce valid Mermaid syntax.
    """
    template = """
    You are an expert at creating Mermaid diagrams. Based on the user's request, generate a complete Mermaid diagram code.

    User Request: {user_input}

    Please create a Mermaid diagram that best represents the user's request. Follow these guidelines:
    1. Use appropriate Mermaid diagram types (flowchart, sequence, class, etc.)
    2. Ensure the syntax is valid and complete
    3. Include proper node connections and labels
    4. Make the diagram clear and well-structured
    5. Only return the Mermaid code, starting with the diagram type declaration

    Mermaid Code:
    """
    
    return PromptTemplate(
        input_variables=["user_input"],
        template=template
    )

def extract_mermaid_code(response_text):
    """
    Extract clean Mermaid code from the LLM response.
    This function removes any extra formatting or explanatory text.
    """
    # Remove code block markers if present
    response_text = response_text.strip()
    if response_text.startswith("```mermaid"):
        response_text = response_text[10:]  # Remove ```mermaid
    elif response_text.startswith("```"):
        response_text = response_text[3:]   # Remove ```
    
    if response_text.endswith("```"):
        response_text = response_text[:-3]  # Remove closing ```
    
    return response_text.strip()

def display_mermaid_diagram(mermaid_code):
    """
    Display the Mermaid diagram using Streamlit's HTML component.
    This function embeds the Mermaid.js library to render the diagram.
    """

    stmd.st_mermaid(mermaid_code,height=600)

def main():
    """
    Main application function that orchestrates the Streamlit interface
    and integrates all components together.
    """
    # App header and description
    st.markdown('<h1 class="main-header">🧩 Mermaid Diagram Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="description">Transform your ideas into beautiful diagrams using AI-powered Mermaid code generation</p>', unsafe_allow_html=True)
    
    # Sidebar for API key input and instructions
    with st.sidebar:
        st.header("🔑 Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Google API Key",
            type="password",
            help="Enter your Google API key to use the Gemini model"
        )
        
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
            st.success("API Key set successfully!")
        
        st.header("📋 Instructions")
        st.markdown("""
        1. Enter your Google API key above
        2. Describe the diagram you want to create
        3. Click 'Generate Diagram' to create your Mermaid code
        4. View both the code and rendered diagram below
        """)
        
        st.header("💡 Example Prompts")
        st.markdown("""
        - "Create a flowchart for user login process"
        - "Show a sequence diagram for API authentication"
        - "Draw a class diagram for a simple blog system"
        - "Make a network diagram for a web application"
        """)
    
    # Main content area
    if not api_key:
        st.warning("⚠️ Please enter your Google API key in the sidebar to get started.")
        st.info("💡 You can get a free API key from Google AI Studio: https://makersuite.google.com/app/apikey")
        return
    
    # Initialize the LLM
    llm = initialize_llm()
    if not llm:
        return
    
    # User input section
    st.header("📝 Describe Your Diagram")
    user_prompt = st.text_area(
        "What kind of diagram would you like to create?",
        placeholder="Example: Create a flowchart showing the process of ordering food online, from browsing menu to delivery",
        height=100
    )
    
    # Generate button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        generate_button = st.button("🚀 Generate Diagram", type="primary", use_container_width=True)
    
    # Process user input when button is clicked
    if generate_button and user_prompt:
        with st.spinner("🤖 Generating your Mermaid diagram..."):
            try:
                # Create the prompt template and format it with user input
                prompt_template = create_mermaid_prompt()
                formatted_prompt = prompt_template.format(user_input=user_prompt)
                
                # Generate response using the LLM
                response = llm.invoke([HumanMessage(content=formatted_prompt)])
                
                # Extract clean Mermaid code from response
                mermaid_code = extract_mermaid_code(response.content)
                
                st.header("📄 Generated Mermaid Code")
                st.code(mermaid_code, language="mermaid")
                    
                # Add copy button functionality
                if st.button("📋 Copy Code", key="copy_code"):
                    st.success("Code copied to clipboard!")
                
                st.header("🎨 Rendered Diagram")
                display_mermaid_diagram(mermaid_code)
                
                
            except Exception as e:
                st.error(f"❌ Error generating diagram: {str(e)}")
                st.info("💡 Try rephrasing your request or check your API key.")
    
    elif generate_button and not user_prompt:
        st.warning("⚠️ Please enter a description for your diagram.")
    
    # Footer with additional information
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9em;">
        <p>This app uses Google's Gemini AI through LangChain to generate Mermaid diagram code.</p>
        <p>Learn more about <a href="https://mermaid.js.org/" target="_blank">Mermaid syntax</a> | 
        <a href="https://python.langchain.com/docs/integrations/chat/google_generative_ai" target="_blank">LangChain Google GenAI</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
