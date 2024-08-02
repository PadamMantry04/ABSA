from flask import Flask, request, jsonify, render_template
import spacy
from flair.models import TextClassifier
from flair.data import Sentence
import re

app = Flask(__name__)

# Load English spaCy model
nlp = spacy.load("en_core_web_sm")

classifier = TextClassifier.load('en-sentiment')

# Function to extract aspects from a review
def extract_aspects(text):
    doc = nlp(text)
    aspects = []
    for chunk in doc.noun_chunks:
        aspects.append(chunk.text.lower())
    return aspects

def classify_aspects(reviews):
    aspect_sentiments = {'positive': [], 'negative': []}
    overall_sentiments = []

    for review in reviews:
        # Calculate overall sentiment for the review
        sentence_ov = Sentence(review)
        classifier.predict(sentence_ov)
        overall_sentiment = sentence_ov.labels[0].value
        overall_sentiments.append(overall_sentiment)

        # Tokenize the review into smaller parts using punctuations and conjunctions as delimiters
        parts = re.split(r'(?<!\w\b\b)\b(?:and|but|however|yet|or|so|therefore)\b|[.,?!]', review)
        parts = [part.strip() for part in parts if part.strip()]

        # Extract aspects and analyze sentiment for each part
        for part in parts:
            sentence = Sentence(part)
            classifier.predict(sentence)
            aspects = extract_aspects(part)
            for aspect in aspects:
                doc = nlp(aspect)
                filtered_words = [token.text for token in doc if not token.is_stop]
                filtered_aspect = ' '.join(filtered_words)
                sentiment = sentence.labels[0].value
                if sentiment == 'POSITIVE' and filtered_aspect:
                    aspect_sentiments['positive'].append(filtered_aspect)
                elif sentiment == 'NEGATIVE' and filtered_aspect:
                    aspect_sentiments['negative'].append(filtered_aspect)

    return aspect_sentiments, overall_sentiments

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    reviews = data.get('reviews', [])
    aspect_sentiments, overall_sentiments = classify_aspects(reviews)
    response = {
        'aspect_sentiments': aspect_sentiments,
        'overall_sentiments': overall_sentiments
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
