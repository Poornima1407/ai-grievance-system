import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle

# Load your dataset
data = pd.read_csv("data/grievances.csv")

# Input and output columns (based on YOUR dataset)
X = data["Complaint_Text"]     # complaint text
y = data["Department"]         # department to predict

# Convert text to numeric form
vectorizer = TfidfVectorizer(stop_words="english")
X_vec = vectorizer.fit_transform(X)

# Train the model
model = MultinomialNB()
model.fit(X_vec, y)

# Save trained model
pickle.dump(model, open("grievance_model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("✅ Model trained using YOUR dataset successfully")
