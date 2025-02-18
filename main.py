import pandas as pd
from fastapi import FastAPI
from fastapi import Query
from typing import List
from fastapi import Path

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from fastapi import Form

# Load Sentence Transformer Model (AI Embeddings)


app = FastAPI()


embedding_model = SentenceTransformer("local_model")

# Load the career dataset
df = pd.read_csv("career_path_dataset_corrected.csv")

# Combine relevant text fields for better similarity matching
df["combined_text"] = df["Career Title"] + " " + df["Industry"] + " " + df["Entry-Level Roles"]

# Generate AI embeddings for all careers
df["career_embedding"] = df["combined_text"].apply(lambda x: embedding_model.encode(x))



@app.get("/")
def home():
    return {"message": "Welcome to the AI-Powered Career Path Advisor API"}

@app.get("/careers")
def get_all_careers():
    """Returns all career paths from the dataset"""
    return df.to_dict(orient="records")

@app.get("/careers_msg")
def careers_msg():
    return {"message": "List of careers"}


@app.get("/recommend_rule")
def recommend_careers_rule(skills: List[str] = Query([]), interests: List[str] = Query([])):
    """
    Returns career recommendations based on user's skills and interests.
    """
    if not skills and not interests:
        return {"error": "Please provide at least one skill or interest to get recommendations."}

    # Filter careers based on skills matching entry-level roles OR interests matching industry
    filtered_df = df[
        df["Entry-Level Roles"].str.contains('|'.join(skills), case=False, na=False) |
        df["Industry"].str.contains('|'.join(interests), case=False, na=False)
    ]

    # If no careers match, return a message
    if filtered_df.empty:
        return {"message": "No matching careers found. Try different skills or interests."}

    return filtered_df.to_dict(orient="records")

@app.get("/recommend")
def recommend_careers(skills: List[str] = Query([]), interests: List[str] = Query([]), top_n: int = 3):
    """
    Returns career recommendations using AI similarity matching.
    """
    if not skills and not interests:
        return {"error": "Please provide at least one skill or interest to get recommendations."}

    # Convert user input into a single text string
    user_text = " ".join(skills + interests)

    # Generate AI embedding for the user input
    user_embedding = embedding_model.encode(user_text).reshape(1, -1)

    # Compute similarity scores between user input and all career paths
    df["similarity"] = df["career_embedding"].apply(lambda x: cosine_similarity(user_embedding, x.reshape(1, -1))[0][0])

    # Sort by similarity score in descending order
    recommended_careers = df.sort_values(by="similarity", ascending=False).head(top_n)

    return recommended_careers.drop(columns=["career_embedding", "combined_text", "similarity"]).to_dict(orient="records")



@app.get("/career-path/{career_id}")
def get_career_path(career_id: str = Path(..., title="Career Title")):
    """
    Returns full career path details for a given career title.
    """
    career = df[df["Career Title"].str.lower() == career_id.lower()]

    if career.empty:
        return {"message": "Career not found. Please check the career title."}

    return career.to_dict(orient="records")[0]



# Define career test questions
career_test_questions = [
    {"question": "What kind of work do you enjoy the most?", 
     "options": ["Analyzing data and finding patterns", 
                 "Building and coding software applications", 
                 "Solving cybersecurity challenges", 
                 "Creating designs and improving user experience", 
                 "Managing business operations and growth strategies"]},
    
    {"question": "What best describes your problem-solving approach?", 
     "options": ["Using logic and structured methods", 
                 "Experimenting with new technologies", 
                 "Investigating and securing systems", 
                 "Creating new ideas and user-friendly solutions", 
                 "Optimizing business strategies"]},
    
    {"question": "Which tools or technologies excite you the most?", 
     "options": ["Python, SQL, Machine Learning", 
                 "Java, C++, Web Development", 
                 "Penetration Testing, Network Security", 
                 "Figma, Adobe XD, UI/UX tools", 
                 "Business Intelligence, Marketing Tools"]}
]

@app.get("/career-test")
def get_career_test():
    """Returns the career assessment test questions."""
    return {"questions": career_test_questions}

@app.post("/career-test-submit")
def submit_career_test(answers: list = Form(...)):
    """
    Processes career test answers and generates recommended careers.
    """
    skills = []
    interests = []

    # Mapping user responses to skills and interests
    for answer in answers:
        if answer == "Analyzing data and finding patterns":
            skills.append("Data Science")
            interests.append("AI")
        elif answer == "Building and coding software applications":
            skills.append("Software Development")
            interests.append("AI")
        elif answer == "Solving cybersecurity challenges":
            skills.append("Cybersecurity")
            interests.append("IT Security")
        elif answer == "Creating designs and improving user experience":
            skills.append("UI/UX")
            interests.append("Marketing")
        elif answer == "Managing business operations and growth strategies":
            skills.append("Business Analysis")
            interests.append("Finance")
    
    return recommend_careers(skills=skills, interests=interests)

# Run this using: uvicorn main:app --reload
