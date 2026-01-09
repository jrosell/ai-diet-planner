import os
import streamlit as st
import datetime
import time
import pandas as pd
import duckdb
import ollama
from ollama import chat
from ollama import ChatResponse
from dotenv import load_dotenv
from bmi_calc import calculate_bmi_status

# 1. Load Defaults from .env
load_dotenv()

# Extract values with fallbacks
ENV_WEIGHT = float(os.getenv("DEFAULT_WEIGHT", 70.0))
ENV_HEIGHT = int(os.getenv("DEFAULT_HEIGHT", 170))
ENV_AGE = int(os.getenv("DEFAULT_AGE", 30))
ENV_GENDER = os.getenv("DEFAULT_GENDER", "Man")

# CONSTANTS
AI_MODEL = "gemma3:1b"
DB_FILE = "diet_planner.db"
TABLE = "user_plans"

def setup():
    """Initializes local AI model and DuckDB table with observations column."""
    try:
        ollama.pull(AI_MODEL)
    except:
        pass
    
def setup():
    try:
        ollama.pull(AI_MODEL)
    except:
        pass
    
    with duckdb.connect(DB_FILE) as conn:
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE} (
                user_id VARCHAR,
                timestamp TIMESTAMP,
                weight DOUBLE,
                height INTEGER,
                age INTEGER,
                gender VARCHAR,
                diet_plan VARCHAR
            )
        """)
        cols = conn.execute(f"PRAGMA table_info('{TABLE}')").df()
        if 'observations' not in cols['name'].values:
            conn.execute(f"ALTER TABLE {TABLE} ADD COLUMN observations VARCHAR")
            st.toast("Database schema updated: Added observations column")

def generate_diet_plan(params):
    """Calls Ollama to generate a plan including custom observations."""
    try:
        prompt = f"""
        Create a personalized 7-day diet plan for:
        - {params['gender']}, {params['age']} years old
        - Weight: {params['weight']} kg
        - Height: {params['height']} cm
        - BMI: {params['bmi']} ({params['bmi_status']})
        
        Additional User Observations/Preferences:
        {params['observations'] if params['observations'] else "None provided."}
       
        Include: Daily calorie targets, macros, meal timing, and food recommendations.
        Make it practical and culturally adaptable.
        """
    
        response: ChatResponse = chat(model=AI_MODEL, messages=[
            {'role': 'user', 'content': prompt},
        ])
        return response['message']['content']
    except Exception as e:
        st.error(f"AI generation error: {str(e)}")
        return None

def save_to_db(user_id, plan, observations):
    """Persists plan and observations to DuckDB."""
    try:
        data = st.session_state.user_data
        with duckdb.connect(DB_FILE) as conn:
            conn.execute(f"INSERT INTO {TABLE} VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
                user_id, 
                datetime.datetime.now(), 
                data["weight"], 
                data["height"], 
                data["age"], 
                data["gender"], 
                plan,
                observations
            ))
        return True
    except Exception as e:
        st.error(f"Data saving error: {str(e)}")
        return False

def main():
    st.set_page_config(page_title="AI Diet Planner", page_icon="🍏", layout="wide")
    setup()
  
    if "user_data" not in st.session_state:
        st.session_state.user_data = None
    if "diet_plan" not in st.session_state:
        st.session_state.diet_plan = None
  
    st.title("🍏 AI-Powered Diet Planner")
    
    # --- SECTION 1: USER INPUT FORM ---
    with st.form("user_profile", clear_on_submit=False):
        st.subheader("Your Profile & Preferences")
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=ENV_WEIGHT)
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=ENV_HEIGHT)
        with col2:
            age = st.number_input("Age", min_value=18, max_value=100, value=ENV_AGE)
            gender_options = ["Man", "Woman"]
            default_ix = gender_options.index(ENV_GENDER) if ENV_GENDER in gender_options else 0
            gender = st.selectbox("Gender", gender_options, index=default_ix)
        
        observations = st.text_area("Custom Observations", placeholder="e.g., I'm allergic to nuts, I prefer vegetarian meals, or I exercise 3 times a week.")
      
        submitted = st.form_submit_button("Generate New Diet Plan")
      
        if submitted:
            bmi_result = calculate_bmi_status(weight, height)
            st.session_state.user_data = {
                "weight": weight, "height": height, 
                "age": age, "gender": gender,
                "bmi": bmi_result["value"],
                "bmi_status": bmi_result["status"],
                "observations": observations
            }

            st.subheader("📊 Current Assessment")
            if bmi_result["status"] == "normal":
                st.success(f"BMI: {bmi_result['value']} - {bmi_result['message']}")
            else:
                st.warning(f"BMI: {bmi_result['value']} - {bmi_result['message']}")

    # --- SECTION 2: NEW PLAN GENERATION ---
    if submitted and st.session_state.user_data:
        with st.spinner(f"🧠 {AI_MODEL} is crafting your plan..."):
            diet_plan = generate_diet_plan(st.session_state.user_data)

            if diet_plan:
                st.session_state.diet_plan = diet_plan
                user_id = f"user_{int(time.time())}"
                if save_to_db(user_id, diet_plan, observations):
                    st.toast("✅ Plan saved successfully!")
  
    # --- SECTION 3: DISPLAY CURRENT PLAN ---
    if st.session_state.diet_plan:
        st.divider()
        st.subheader("New Personalized Diet Plan")
        st.markdown(st.session_state.diet_plan)

    # --- SECTION 4: INTERACTIVE HISTORY ---
    st.divider()
    st.subheader("📚 Saved Plans History")
    
    try:
        with duckdb.connect(DB_FILE) as conn:
            # We fetch all columns including the new 'observations' and 'age'
            df_history = conn.execute(f"SELECT * FROM {TABLE} ORDER BY timestamp DESC").df()
        
        if not df_history.empty:
            st.info("💡 Click a row to view the saved plan and observations below.")
            
            # Added 'age' to column_order
            event = st.dataframe(
                df_history,
                column_order=("timestamp", "weight", "age", "height", "gender"),
                hide_index=True,
                use_container_width=True,
                on_select="rerun",
                selection_mode="single-row"
            )

            # Handle row selection click
            selected_rows = event.selection.rows
            if selected_rows:
                idx = selected_rows[0]
                saved_row = df_history.iloc[idx]
                
                st.success(f"Viewing Saved Plan from {saved_row['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                
                # Layout for saved plan metadata
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Weight", f"{saved_row['weight']} kg")
                m2.metric("Age", saved_row['age'])
                m3.metric("Gender", saved_row['gender'])
                m4.metric("Height", f"{saved_row['height']} cm")
                
                if saved_row['observations']:
                    st.info(f"**Observations for this plan:**\n\n{saved_row['observations']}")
                
                with st.expander("Expand Saved Plan Text", expanded=True):
                    st.markdown(saved_row['diet_plan'])
                
                st.download_button(
                    label="Download as Markdown",
                    data=saved_row['diet_plan'],
                    file_name=f"plan_{saved_row['timestamp'].strftime('%Y%m%d')}.md"
                )
        else:
            st.info("No previous plans found in local storage.")
            
    except Exception as e:
        st.error(f"History display error: {str(e)}")

if __name__ == "__main__":
    main()