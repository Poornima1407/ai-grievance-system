import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# ===============================
# Load dataset
# ===============================
df = pd.read_csv("data/grievances.csv")

# ===============================
# Clean data (IMPORTANT)
# ===============================
# Keep only required columns
df = df[["Complaint_Text", "Department"]]

# Drop rows with missing values
df.dropna(inplace=True)

# Convert to string (safety)
df["Complaint_Text"] = df["Complaint_Text"].astype(str)
df["Department"] = df["Department"].astype(str)

# ===============================
# Features & Labels
# ===============================
X = df["Complaint_Text"]
y = df["Department"]

# ===============================
# Vectorization
# ===============================
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=3000
)

X_vec = vectorizer.fit_transform(X)

# ===============================
# Train model
# ===============================
model = MultinomialNB()
model.fit(X_vec, y)

# ===============================
# Save model
# ===============================
pickle.dump(model, open("grievance_model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("✅ Model trained successfully after cleaning NaN values")

