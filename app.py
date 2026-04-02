import streamlit as st
import pickle
import time
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
#  MONGODB CONNECTION (lazy — only connects when needed)
# ─────────────────────────────────────────────────────────────────────────────
from datetime import datetime
import streamlit as st


@st.cache_resource
def get_mongo_client():
    try:
        from pymongo import MongoClient
        MONGO_URI = st.secrets.get("MONGO_URI", "mongodb://localhost:27017/")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")          # verify connection
        return client
    except Exception:
        return None                           # silently fail — app still works


def save_prediction(disease, inputs, result):
    """Save one prediction record to MongoDB."""
    client = get_mongo_client()
    if client is None:
        return
    try:
        db  = client["MedAI"]
        col = db["predictions"]
        doc = {
            "disease":   disease,
            "inputs":    inputs,
            "result":    str(result),         # ✅ ensure result is stored as string
            "timestamp": datetime.utcnow(),
        }
        col.insert_one(doc)
    except Exception:
        pass                                  # don't crash the app on DB errors


def get_prediction_history(disease=None, limit=50):
    """Retrieve recent predictions from MongoDB."""
    client = get_mongo_client()
    if client is None:
        return []
    try:
        db  = client["MedAI"]
        col = db["predictions"]
        q   = {"disease": disease} if disease else {}
        return list(col.find(q, {"_id": 0}).sort("timestamp", -1).limit(limit))
    except Exception:
        return []

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="MedAI Diagnosis", page_icon="⚕️", layout="wide")

