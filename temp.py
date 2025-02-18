import streamlit as st
import requests

# Set FastAPI backend URL
API_URL = "http://127.0.0.1:8000"

st.title("AI-Powered Career Path Advisor")

# Step 1: Fetch Career Test Questions from FastAPI
st.subheader("Career Assessment Test")
response = requests.get(f"{API_URL}/career-test")

if response.status_code == 200:
    questions = response.json()["questions"]

    user_answers = []
    
    # Step 2: Display Questions in Streamlit
    for i, question in enumerate(questions):
        user_answers.append(st.radio(question["question"], question["options"], key=i))
    
    # Step 3: Submit Answers to FastAPI for Recommendations
    if st.button("Get Career Recommendations"):
        response = requests.post(f"{API_URL}/career-test-submit", data={"answers": user_answers})
        
        if response.status_code == 200:
            recommendations = response.json()
            st.subheader("Recommended Careers Based on Your Answers:")
            
            for career in recommendations:
                st.write(f"**{career['Career Title']}** ({career['Industry']})")
                st.write(f"Entry-Level Roles: {career['Entry-Level Roles']}")
                st.write(f"Mid-Level Roles: {career['Mid-Level Roles']}")
                st.write(f"Senior-Level Roles: {career['Senior-Level Roles']}")
                st.write(f"Expected Salary: {career['Expected Salary (INR)']}")
                st.write(f"Top Hiring Companies: {career['Top Hiring Private Companies in India']}")
                st.write("---")
        else:
            st.error("Error fetching recommendations. Please try again.")

else:
    st.error("Failed to load career test. Make sure FastAPI is running.")
