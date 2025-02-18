import streamlit as st
import requests
import pandas as pd
import time
import matplotlib.pyplot as plt

# Set FastAPI backend URL
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Career Advisor", layout="wide")

st.title("🎯 AI-Powered Career Path Advisor")

# Step 1: Fetch Career Test Questions from FastAPI
st.subheader("📋 Take the Career Assessment Test")
response = requests.get(f"{API_URL}/career-test")

if response.status_code == 200:
    questions = response.json()["questions"]

    user_answers = []
    
    # Step 2: Display Questions in Streamlit
    for i, question in enumerate(questions):
        user_answers.append(st.radio(f"**{question['question']}**", question["options"], key=i))
    
    # Step 3: Submit Answers to FastAPI for Recommendations
    if st.button("🔍 Get Career Recommendations"):
        progress_bar = st.progress(0)  # Initialize progress bar

        # Simulating progress
        for percent_complete in range(100):
            time.sleep(0.01)
            progress_bar.progress(percent_complete + 1)

        response = requests.post(f"{API_URL}/career-test-submit", data={"answers": user_answers})
        
        if response.status_code == 200:
            progress_bar.empty()  # Remove progress bar after completion
            recommendations = response.json()
            st.subheader("💼 Recommended Careers Based on Your Answers:")

            career_titles = []
            salary_ranges = []

            # Step 4: Display Recommendations Using Columns for Better UI
            for i, career in enumerate(recommendations):
                with st.container():
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        st.markdown(f"### {i+1}. **{career['Career Title']}**")
                        st.write(f"**Industry:** {career['Industry']}")
                        st.write(f"💰 **Salary:** {career['Expected Salary (INR)']}")
                        st.write(f"🏢 **Hiring Companies:** {career['Top Hiring Private Companies in India']}")

                    with col2:
                        st.markdown(f"💡 **Entry-Level:** {career['Entry-Level Roles']}")
                        st.markdown(f"📈 **Mid-Level:** {career['Mid-Level Roles']}")
                        st.markdown(f"🏆 **Senior-Level:** {career['Senior-Level Roles']}")

                    st.divider()

                # Extract salary data for visualization
                career_titles.append(career["Career Title"])
                salary_ranges.append(career["Expected Salary (INR)"])

            # Step 5: Convert Salary Data into Numbers for Visualization
            def convert_salary_to_number(salary_str):
                """Converts salary range (e.g., '6-15 LPA') to an average numerical value."""
                try:
                    if not salary_str or salary_str.strip() == "":
                        return None  # Handle missing or empty salary values
                    
                    salary_range = salary_str.split(" LPA")[0]
                    salary_range = salary_range.replace("+", "")
                    values = [int(s) for s in salary_range.split("-") if s.isdigit()]
                    
                    if len(values) == 1:  
                        return values[0]  # If only one value (e.g., '30+ LPA'), return it
                    elif len(values) == 2:
                        return sum(values) / 2  # If range (e.g., '6-15 LPA'), return average
                    else:
                        return None  # Skip if formatting is unexpected

                except:
                    return None  # Handle any unexpected errors

            salary_values = [convert_salary_to_number(salary) for salary in salary_ranges]

            # Step 6: Display Salary Comparison Chart Only if Valid Data Exists
            valid_careers = [career_titles[i] for i in range(len(salary_values)) if salary_values[i] is not None]
            valid_salaries = [salary for salary in salary_values if salary is not None]

            if valid_salaries:
                st.subheader("📊 Salary Comparison for Recommended Careers")

                fig, ax = plt.subplots(figsize=(8, 5))
                ax.barh(valid_careers, valid_salaries, color="skyblue")
                ax.set_xlabel("Average Expected Salary (LPA)")
                ax.set_ylabel("Career Title")
                ax.set_title("Salary Comparison of Recommended Careers")
                st.pyplot(fig)
            else:
                st.warning("⚠️ Not enough valid salary data to display a comparison chart.")

        else:
            st.error("⚠️ Error fetching recommendations. Please try again.")
else:
    st.error("❌ Failed to load career test. Make sure FastAPI is running.")
