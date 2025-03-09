import streamlit as st
import re
import secrets
import string
from zxcvbn import zxcvbn
from typing import Dict, List, Union

# Configuration
st.set_page_config(
    page_title="SecurePass Evaluator",
    page_icon="🔒",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Progress bar enhancements */
    .progress-bar {
        height: 25px;
        border-radius: 12px;
        overflow: hidden;
        background: #e9ecef;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .progress-bar-fill {
        height: 100%;
        transition: width 0.6s ease-in-out;
        position: relative;
    }
    
    .progress-bar-fill::after {
        content: '';
        position: absolute;
        right: 0;
        top: 0;
        bottom: 0;
        width: 10px;
        background: linear-gradient(45deg, rgba(255,255,255,0.2) 25%, transparent 25%,
                    transparent 50%, rgba(255,255,255,0.2) 50%,
                    rgba(255,255,255,0.2) 75%, transparent 75%);
        background-size: 20px 20px;
    }
    
    /* Score colors with gradients */
    .score-0 { background: linear-gradient(135deg, #ff4d4d 0%, #ff1a1a 100%); }
    .score-1 { background: linear-gradient(135deg, #ff944d 0%, #ff6a00 100%); }
    .score-2 { background: linear-gradient(135deg, #ffdb4d 0%, #ffcc00 100%); }
    .score-3 { background: linear-gradient(135deg, #b3ff66 0%, #80ff00 100%); }
    .score-4 { background: linear-gradient(135deg, #66ff66 0%, #00cc00 100%); }
    
    /* Card styling */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
    }
    
    /* Input enhancements */
    .stTextInput input {
        border-radius: 8px!important;
        padding: 12px 16px!important;
        font-size: 16px!important;
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 8px!important;
        padding: 10px 24px!important;
        background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);
        transition: transform 0.2s!important;
        border: none;
        color: white;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: rgb(224, 215, 215)
    }
    
    /* Icon animations */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    .pulse-icon {
        animation: pulse 2s infinite;
    }
    </style>
""", unsafe_allow_html=True)

# Password analysis function
def analyze_password(password: str) -> Dict[str, Union[bool, int]]:
    analysis = {
        'length': len(password),
        'uppercase': bool(re.search(r'[A-Z]', password)),
        'lowercase': bool(re.search(r'[a-z]', password)),
        'numbers': bool(re.search(r'[0-9]', password)),
        'special': bool(re.search(r'[^A-Za-z0-9]', password)),
        'common_patterns': bool(re.search(r'(123|abc|password|qwerty)', password.lower())),
        'repeats': bool(re.search(r'(.)\1{2,}', password)),
    }
    return analysis

# Strength calculation
def calculate_strength(analysis: Dict[str, Union[bool, int]]) -> Dict[str, Union[str, int]]:
    score = 0
    
    # Additive factors
    score += min(analysis['length'] * 2, 20)  # Max 20 for length
    score += 5 * sum([analysis['uppercase'], analysis['lowercase'], 
                     analysis['numbers'], analysis['special']])
    
    # Deductions
    if analysis['common_patterns']:
        score -= 15
    if analysis['repeats']:
        score -= 10
    if analysis['length'] < 8:
        score -= 20
    
    # Normalize score
    score = max(0, min(score, 100))
    
    # Determine strength category
    if score < 40:
        return {'strength': 'Weak', 'score': score, 'color': '#ff4b4b'}
    elif score < 75:
        return {'strength': 'Moderate', 'score': score, 'color': '#f4c430'}
    else:
        return {'strength': 'Strong', 'score': score, 'color': '#2ecc71'}

# AI-powered suggestions generator
def generate_suggestions(analysis: Dict[str, Union[bool, int]]) -> List[str]:
    suggestions = []
    
    if analysis['length'] < 12:
        suggestions.append("🔍 Increase length to at least 12 characters")
    if not analysis['uppercase']:
        suggestions.append("🔠 Add uppercase letters")
    if not analysis['lowercase']:
        suggestions.append("🔡 Add lowercase letters")
    if not analysis['numbers']:
        suggestions.append("🔢 Include numbers")
    if not analysis['special']:
        suggestions.append("⚡ Add special characters (!@#$%^ etc.)")
    if analysis['common_patterns']:
        suggestions.append("🚫 Avoid common patterns and dictionary words")
    if analysis['repeats']:
        suggestions.append("♻️ Reduce repeating characters")
    
    # Advanced heuristic suggestions
    if analysis['length'] >= 8 and analysis['length'] < 12:
        suggestions.append("💡 Try using a passphrase instead of random characters")
    if len(suggestions) == 0:
        suggestions.append("✅ Excellent password! Consider using a password manager to store it securely.")
    
    return suggestions

# Secure password generator
def generate_password(length: int = 12, uppercase: bool = True, 
                     lowercase: bool = True, numbers: bool = True, 
                     special: bool = True) -> str:
    characters = ''
    if uppercase: characters += string.ascii_uppercase
    if lowercase: characters += string.ascii_lowercase
    if numbers: characters += string.digits
    if special: characters += '!@#$%^&*()_+-='
    
    if not characters:
        return "Please select at least one character type"
    
    return ''.join(secrets.choice(characters) for _ in range(length))

# UI Components
def main() -> None:
    # Hero Section
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🔐 SecurePass Pro")
        st.markdown("<h3 style='font-weight: 400;'>Enterprise-grade Password Security Analysis</h3>", unsafe_allow_html=True)
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3064/3064155.png", width=100)

    # Main Card Container
    with st.container():
        # Password Input Section
        password = st.text_input(
                "Enter password to analyze:",
                type="password",
                help="Start typing to see real-time analysis",
                key="pw_input"
            )
        st.button('Analyze Now', key="analyze_btn")

        if password:
            # Analysis Results
            result = zxcvbn(password)
            score = result['score']
            analysis = analyze_password(password)
            suggestions = generate_suggestions(analysis)
            
            # Strength Visualization
            with st.container():
                strength_labels = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"]
                progress_percent = (score + 1) * 20

                # Header with animated icon
                st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                        <span class='pulse-icon' style='font-size: 32px;'>{"🔴🟠🟡🟢🟢"[score]}</span>
                        <h3 style='margin: 0;'>Security Assessment</h3>
                    </div>
                """, unsafe_allow_html=True)

                # Progress bar with score
                st.markdown(f"""
                    <div style="margin-bottom: 1.5rem;">
                        <div class="progress-bar">
                            <div class="progress-bar-fill score-{score}" style="width: {progress_percent}%;"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                            <span class='text-{score}' style='font-weight: 600;'>{strength_labels[score]}</span>
                            <span style='color: #7f8c8d;'>Score: {analysis['length']}/24</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Metrics Grid
                cols = st.columns(4)
                metrics = [
                    ("Length", f"{analysis['length']} chars", "#4b6cb7"),
                    ("Complexity", f"{sum([analysis['uppercase'], analysis['lowercase'], analysis['numbers'], analysis['special']])}/4", "#2ecc71"),
                    ("Predictability", "High" if analysis['common_patterns'] else "Low", "#e74c3c"),
                    ("Entropy", f"{result['guesses_log10']:.1f} bits", "#f1c40f")
                ]
                
                for col, (label, value, color) in zip(cols, metrics):
                    with col:
                        st.markdown(f"""
                            <div style="text-align: center; padding: 1rem; background: {color}10; border-radius: 8px;">
                                <div style="color: {color}; font-weight: 600; margin-bottom: 0.5rem;">{label}</div>
                                <div style="font-size: 1.2rem; font-weight: 700;">{value}</div>
                            </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)  # Close card

            # Recommendations Section
            with st.container():
                st.markdown("### 🔍 Security Recommendations")
                
                # Two-column layout for suggestions
                rec_cols = st.columns(2)
                with rec_cols[0]:
                    for suggestion in suggestions[:len(suggestions)//2]:
                        st.markdown(f"<div style='padding: 0.5rem; border-left: 3px solid #4b6cb7; margin: 0.5rem 0;'>📌 {suggestion}</div>", unsafe_allow_html=True)
                with rec_cols[1]:
                    for suggestion in suggestions[len(suggestions)//2:]:
                        st.markdown(f"<div style='padding: 0.5rem; border-left: 3px solid #4b6cb7; margin: 0.5rem 0;'>📌 {suggestion}</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)  # Close card

        # Password Generator
        with st.expander("✨ Advanced Password Generator", expanded=True):
            st.markdown("### Create Secure Password")
            length = st.slider("Length", 8, 24, 16, key="gen_length")
            char_types = st.columns(4)
            with char_types[0]: uppercase = st.checkbox("A-Z", True)
            with char_types[1]: lowercase = st.checkbox("a-z", True)
            with char_types[2]: numbers = st.checkbox("0-9", True)
            with char_types[3]: special = st.checkbox("!@#", True)
                
            if st.button("Generate Password", key="generate_btn"):
                new_pw: str = generate_password(length, uppercase, lowercase, numbers, special)
                st.code(new_pw)
                st.success("Password generated! Copy it to a secure location.")

        with st.expander("ℹ️ Password Security Guide"):
            st.markdown("""
            ## Password Security Fundamentals
        
            **What makes a password strong?**
            - Length (12+ characters recommended)
            - Mix of character types (upper/lower case, numbers, symbols)
            - No common words or predictable patterns
            - Unique for each account/service
        
            **Common Attack Methods:**
            - Brute force attacks
            - Dictionary attacks
            - Credential stuffing
            - Social engineering
        
            **Advanced Protection Tips:**
            - Use passphrases instead of passwords
            - Enable multi-factor authentication
            - Regularly check for data breaches
            - Use a reputable password manager
            """)


if __name__ == "__main__":
    main()