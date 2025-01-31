import os
import openai
import streamlit as st
from googlesearch import search
from typing import List, Tuple, Dict
import time
from dataclasses import dataclass
from datetime import datetime

# Data structures
@dataclass
class SearchResult:
    title: str
    url: str
    description: str
    timestamp: datetime

@dataclass
class Citation:
    text: str
    source_title: str
    url: str

# Together AI Configuration
TOGETHER_API_KEY = "YOUR_API_KEY_HERE"
BASE_URL = "https://api.together.xyz/v1"

client = openai.OpenAI(api_key=TOGETHER_API_KEY, base_url=BASE_URL)

# Session State Management
def init_session_state():
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'sources' not in st.session_state:
        st.session_state.sources = []
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

def get_search_results(query: str, num_results: int = 5) -> List[SearchResult]:
    """Enhanced search function with better error handling and metadata"""
    try:
        results = search(query, num_results=num_results, advanced=True)
        return [
            SearchResult(
                title=result.title,
                url=result.url,
                description=result.description,
                timestamp=datetime.now()
            )
            for result in results
        ]
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return []

def generate_answer(query: str, sources: List[SearchResult]) -> Tuple[str, List[Citation]]:
    """Generates a detailed answer with citations using Together AI"""
    context = "\n\n".join([
        f"Source: {s.title}\nURL: {s.url}\nContent: {s.description}"
        for s in sources
    ])
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are an AI research assistant that provides detailed, accurate answers with citations.
                    Format your response in markdown with clear sections:
                    1. Direct answer to the question
                    2. Supporting details with inline citations [1], [2], etc.
                    3. Follow-up insights or implications"""
                },
                {
                    "role": "user",
                    "content": f"Question: {query}\n\nAvailable sources:\n{context}"
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        citations = [
            Citation(
                text=s.description[:200] + "...",
                source_title=s.title,
                url=s.url
            )
            for s in sources
        ]
        
        return answer, citations
    except Exception as e:
        st.error(f"Error generating answer: {str(e)}")
        return "I apologize, but I couldn't generate an answer at this time.", []

# [Previous imports and data structures remain the same until the CSS section]

def create_ui():
    st.set_page_config(
        page_title="Research Assistant",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Updated CSS with fixed text colors
    st.markdown("""
    <style>
    /* Global styles */
    .main {
        background-color: #1a1a1a;
    }
    
    /* UI Elements - White Text */
    .sidebar .sidebar-content {
        color: white !important;
    }
    
    .sidebar h1, .sidebar h2, .sidebar h3, .sidebar p {
        color: white !important;
    }
    
    .main h1, .main h2, .main h3 {
        color: white !important;
    }
    
    /* Search Input - Black Text */
    .stTextInput > div > div > input {
        background-color: white !important;
        color: black !important;
        padding: 15px !important;
        font-size: 16px !important;
        border-radius: 8px !important;
        border: 1px solid #e5e5e5 !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #666666 !important;
    }
    
    /* Output Container - Black Text */
    .message-container {
        background-color: white !important;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #e5e5e5;
    }
    
    .message-container * {
        color: black !important;
    }
    
    /* Source Cards - Black Text */
    .source-card {
        background-color: white !important;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #e5e5e5;
        transition: all 0.3s ease;
    }
    
    .source-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
    }
    
    .source-card * {
        color: black !important;
    }
    
    .source-card a {
        color: #10a37f !important;
        text-decoration: none;
    }
    
    /* History Section - White & Black Text */
    .history-header {
        color: white !important;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    
    .history-item {
        background-color: white;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #e5e5e5;
    }
    
    .history-question {
        color: white !important;
        padding: 10px;
        font-weight: bold;
    }
    
    .history-answer {
        color: black !important;
        background-color: white;
        padding: 15px;
        border-radius: 0 0 8px 8px;
    }
    
    /* Expander - White & Black Text */
    .streamlit-expanderHeader {
        background-color: #2d2d2d !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    .streamlit-expanderContent {
        background-color: white !important;
        color: black !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background-color: #10a37f !important;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #2d2d2d;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #10a37f;
        border-radius: 4px;
    }
    
    /* Main content area text */
    .main-content {
        color: white !important;
    }
    
    .main-content p {
        color: white !important;
    }
    
    /* Answer text specific styling */
    .answer-text {
        color: black !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #10a37f !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        background-color: #0d8c6d !important;
        transform: translateY(-1px);
    }
    
    /* Loading animation */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .loading {
        animation: pulse 1.5s infinite;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    init_session_state()
    create_ui()
    
    # Sidebar with white text
    with st.sidebar:
        st.markdown('<h1 style="color: white;">🔍 Settings</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color: white;">Customize your research experience</p>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<h3 style="color: white;">About</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: white;">
        This AI Research Assistant helps you find and analyze information from multiple sources.
        - ✨ Real-time search
        - 📚 Multiple sources
        - 🎯 Accurate citations
        </div>
        """, unsafe_allow_html=True)
    
    # Main content with white headers and black text for content
    st.markdown('<h1 style="color: white;">AI Research Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: white;">Ask any question and get detailed answers with reliable sources.</p>', unsafe_allow_html=True)
    
    # Search interface with black text
    query = st.text_input(
        "What would you like to know?",
        key="search_input",
        placeholder="Type your question here..."
    )
    
    if query:
        with st.spinner("🔍 Researching your question..."):
            # Progress animation
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # Get results and generate answer
            sources = get_search_results(query)
            answer, citations = generate_answer(query, sources)
            
            # Display answer with black text
            st.markdown(
                f"""
                <div class="message-container">
                    <h3 style="color: black !important;">Answer</h3>
                    <div class="answer-text">
                        {answer}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Display sources
            st.markdown('<h3 style="color: white !important;">Sources</h3>', unsafe_allow_html=True)
            cols = st.columns(min(3, len(citations)))
            for i, citation in enumerate(citations):
                with cols[i % 3]:
                    st.markdown(
                        f"""
                        <div class="source-card">
                            <h4>{citation.source_title[:50]}...</h4>
                            <p>{citation.text[:100]}...</p>
                            <a href="{citation.url}" target="_blank">Read more →</a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            # Update conversation history
            st.session_state.conversation_history.append({
                "query": query,
                "answer": answer,
                "citations": citations,
                "timestamp": datetime.now()
            })
    
    # Display conversation history
    if st.session_state.conversation_history:
        st.markdown('<h3 class="history-header">Previous Questions</h3>', unsafe_allow_html=True)
        for item in reversed(st.session_state.conversation_history[:-1]):
            with st.expander(f"Q: {item['query']}", expanded=False):
                st.markdown(
                    f"""
                    <div class="message-container">
                        <div class="answer-text">
                            {item['answer']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown('<p style="color: black !important;"><strong>Sources:</strong></p>', unsafe_allow_html=True)
                for citation in item['citations']:
                    st.markdown(
                        f"""
                        <div class="source-card">
                            <a href="{citation.url}" target="_blank">
                                {citation.source_title}
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

if __name__ == "__main__":
    main()