# ─────────────────────────────────────────────────────────────────────────────
#  FULL CSS + ANIMATIONS
# ─────────────────────────────────────────────────────────────────────────────
css = """
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --bg-deep:       #050d1a;
    --bg-card:       rgba(10, 22, 45, 0.85);
    --accent-cyan:   #00e5ff;
    --accent-blue:   #2979ff;
    --accent-violet: #7c4dff;
    --accent-green:  #00e676;
    --accent-orange: #ff6d00;
    --text-primary:  #e8f4fd;
    --text-muted:    #7a9bbf;
    --border-subtle: rgba(0, 229, 255, 0.14);
    --border-glow:   rgba(0, 229, 255, 0.5);
    --shadow-card:   0 8px 40px rgba(0,0,0,0.55), 0 0 0 1px var(--border-subtle);
    --shadow-glow:   0 0 32px rgba(0,229,255,0.22);
    --radius-card:   18px;
    --radius-input:  12px;
    --font-head:     'Syne', sans-serif;
    --font-body:     'DM Sans', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    color: var(--text-primary) !important;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

/* ── ANIMATED BACKGROUND ── */
[data-testid="stAppViewContainer"] {
    background-color: var(--bg-deep);
    background-image:
        radial-gradient(ellipse 80% 60% at 10% 0%,   rgba(41,121,255,0.22) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 90% 10%,  rgba(124,77,255,0.18) 0%, transparent 55%),
        radial-gradient(ellipse 70% 60% at 50% 100%, rgba(0,229,255,0.12)  0%, transparent 60%),
        url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none'%3E%3Cg fill='%2300e5ff' fill-opacity='0.025'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    min-height: 100vh;
    animation: bgShift 18s ease-in-out infinite alternate;
}
@keyframes bgShift {
    0%   { background-position: 0% 0%, 100% 10%, 50% 100%, 0 0; }
    100% { background-position: 5% 5%, 95% 15%, 55% 95%, 0 0; }
}

[data-testid="stSidebar"] {
    background: rgba(4,10,22,0.97) !important;
    border-right: 1px solid var(--border-subtle) !important;
    backdrop-filter: blur(24px);
}

.block-container {
    padding: 2rem 3rem 4rem !important;
    max-width: 980px !important;
}

h1, h2, h3 {
    font-family: var(--font-head) !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
}

p {
    font-family: var(--font-body) !important;
    color: var(--text-muted) !important;
    font-size: 0.95rem !important;
    line-height: 1.75 !important;
    font-weight: 300 !important;
}

/* ── GLASS COLUMNS ── */
div[data-testid="column"] {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-card);
    padding: 1.6rem !important;
    box-shadow: var(--shadow-card);
    backdrop-filter: blur(18px);
    transition: border-color 0.35s, box-shadow 0.35s, transform 0.35s;
    animation: slideUp 0.5s cubic-bezier(0.22,1,0.36,1) both;
}
div[data-testid="column"]:hover {
    border-color: var(--border-glow);
    box-shadow: var(--shadow-card), var(--shadow-glow);
    transform: translateY(-2px);
}

/* ── INPUT LABELS ── */
label,
.stTextInput label,
.stNumberInput label,
.stSelectbox label {
    font-family: var(--font-body) !important;
    font-size: 0.76rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: var(--accent-cyan) !important;
    margin-bottom: 3px !important;
}

/* ── INPUT FIELDS ── */
input[type="text"],
input[type="number"],
textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: rgba(0,229,255,0.05) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-input) !important;
    color: #8b4513 !important;
    -webkit-text-fill-color: #8b4513 !important;
    font-family: var(--font-body) !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    padding: 0.65rem 1rem !important;
    transition: border-color 0.25s, box-shadow 0.25s, background 0.25s !important;
    caret-color: var(--accent-cyan) !important;
}
input[type="text"]:focus,
input[type="number"]:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,0.18), 0 0 20px rgba(0,229,255,0.12) !important;
    background: rgba(0,229,255,0.08) !important;
    outline: none !important;
    color: #8b4513 !important;
    -webkit-text-fill-color: #8b4513 !important;
}
input::placeholder { color: rgba(255,255,255,0.3) !important; }

/* ── NUMBER SPINNER ── */
[data-testid="stNumberInput"] button {
    background: rgba(0,229,255,0.08) !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--accent-cyan) !important;
    border-radius: 8px !important;
    transition: background 0.2s, transform 0.15s !important;
}
[data-testid="stNumberInput"] button:hover {
    background: rgba(0,229,255,0.2) !important;
    transform: scale(1.12) !important;
}

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] > div > div {
    background: rgba(0,229,255,0.05) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-input) !important;
    color: #ffffff !important;
    font-family: var(--font-body) !important;
    transition: border-color 0.25s, box-shadow 0.25s !important;
}
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,0.18) !important;
}
[data-testid="stSelectbox"] svg { color: var(--accent-cyan) !important; }

/* ── BUTTONS — FIX 1: clear white text on dark-to-blue gradient ── */
.stButton > button {
    font-family: var(--font-head) !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;

    /* FIX: white text — visible on every background */
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;

    background: linear-gradient(135deg, #0088cc 0%, #2979ff 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.78rem 2.4rem !important;
    cursor: pointer !important;
    position: relative !important;
    overflow: hidden !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    box-shadow: 0 4px 24px rgba(0,136,204,0.45), 0 0 0 1px rgba(0,229,255,0.3) !important;
    width: 100% !important;
    margin-top: 0.8rem !important;
}
.stButton > button::before {
    content: '' !important;
    position: absolute !important;
    top: 0; left: -100% !important;
    width: 100%; height: 100% !important;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent) !important;
    transition: left 0.5s !important;
}
.stButton > button:hover::before { left: 100% !important; }
.stButton > button:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 10px 40px rgba(0,136,204,0.65) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}
.stButton > button:active { transform: translateY(0) scale(0.98) !important; }

/* ── ALERTS ── */
[data-testid="stAlert"], .stSuccess {
    background: linear-gradient(135deg, rgba(0,230,118,0.12) 0%, rgba(0,229,255,0.07) 100%) !important;
    border: 1px solid rgba(0,230,118,0.4) !important;
    border-radius: var(--radius-card) !important;
    padding: 1.2rem 1.5rem !important;
    box-shadow: 0 0 32px rgba(0,230,118,0.15) !important;
    backdrop-filter: blur(10px) !important;
    animation: popIn 0.45s cubic-bezier(0.34,1.56,0.64,1) both !important;
}
[data-testid="stAlert"] p, .stSuccess p {
    color: var(--accent-green) !important;
    font-family: var(--font-head) !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
}
[data-testid="stWarning"] {
    background: linear-gradient(135deg, rgba(255,109,0,0.12), rgba(255,200,0,0.06)) !important;
    border: 1px solid rgba(255,109,0,0.4) !important;
    border-radius: var(--radius-card) !important;
    animation: popIn 0.45s cubic-bezier(0.34,1.56,0.64,1) both !important;
}

/* ── ANIMATIONS ── */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(28px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes popIn {
    0%   { opacity: 0; transform: scale(0.85) translateY(10px); }
    70%  { transform: scale(1.03) translateY(-2px); }
    100% { opacity: 1; transform: scale(1) translateY(0); }
}
@keyframes floatOrb {
    0%, 100% { transform: translateY(0px) translateX(0px); }
    33%       { transform: translateY(-18px) translateX(8px); }
    66%       { transform: translateY(10px) translateX(-6px); }
}

.block-container { animation: fadeSlideUp 0.55s cubic-bezier(0.22,1,0.36,1) both; }

hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, var(--accent-cyan), var(--accent-violet), transparent) !important;
    margin: 1.8rem 0 !important;
    opacity: 0.35 !important;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(var(--accent-blue), var(--accent-cyan));
    border-radius: 999px;
}

[data-testid="stTooltipIcon"] svg { color: var(--accent-cyan) !important; opacity: 0.55; }
[data-testid="stTooltipIcon"]:hover svg { opacity: 1; }

[data-testid="stInfo"] {
    background: rgba(41,121,255,0.1) !important;
    border: 1px solid rgba(41,121,255,0.3) !important;
    border-radius: 12px !important;
    animation: slideUp 0.4s ease both !important;
}

[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 14px !important;
    animation: slideUp 0.4s ease both;
    margin-bottom: 0.7rem !important;
}
[data-testid="stExpander"] summary {
    font-family: var(--font-head) !important;
    color: var(--accent-cyan) !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
}

/* Tab styling */
[data-testid="stTabs"] [role="tab"] {
    font-family: var(--font-head) !important;
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--accent-cyan) !important;
    border-bottom-color: var(--accent-cyan) !important;
}

/* ── FIX 2: disease-card predict button — centered, darker bg, clear white text ── */
.card-btn-wrap {
    display: flex;
    justify-content: center;
    margin-top: 0.8rem;
}
.card-btn-wrap .stButton > button {
    width: auto !important;
    min-width: 130px !important;
    padding: 0.6rem 1.8rem !important;
    font-size: 0.82rem !important;
    background: linear-gradient(135deg, #006fa8 0%, #1a5fd1 100%) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    box-shadow: 0 4px 18px rgba(0,111,168,0.5) !important;
    margin-top: 0 !important;
}
.card-btn-wrap .stButton > button:hover {
    background: linear-gradient(135deg, #0088cc 0%, #2979ff 100%) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}
"""
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"
if "selected_disease" not in st.session_state:
    st.session_state.selected_disease = "Diabetes"

# ─────────────────────────────────────────────────────────────────────────────
#  LOAD MODELS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_models():
    return {
        'diabetes':      pickle.load(open('Models/diabetes_model.sav', 'rb')),
        'heart_disease': pickle.load(open('Models/heart_disease_model.sav', 'rb')),
        'parkinsons':    pickle.load(open('Models/parkinsons_model.sav', 'rb')),
        'lung_cancer':   pickle.load(open('Models/lungs_disease_model.sav', 'rb')),
        'thyroid':       pickle.load(open('Models/Thyroid_model.sav', 'rb')),
    }
models = load_models()

