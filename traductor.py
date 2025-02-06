import pandas as pd
from deep_translator import GoogleTranslator

def split_text(text, max_length=5000):
    """Splits text into chunks that do not exceed the max_length limit."""
    parts = []
    while len(text) > max_length:
        split_index = text[:max_length].rfind(".")  # Try splitting at the last full stop
        if split_index == -1:  # If no full stop is found, just split at max_length
            split_index = max_length
        parts.append(text[:split_index + 1])
        text = text[split_index + 1:].strip()  # Remove the processed part
    parts.append(text)  # Add the last remaining part
    return parts

def translate_large_text(text, translator):
    """Translates large text by splitting it into smaller parts."""
    parts = split_text(text)
    translated_parts = [translator.translate(part) for part in parts]
    return " ".join(translated_parts)

# Load the dataset (replace with your actual file path)
comentarios = pd.read_csv("data/airline-reviews-test.csv")

# Initialize translator
translator = GoogleTranslator(source="auto", target="en")

# Apply translation to each review
comentarios['Reviews'] = comentarios['Reviews'].astype(str).apply(lambda x: translate_large_text(x, translator))

# Save the translated data (optional)
comentarios.to_csv("data/comentarios-test.csv", index=False)
