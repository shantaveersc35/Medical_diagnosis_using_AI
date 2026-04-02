# 🩺 MedAI Diagnosis System

An AI-powered medical diagnosis web application built using **Streamlit** and **Machine Learning**.  
This app predicts multiple diseases instantly and securely stores prediction history in **MongoDB Atlas**.

---

## 🚀 Features

- 🔬 Predict 5 major diseases:
  - Diabetes
  - Heart Disease
  - Parkinson’s Disease
  - Lung Cancer
  - Hypo-Thyroid

- 🎨 Modern UI with animations and responsive layout  
- ⚡ Fast real-time predictions using trained ML models  
- ☁️ Cloud deployment via Streamlit Cloud  
- 🗄️ MongoDB Atlas integration (stores prediction history)  
- 🔐 Secure handling of database credentials using Streamlit Secrets  

---

## 🧠 Technologies Used

- **Frontend & Backend:** Streamlit (Python)
- **Machine Learning:** Scikit-learn
- **Database:** MongoDB Atlas
- **Libraries:** NumPy, Pandas, Pickle
- **Deployment:** Streamlit Cloud

---

## 📂 Project Structure
```
project/
│
├── app.py
├── requirements.txt
├── Models/
│ ├── diabetes_model.sav
│ ├── heart_disease_model.sav
│ ├── parkinsons_model.sav
│ ├── lungs_disease_model.sav
│ └── Thyroid_model.sav
│
└── .streamlit/
└── secrets.toml 
```
---

## ⚙️ Setup & Run Locally

1. Install dependencies:

pip install -r requirements.txt

2. Run the app:

streamlit run app.py

3. Open in browser:

http://localhost:8501

---

## 🔐 MongoDB Setup

Create a `.streamlit/secrets.toml` file:

MONGO_URI = "your_mongodb_atlas_connection_string"

---

## 🌐 Live Demo

https://medai-diagnosis.streamlit.app

---

## 🧪 Example Stored Data

{
  "disease": "Diabetes",
  "inputs": [2, 120, 70, 20, 80, 30.5, 0.5, 25],
  "result": "Not Diabetic",
  "timestamp": "2026-04-01T10:30:00"
}

---


## 👨‍💻 Author

Shantaveerayya S C

---

## ⭐ Support

If you found this project useful:

- ⭐ Star this repository  
- Share with others  
- Give feedback  

---