# ─────────────────────────────────────────────────────────────────────────────
#  DISEASE DATA
# ─────────────────────────────────────────────────────────────────────────────
DISEASES = {
    "Diabetes": {
        "icon": "🩸",
        "color": "#00e5ff",
        "tagline": "Blood Sugar Disorder",
        "description": "Diabetes is a chronic metabolic disease where the body cannot properly regulate blood glucose. Type 2 diabetes affects over 500 million people worldwide and is closely linked to insulin resistance, obesity, and genetics.",
        "symptoms": ["Frequent urination", "Excessive thirst", "Blurred vision", "Slow-healing wounds", "Unexplained weight loss", "Fatigue & weakness"],
        "prevention": ["Maintain healthy BMI (18.5–24.9)", "Exercise 150 min/week", "Limit refined carbs & sugars", "Regular blood sugar monitoring", "Avoid smoking & excess alcohol"],
        "treatment": ["Metformin or insulin therapy", "Low-GI diet plan", "Regular HbA1c testing every 3 months", "Weight management programs", "Continuous glucose monitoring (CGM)"],
    },
    "Heart Disease": {
        "icon": "❤️",
        "color": "#ff4d6d",
        "tagline": "Cardiovascular Condition",
        "description": "Heart disease encompasses conditions affecting the heart's structure and function, including coronary artery disease and heart failure. It is the #1 cause of death globally, responsible for 17.9 million deaths annually.",
        "symptoms": ["Chest pain or pressure", "Shortness of breath", "Irregular heartbeat", "Fatigue", "Dizziness or fainting", "Swollen ankles or feet"],
        "prevention": ["Control blood pressure & cholesterol", "Follow Mediterranean diet", "No smoking", "Manage stress levels", "Regular cardiac screenings after age 40"],
        "treatment": ["Statins & antihypertensives", "Angioplasty or bypass surgery", "Cardiac rehabilitation programs", "Aspirin therapy (as prescribed)", "Lifestyle modification & diet"],
    },
    "Parkinson's": {
        "icon": "🧠",
        "color": "#a855f7",
        "tagline": "Neurological Movement Disorder",
        "description": "Parkinson's disease is a progressive neurological disorder caused by the loss of dopamine-producing neurons, leading to tremors, stiffness, and impaired movement. It affects ~10 million people worldwide with no known cure.",
        "symptoms": ["Resting tremors", "Muscle rigidity", "Slowed movement (bradykinesia)", "Balance difficulties", "Soft or slurred speech", "Loss of automatic movements"],
        "prevention": ["Regular aerobic exercise", "High caffeine intake (associated with lower risk)", "Avoid pesticide exposure", "Mediterranean or MIND diet", "Head injury prevention"],
        "treatment": ["Levodopa/Carbidopa medication", "Dopamine agonists", "Deep Brain Stimulation (DBS)", "Physiotherapy & speech therapy", "Occupational therapy for daily living"],
    },
    "Lung Cancer": {
        "icon": "🛡️",
        "color": "#22d3ee",
        "tagline": "Pulmonary Malignancy",
        "description": "Lung cancer is the leading cause of cancer deaths worldwide, accounting for ~1.8 million deaths annually. It is primarily caused by smoking (85% of cases), but environmental and genetic factors also contribute significantly.",
        "symptoms": ["Persistent cough", "Coughing up blood", "Chest pain", "Hoarseness", "Unexplained weight loss", "Bone pain & headache (advanced)"],
        "prevention": ["Stop smoking immediately", "Avoid secondhand smoke", "Test home for radon gas", "Avoid carcinogen exposure at work", "Annual low-dose CT scan (high-risk groups)"],
        "treatment": ["Surgery (lobectomy/pneumonectomy)", "Chemotherapy & radiation", "Targeted therapy (EGFR/ALK inhibitors)", "Immunotherapy (PD-1/PD-L1 inhibitors)", "Palliative & supportive care"],
    },
    "Hypo-Thyroid": {
        "icon": "🔬",
        "color": "#34d399",
        "tagline": "Underactive Thyroid Gland",
        "description": "Hypothyroidism occurs when the thyroid gland fails to produce sufficient thyroid hormones, slowing metabolism and affecting nearly every organ. It affects ~5% of the population, with women being 5–10× more likely to develop it.",
        "symptoms": ["Fatigue & sluggishness", "Increased cold sensitivity", "Weight gain", "Puffy face", "Constipation", "Depression & brain fog"],
        "prevention": ["Adequate iodine intake", "Regular thyroid function tests", "Avoid excess goitrogenic foods", "Manage autoimmune conditions (Hashimoto's)", "Selenium-rich diet"],
        "treatment": ["Daily levothyroxine (T4) replacement", "Regular TSH level monitoring every 6–12 months", "Dietary adjustments", "Exercise for metabolic support", "Treating underlying autoimmune cause"],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def header_banner():
    st.markdown("""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.4rem;
                animation:fadeSlideUp 0.6s cubic-bezier(0.22,1,0.36,1) both;">
        <div style="width:52px;height:52px;background:linear-gradient(135deg,#00e5ff,#2979ff);
                    border-radius:15px;display:flex;align-items:center;justify-content:center;
                    font-size:1.6rem;box-shadow:0 0 28px rgba(0,229,255,0.5);flex-shrink:0;
                    animation:floatOrb 6s ease-in-out infinite;">⚕️</div>
        <div>
            <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.9rem;
                        letter-spacing:-0.02em;
                        background:linear-gradient(135deg,#ffffff 0%,#00e5ff 55%,#2979ff 100%);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        line-height:1.1;">MedAI Diagnosis</div>
            <div style="font-family:'DM Sans',sans-serif;font-size:0.78rem;color:#7a9bbf;
                        font-weight:300;letter-spacing:0.1em;text-transform:uppercase;">
                AI-Powered Health Prediction System</div>
        </div>
    </div>
    <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(0,229,255,0.4),transparent);
                margin-bottom:1.6rem;"></div>
    """, unsafe_allow_html=True)

def section_header(icon, title, subtitle, color="#8b4513"):
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem; animation: fadeSlideUp 0.5s ease both;">
        <div style="
            font-family: 'Syne', sans-serif;
            font-weight: 800;
            font-size: 2.4rem;
            letter-spacing: -0.03em;
            color: #ffffff;
            text-shadow: 2px 0.8px 0px {color};
            display: block;
            line-height: 1.1;
        ">
            {icon} {title}
        </div>
        <div style="
            font-family: 'DM Sans', sans-serif;
            color: {color};
            font-size: 1rem;
            font-weight: 600;
            margin-top: 8px;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        ">
            {subtitle}
        </div>
    </div>
    """, unsafe_allow_html=True)

def num_input(label, key, min_val, max_val, default=0, step=1, fmt="%.0f", note=""):
    full_label = f"{label}  ({note})" if note else label
    return st.number_input(full_label, min_value=float(min_val), max_value=float(max_val),
                           value=float(default), step=float(step), key=key, format=fmt)

def show_result(positive, pos_msg, neg_msg):
    with st.spinner("🔬 Analysing inputs..."):
        time.sleep(0.9)
    if positive:
        st.warning(f"⚠️ {pos_msg}")
        st.markdown("""
        <div style="background:rgba(255,109,0,0.08);border:1px solid rgba(255,109,0,0.25);
                    border-radius:12px;padding:0.9rem 1.2rem;margin-top:0.5rem;
                    animation:popIn 0.5s cubic-bezier(0.34,1.56,0.64,1) both;">
            <span style="color:#ffab40;font-family:'DM Sans',sans-serif;font-size:0.87rem;">
            💡 Please consult a qualified medical professional for proper diagnosis and treatment.
            </span></div>""", unsafe_allow_html=True)
    else:
        st.success(f"✅ {neg_msg}")
        st.markdown("""
        <div style="background:rgba(0,230,118,0.07);border:1px solid rgba(0,230,118,0.2);
                    border-radius:12px;padding:0.9rem 1.2rem;margin-top:0.5rem;
                    animation:popIn 0.5s cubic-bezier(0.34,1.56,0.64,1) both;">
            <span style="color:#69f0ae;font-family:'DM Sans',sans-serif;font-size:0.87rem;">
            ✨ Great news! Keep maintaining a healthy lifestyle. Regular check-ups are still recommended.
            </span></div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  NAV BAR
# ─────────────────────────────────────────────────────────────────────────────
header_banner()

nav_options = ["🏠 Home", "🔬 Predict", "📖 Disease Info", "💊 Recovery & Cure"]
nav_cols = st.columns(len(nav_options))
for i, opt in enumerate(nav_options):
    with nav_cols[i]:
        active = st.session_state.page == opt
        st.markdown(f"""<style>
        div[data-testid="stHorizontalBlock"] > div:nth-child({i+1}) button {{
            background: {'linear-gradient(135deg,#00e5ff,#2979ff)' if active else 'rgba(0,229,255,0.06)'} !important;
            color: {'#ffffff' if active else '#c8dff0'} !important;
            -webkit-text-fill-color: {'#ffffff' if active else '#c8dff0'} !important;
            border: 1px solid {'rgba(0,229,255,0.7)' if active else 'rgba(0,229,255,0.15)'} !important;
            font-size: 0.82rem !important;
            padding: 0.52rem 0.4rem !important;
            width: 100% !important;
            margin-top: 0 !important;
            font-weight: {'700' if active else '500'} !important;
            box-shadow: {'0 4px 20px rgba(0,229,255,0.3)' if active else 'none'} !important;
        }}
        </style>""", unsafe_allow_html=True)
        if st.button(opt, key=f"nav_{i}"):
            st.session_state.page = opt
            st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)
page = st.session_state.page

# ─────────────────────────────────────────────────────────────────────────────
#  🏠 HOME PAGE
# ─────────────────────────────────────────────────────────────────────────────
if page == "🏠 Home":

    st.markdown("""
    <div style="text-align:center;padding:2.5rem 1rem 1rem;
                animation:fadeSlideUp 0.7s cubic-bezier(0.22,1,0.36,1) both;position:relative;">
        <div style="position:absolute;top:-30px;left:8%;width:130px;height:130px;
                    background:radial-gradient(circle,rgba(0,229,255,0.13),transparent 70%);
                    border-radius:50%;animation:floatOrb 7s ease-in-out infinite;pointer-events:none;"></div>
        <div style="position:absolute;top:-10px;right:10%;width:100px;height:100px;
                    background:radial-gradient(circle,rgba(124,77,255,0.13),transparent 70%);
                    border-radius:50%;animation:floatOrb 9s ease-in-out infinite reverse;pointer-events:none;"></div>
        <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:3rem;
                    letter-spacing:-0.03em;line-height:1.1;
                    background:linear-gradient(135deg,#ffffff 0%,#00e5ff 40%,#7c4dff 100%);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    margin-bottom:1rem;">
            AI-Powered Medical<br>Diagnosis System
        </div>
        <div style="font-family:'DM Sans',sans-serif;color:#7a9bbf;font-size:1rem;
                    font-weight:300;max-width:540px;margin:0 auto 2rem;line-height:1.75;">
            Predict 5 critical diseases instantly using trained machine learning models.
            Fast, accurate, and educational — not a substitute for professional medical advice.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Disease cards
    st.markdown("""<div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.9rem;
        color:#7a9bbf;text-align:center;letter-spacing:0.12em;text-transform:uppercase;
        margin-bottom:1rem;">Select a Disease to Get Started</div>""", unsafe_allow_html=True)

    d_list = list(DISEASES.items())
    row1 = st.columns(3)
    row2_wrap = st.columns([1, 1.5, 1.5, 1])
    row2 = [row2_wrap[1], row2_wrap[2]]
    all_cols = list(row1) + list(row2)

    for i, (dname, ddata) in enumerate(d_list):
        with all_cols[i]:
            # Disease info card (HTML only — no button inside)
            st.markdown(f"""
            <div style="background:rgba(10,22,45,0.9);border:1px solid {ddata['color']}33;
                        border-radius:18px;padding:1.5rem 1.5rem 0.5rem;text-align:center;
                        box-shadow:0 4px 30px rgba(0,0,0,0.4);
                        animation:slideUp 0.5s {0.08*i:.2f}s cubic-bezier(0.22,1,0.36,1) both;
                        transition:transform 0.3s,border-color 0.3s,box-shadow 0.3s;"
                 onmouseover="this.style.transform='translateY(-5px)';this.style.borderColor='{ddata['color']}88';this.style.boxShadow='0 14px 40px rgba(0,0,0,0.5),0 0 24px {ddata['color']}22';"
                 onmouseout="this.style.transform='';this.style.borderColor='{ddata['color']}33';this.style.boxShadow='0 4px 30px rgba(0,0,0,0.4)';">
                <div style="font-size:2.4rem;margin-bottom:0.5rem;
                            animation:floatOrb {5+i}s ease-in-out infinite;">{ddata['icon']}</div>
                <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;
                            color:{ddata['color']};margin-bottom:0.25rem;">{dname}</div>
                <div style="font-family:'DM Sans',sans-serif;font-size:0.74rem;
                            color:#7a9bbf;font-weight:300;margin-bottom:0.6rem;">{ddata['tagline']}</div>
            </div>""", unsafe_allow_html=True)

            # FIX: centered "Predict" button below each card
            st.markdown('<div class="card-btn-wrap">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("Predict", key=f"home_card_{i}"):
                    st.session_state.page = "🔬 Predict"
                    st.session_state.selected_disease = dname
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Stats
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    s_cols = st.columns(4)
    for col, (val, lab) in zip(s_cols, [("5", "Diseases Covered"), ("95%+", "Model Accuracy"), ("4 K", "Training Records"), ("Free", "Always")]):
        with col:
            st.markdown(f"""
            <div style="text-align:center;padding:0.8rem 0;animation:slideUp 0.5s ease both;">
                <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.9rem;
                            background:linear-gradient(135deg,#00e5ff,#2979ff);
                            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">{val}</div>
                <div style="font-family:'DM Sans',sans-serif;color:#7a9bbf;font-size:0.75rem;
                            text-transform:uppercase;letter-spacing:0.08em;">{lab}</div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  🔬 PREDICT PAGE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔬 Predict":

    disease_choice = st.selectbox(
        "🩺 Select Disease to Predict",
        list(DISEASES.keys()),
        index=list(DISEASES.keys()).index(st.session_state.selected_disease),
        key="predict_select"
    )
    st.session_state.selected_disease = disease_choice
    ddata = DISEASES[disease_choice]

    st.markdown("<hr>", unsafe_allow_html=True)
    section_header(ddata["icon"], disease_choice, ddata["tagline"], ddata["color"])

    st.markdown(f"""
    <div style="background:rgba(41,121,255,0.07);border-left:3px solid {ddata['color']};
                border-radius:0 12px 12px 0;padding:0.85rem 1.2rem;margin-bottom:1.5rem;
                animation:slideUp 0.4s ease both;">
        <span style="font-family:'DM Sans',sans-serif;color:#b0cce4;font-size:0.91rem;
                     font-weight:300;line-height:1.7;">{ddata['description'][:230]}...</span>
    </div>""", unsafe_allow_html=True)

    # ── DIABETES ──────────────────────────────────────────────
    if disease_choice == "Diabetes":
        col1, col2 = st.columns(2)
        with col1:
            Pregnancies              = num_input("Number of Pregnancies",       "Pregnancies",             0,   20,   1,    1,    "%.0f", "0 – 20 times")
            BloodPressure            = num_input("Blood Pressure (mm Hg)",      "BloodPressure",           0,   180,  70,   1,    "%.0f", "0 – 180 mm Hg")
            Insulin                  = num_input("Insulin Level (μU/mL)",       "Insulin",                 0,   900,  80,   1,    "%.0f", "0 – 900 μU/mL")
            DiabetesPedigreeFunction = num_input("Diabetes Pedigree Function",  "DiabetesPedigreeFunction",0.0, 2.5,  0.47, 0.001,"%.3f", "0.078 – 2.42")
        with col2:
            Glucose       = num_input("Glucose Level (mg/dL)",   "Glucose",      0,   300,  117, 1,   "%.0f", "70 – 200 mg/dL")
            SkinThickness = num_input("Skin Thickness (mm)",      "SkinThickness",0,   100,  20,  1,   "%.0f", "0 – 99 mm")
            BMI           = num_input("BMI (kg/m²)",              "BMI",          0.0, 70.0, 31.0,0.1, "%.1f", "15.0 – 67.1 kg/m²")
            Age           = num_input("Age (years)",              "Age",          1,   110,  33,  1,   "%.0f", "1 – 110 yrs")

        if st.button("🔍 Run Diabetes Prediction"):
            inputs = [Pregnancies, Glucose, BloodPressure, SkinThickness,
                      Insulin, BMI, DiabetesPedigreeFunction, Age]
            res = models['diabetes'].predict([inputs])
            result_text = "Diabetic" if res[0] == 1 else "Not Diabetic"
            show_result(res[0] == 1,
                        "The person is likely Diabetic",
                        "The person is likely Not Diabetic")
            save_prediction("Diabetes",
                            dict(Pregnancies=Pregnancies, Glucose=Glucose,
                                 BloodPressure=BloodPressure, SkinThickness=SkinThickness,
                                 Insulin=Insulin, BMI=BMI,
                                 DiabetesPedigreeFunction=DiabetesPedigreeFunction, Age=Age),
                            result_text)

    # ── HEART DISEASE ─────────────────────────────────────────
    elif disease_choice == "Heart Disease":
        col1, col2 = st.columns(2)
        with col1:
            age     = num_input("Age (years)",                        "hage",    1,   110, 54,  1,   "%.0f", "1 – 110 yrs")
            cp      = num_input("Chest Pain Type",                    "cp",      0,   3,   0,   1,   "%.0f", "0=none  1=typical  2=atypical  3=non-anginal")
            chol    = num_input("Serum Cholesterol (mg/dL)",          "chol",    100, 600, 246, 1,   "%.0f", "100 – 600 mg/dL")
            restecg = num_input("Resting ECG Results",                "restecg", 0,   2,   0,   1,   "%.0f", "0=normal  1=ST-T abnorm  2=LV hypertrophy")
            exang   = num_input("Exercise Induced Angina",            "exang",   0,   1,   0,   1,   "%.0f", "0=No  1=Yes")
            slope   = num_input("ST Segment Slope",                   "slope",   0,   2,   1,   1,   "%.0f", "0=upsloping  1=flat  2=downsloping")
            thal    = num_input("Thalassemia",                        "thal",    0,   3,   2,   1,   "%.0f", "0=normal  1=fixed defect  2=reversible defect")
        with col2:
            sex      = num_input("Sex",                               "sex",     0,   1,   1,   1,   "%.0f", "0=Female  1=Male")
            trestbps = num_input("Resting Blood Pressure (mm Hg)",    "trestbps",80,  220, 132, 1,   "%.0f", "80 – 220 mm Hg")
            fbs      = num_input("Fasting Blood Sugar > 120 mg/dL",   "fbs",     0,   1,   0,   1,   "%.0f", "0=False  1=True")
            thalach  = num_input("Max Heart Rate Achieved (bpm)",     "thalach", 60,  220, 150, 1,   "%.0f", "60 – 220 bpm")
            oldpeak  = num_input("ST Depression (exercise vs rest)",  "oldpeak", 0.0, 7.0, 1.0, 0.1, "%.1f", "0.0 – 6.2")
            ca       = num_input("Major Vessels (fluoroscopy)",       "ca",      0,   4,   0,   1,   "%.0f", "0 – 4 vessels")

        if st.button("🔍 Run Heart Disease Prediction"):
            res = models['heart_disease'].predict([[age, sex, cp, trestbps, chol, fbs,
                                                    restecg, thalach, exang, oldpeak, slope, ca, thal]])
            result_text = "Heart Disease" if res[0] == 1 else "No Heart Disease"
            show_result(res[0] == 1,
                        "The person likely has Heart Disease",
                        "The person likely does Not have Heart Disease")
            save_prediction("Heart Disease",
                            dict(age=age, sex=sex, cp=cp, trestbps=trestbps, chol=chol,
                                 fbs=fbs, restecg=restecg, thalach=thalach, exang=exang,
                                 oldpeak=oldpeak, slope=slope, ca=ca, thal=thal),
                            result_text)

    # ── PARKINSON'S ───────────────────────────────────────────
    elif disease_choice == "Parkinson's":
        col1, col2, col3 = st.columns(3)
        fields = [
            ("MDVP:Fo(Hz)",      "fo",             85.0,   270.0,  154.2,  0.001,   "%.3f", "85 – 260 Hz"),
            ("MDVP:Fhi(Hz)",     "fhi",            102.0,  592.0,  197.1,  0.001,   "%.3f", "102 – 592 Hz"),
            ("MDVP:Flo(Hz)",     "flo",            65.0,   240.0,  116.3,  0.001,   "%.3f", "65 – 240 Hz"),
            ("MDVP:Jitter(%)",   "Jitter_percent", 0.0,    0.033,  0.006,  0.00001, "%.5f", "0 – 0.033"),
            ("MDVP:Jitter(Abs)", "Jitter_Abs",     0.0,    0.0003, 0.00004,0.000001,"%.6f", "0 – 0.00026"),
            ("MDVP:RAP",         "RAP",            0.0,    0.025,  0.003,  0.00001, "%.5f", "0 – 0.021"),
            ("MDVP:PPQ",         "PPQ",            0.0,    0.020,  0.003,  0.00001, "%.5f", "0 – 0.019"),
            ("Jitter:DDP",       "DDP",            0.0,    0.070,  0.010,  0.00001, "%.5f", "0 – 0.063"),
            ("MDVP:Shimmer",     "Shimmer",        0.009,  0.119,  0.029,  0.001,   "%.4f", "0.009 – 0.119"),
            ("MDVP:Shimmer(dB)", "Shimmer_dB",     0.085,  1.302,  0.282,  0.001,   "%.3f", "0.085 – 1.302 dB"),
            ("Shimmer:APQ3",     "APQ3",           0.004,  0.056,  0.015,  0.001,   "%.4f", "0.004 – 0.056"),
            ("Shimmer:APQ5",     "APQ5",           0.006,  0.079,  0.018,  0.001,   "%.4f", "0.006 – 0.079"),
            ("MDVP:APQ",         "APQ",            0.007,  0.137,  0.024,  0.001,   "%.4f", "0.007 – 0.137"),
            ("Shimmer:DDA",      "DDA",            0.013,  0.169,  0.044,  0.001,   "%.4f", "0.013 – 0.169"),
            ("NHR",              "NHR",            0.0,    0.315,  0.025,  0.001,   "%.4f", "0.000 – 0.315"),
            ("HNR",              "HNR",            8.4,    33.0,   21.9,   0.01,    "%.2f", "8.4 – 33.0 dB"),
            ("RPDE",             "RPDE",           0.256,  0.686,  0.498,  0.001,   "%.4f", "0.256 – 0.686"),
            ("DFA",              "DFA",            0.574,  0.825,  0.718,  0.001,   "%.4f", "0.574 – 0.825"),
            ("Spread1",          "spread1",        -7.964,-2.434, -5.684, 0.001,    "%.4f", "-7.96 – -2.43"),
            ("Spread2",          "spread2",        0.006,  0.450,  0.227,  0.001,   "%.4f", "0.006 – 0.450"),
            ("D2",               "D2",             1.423,  3.672,  2.382,  0.001,   "%.4f", "1.42 – 3.67"),
            ("PPE",              "PPE",            0.044,  0.527,  0.206,  0.001,   "%.4f", "0.044 – 0.527"),
        ]
        vals = {}
        cols3 = [col1, col2, col3]
        for i, (lbl, key, mn, mx, dv, stp, fmt, note) in enumerate(fields):
            with cols3[i % 3]:
                vals[key] = num_input(lbl, key, mn, mx, dv, stp, fmt, note)

        if st.button("🔍 Run Parkinson's Prediction"):
            inp = [vals[k] for _, k, *_ in fields]
            res = models['parkinsons'].predict([inp])
            result_text = "Parkinson's Disease" if res[0] == 1 else "No Parkinson's Disease"
            show_result(res[0] == 1,
                        "The person likely has Parkinson's Disease",
                        "The person likely does Not have Parkinson's Disease")
            save_prediction("Parkinson's", vals, result_text)

    # ── LUNG CANCER ───────────────────────────────────────────
    elif disease_choice == "Lung Cancer":
        col1, col2 = st.columns(2)
        with col1:
            GENDER               = num_input("Gender",               "GENDER",    0, 1, 1, 1, "%.0f", "0=Female  1=Male")
            SMOKING              = num_input("Smoking",              "SMOKING",   1, 2, 1, 1, "%.0f", "1=No  2=Yes")
            ANXIETY              = num_input("Anxiety",              "ANXIETY",   1, 2, 1, 1, "%.0f", "1=No  2=Yes")
            CHRONIC_DISEASE      = num_input("Chronic Disease",      "CHRONIC_DISEASE", 1, 2, 1, 1, "%.0f", "1=No  2=Yes")
            ALLERGY              = num_input("Allergy",              "ALLERGY",   1, 2, 1, 1, "%.0f", "1=No  2=Yes")
            ALCOHOL_CONSUMING    = num_input("Alcohol Consuming",    "ALCOHOL_CONSUMING", 1, 2, 1, 1, "%.0f", "1=No  2=Yes")
            SHORTNESS_OF_BREATH  = num_input("Shortness of Breath",  "SHORTNESS_OF_BREATH", 1, 2, 1, 1, "%.0f", "1=No  2=Yes")
            CHEST_PAIN           = num_input("Chest Pain",           "CHEST_PAIN", 1, 2, 1, 1, "%.0f", "1=No  2=Yes")
        with col2:
            AGE                  = num_input("Age (years)",          "LAGE",      1,  110, 55, 1, "%.0f", "1 – 110 yrs")
            YELLOW_FINGERS       = num_input("Yellow Fingers",       "YELLOW_FINGERS", 1, 2, 1, 1, "%.0f", "1=No  2=Yes")
            PEER_PRESSURE        = num_input("Peer Pressure",        "PEER_PRESSURE", 1, 2, 1, 1, "%.0f", "1=No  2=Yes")
            FATIGUE              = num_input("Fatigue",              "FATIGUE",   1, 2, 1, 1, "%.0f", "1=No  2=Yes")
            WHEEZING             = num_input("Wheezing",             "WHEEZING",  1, 2, 1, 1, "%.0f", "1=No  2=Yes")
            COUGHING             = num_input("Coughing",             "COUGHING",  1, 2, 1, 1, "%.0f", "1=No  2=Yes")
            SWALLOWING_DIFFICULTY= num_input("Swallowing Difficulty","SWALLOWING_DIFFICULTY", 1, 2, 1, 1, "%.0f", "1=No  2=Yes")

        if st.button("🔍 Run Lung Cancer Prediction"):
            res = models['lung_cancer'].predict([[GENDER, AGE, SMOKING, YELLOW_FINGERS, ANXIETY,
                                                   PEER_PRESSURE, CHRONIC_DISEASE, FATIGUE, ALLERGY,
                                                   WHEEZING, ALCOHOL_CONSUMING, COUGHING,
                                                   SHORTNESS_OF_BREATH, SWALLOWING_DIFFICULTY, CHEST_PAIN]])
            result_text = "Lung Cancer" if res[0] == 1 else "No Lung Cancer"
            show_result(res[0] == 1,
                        "The person likely has Lung Cancer",
                        "The person likely does Not have Lung Cancer")
            save_prediction("Lung Cancer",
                            dict(GENDER=GENDER, AGE=AGE, SMOKING=SMOKING,
                                 YELLOW_FINGERS=YELLOW_FINGERS, ANXIETY=ANXIETY,
                                 PEER_PRESSURE=PEER_PRESSURE, CHRONIC_DISEASE=CHRONIC_DISEASE,
                                 FATIGUE=FATIGUE, ALLERGY=ALLERGY, WHEEZING=WHEEZING,
                                 ALCOHOL_CONSUMING=ALCOHOL_CONSUMING, COUGHING=COUGHING,
                                 SHORTNESS_OF_BREATH=SHORTNESS_OF_BREATH,
                                 SWALLOWING_DIFFICULTY=SWALLOWING_DIFFICULTY,
                                 CHEST_PAIN=CHEST_PAIN),
                            result_text)

    # ── HYPO-THYROID ──────────────────────────────────────────
    elif disease_choice == "Hypo-Thyroid":
        col1, col2 = st.columns(2)
        with col1:
            age          = num_input("Age (years)",        "tage",        1,   110,  44,  1,    "%.0f", "1 – 110 yrs")
            on_thyroxine = num_input("On Thyroxine",       "on_thyroxine",0,   1,    0,   1,    "%.0f", "0=No  1=Yes")
            t3_measured  = num_input("T3 Measured",        "t3_measured", 0,   1,    1,   1,    "%.0f", "0=No  1=Yes")
            tt4          = num_input("TT4 Level (nmol/L)", "tt4",         0.0, 600.0,100.0,0.1, "%.1f", "10 – 260 nmol/L (normal)")
        with col2:
            sex = num_input("Sex",               "tsex", 0,   1,   0,   1,    "%.0f", "0=Female  1=Male")
            tsh = num_input("TSH Level (mIU/L)", "tsh",  0.0, 100.0,2.5, 0.01,"%.2f", "0.4 – 4.0 mIU/L (normal)")
            t3  = num_input("T3 Level (nmol/L)", "t3",   0.0, 10.0, 1.8, 0.01,"%.2f", "1.2 – 3.1 nmol/L (normal)")

        if st.button("🔍 Run Thyroid Prediction"):
            res = models['thyroid'].predict([[age, sex, on_thyroxine, tsh, t3_measured, t3, tt4]])
            result_text = "Hypo-Thyroid" if res[0] == 1 else "No Hypo-Thyroid"
            show_result(res[0] == 1,
                        "The person likely has Hypo-Thyroid Disease",
                        "The person likely does Not have Hypo-Thyroid Disease")
            save_prediction("Hypo-Thyroid",
                            dict(age=age, sex=sex, on_thyroxine=on_thyroxine,
                                 tsh=tsh, t3_measured=t3_measured, t3=t3, tt4=tt4),
                            result_text)

# ─────────────────────────────────────────────────────────────────────────────
#  📖 DISEASE INFO PAGE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📖 Disease Info":
    section_header("📖", "Disease Information", "Learn about each condition in depth")

    tabs = st.tabs([f"{v['icon']} {k}" for k, v in DISEASES.items()])
    for tab, (dname, ddata) in zip(tabs, DISEASES.items()):
        with tab:
            st.markdown(f"""
            <div style="animation:fadeSlideUp 0.5s ease both;margin-bottom:1rem;">
                <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.55rem;
                            color:{ddata['color']};margin-bottom:0.4rem;">
                    {ddata['icon']} {dname}
                    <span style="font-size:0.82rem;color:#7a9bbf;font-weight:300;margin-left:8px;">
                        {ddata['tagline']}</span>
                </div>
                <p style="color:#b0cce4 !important;font-size:0.94rem !important;
                          line-height:1.75 !important;">{ddata['description']}</p>
            </div>""", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div style="background:rgba(10,22,45,0.9);border:1px solid {ddata['color']}33;
                            border-radius:16px;padding:1.3rem 1.5rem;
                            animation:slideUp 0.4s ease both;height:100%;">
                    <div style="font-family:'Syne',sans-serif;font-weight:700;color:{ddata['color']};
                                font-size:0.88rem;text-transform:uppercase;letter-spacing:0.08em;
                                margin-bottom:0.8rem;">⚡ Common Symptoms</div>
                    {''.join(f'<div style="font-family:DM Sans,sans-serif;color:#b0cce4;font-size:0.87rem;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);">• {s}</div>' for s in ddata['symptoms'])}
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div style="background:rgba(10,22,45,0.9);border:1px solid rgba(0,230,118,0.25);
                            border-radius:16px;padding:1.3rem 1.5rem;
                            animation:slideUp 0.4s 0.1s ease both;height:100%;">
                    <div style="font-family:'Syne',sans-serif;font-weight:700;color:#00e676;
                                font-size:0.88rem;text-transform:uppercase;letter-spacing:0.08em;
                                margin-bottom:0.8rem;">🛡️ Prevention</div>
                    {''.join(f'<div style="font-family:DM Sans,sans-serif;color:#b0cce4;font-size:0.87rem;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);">✓ {s}</div>' for s in ddata['prevention'])}
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"🔬 Predict {dname} Now", key=f"info_go_{dname}"):
                st.session_state.page = "🔬 Predict"
                st.session_state.selected_disease = dname
                st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  💊 RECOVERY & CURE PAGE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "💊 Recovery & Cure":
    section_header("💊", "Recovery & Cure", "Evidence-based treatment and lifestyle guidance")

    for dname, ddata in DISEASES.items():
        with st.expander(f"{ddata['icon']}  {dname}  —  {ddata['tagline']}"):
            st.markdown(f"""
            <div style="animation:fadeSlideUp 0.45s ease both;">
                <div style="font-family:'Syne',sans-serif;font-weight:700;color:{ddata['color']};
                            font-size:0.9rem;text-transform:uppercase;letter-spacing:0.08em;
                            margin-bottom:0.9rem;">💉 Treatment & Recovery Options</div>
                <div style="display:grid;gap:8px;margin-bottom:1rem;">
                    {''.join(f'''<div style="display:flex;align-items:flex-start;gap:10px;
                        background:rgba(255,255,255,0.03);border-radius:10px;
                        padding:10px 14px;border-left:3px solid {ddata["color"]}66;">
                        <span style="color:{ddata["color"]};font-size:1rem;flex-shrink:0;margin-top:1px;">▸</span>
                        <span style="font-family:DM Sans,sans-serif;color:#c0d8ee;font-size:0.87rem;line-height:1.5;">{t}</span>
                    </div>''' for t in ddata['treatment'])}
                </div>
                <div style="padding:0.85rem 1.1rem;
                            background:rgba(255,109,0,0.07);border:1px solid rgba(255,109,0,0.2);
                            border-radius:10px;font-family:DM Sans,sans-serif;
                            color:#ffab40;font-size:0.81rem;line-height:1.55;">
                    ⚠️ This information is for educational purposes only.
                    Always consult a licensed healthcare provider before starting any treatment.
                </div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding-top:1.1rem;
            border-top:1px solid rgba(0,229,255,0.09);
            text-align:center;font-family:'DM Sans',sans-serif;
            font-size:0.72rem;color:rgba(122,155,191,0.4);
            letter-spacing:0.08em;text-transform:uppercase;">
    <p>MedAI &nbsp;·&nbsp; For educational purposes only &nbsp;·&nbsp;
    Not a substitute for medical advice &nbsp;·&nbsp;  </p>
    <p style="font-size:0.72rem;">© 2025 <b>MedAI</b>. All Rights Reserved. </p>
</div>""", unsafe_allow_html=True)
