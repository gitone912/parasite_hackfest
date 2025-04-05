
import pickle
import re
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np

# Load the saved model and tokenizer
model = load_model("sentiment_model.h5")

with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

# Define the same cleaning function
def clean_tweet(tweet):
    tweet = re.sub(r'http\S+|www\S+|https\S+', '', tweet, flags=re.MULTILINE)
    tweet = re.sub(r'\@\w+|\#','', tweet)
    tweet = re.sub(r'\W', ' ', tweet)
    tweet = re.sub(r'\d', ' ', tweet)
    tweet = re.sub(r'\s+', ' ', tweet)
    tweet = tweet.strip()
    return tweet

# Manual tweets
manual_tweets = [
    "I absolutely love the new update!",
    "This app is terrible and full of bugs.",
    "Not sure how I feel about this, it's okay I guess.",
    "The customer service was fantastic.",
    "I'm never using this service again."
]

# Clean and preprocess
cleaned_manual = [clean_tweet(tweet.lower()) for tweet in manual_tweets]
sequences = tokenizer.texts_to_sequences(cleaned_manual)

# Use the same maxlen from training
maxlen = 56  # Replace with your actual maxlen value if different
padded_sequences = pad_sequences(sequences, maxlen=maxlen, padding='post')

# Predict
predictions = model.predict(padded_sequences)

# Decode predictions
label_map = {0: 'Negative', 1: 'Neutral', 2: 'Positive', 3: 'Irrelevant', 4: 'Mixed'}  # Adjust based on your dataset
predicted_labels = [label_map[np.argmax(pred)] for pred in predictions]

# Show results
for tweet, label in zip(manual_tweets, predicted_labels):
    print(f"Tweet: {tweet}\nPredicted Sentiment: {label}\n")