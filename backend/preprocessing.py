"""
Resume Text Preprocessing
"""

import re
import string

import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")


def clean_resume(text):
    """
    Clean resume text.
    """

    text = str(text)

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Remove emails
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove numbers
    text = re.sub(r"\d+", " ", text)

    # Remove punctuation
    text = text.translate(
        str.maketrans("", "", string.punctuation)
    )

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.lower().strip()


def preprocess_text(text):
    """
    Advanced NLP preprocessing using spaCy.
    """

    doc = nlp(clean_resume(text))

    tokens = [

        token.lemma_

        for token in doc

        if not token.is_stop
        and not token.is_punct
        and token.is_alpha

    ]

    return " ".join(tokens)