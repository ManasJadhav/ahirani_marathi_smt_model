import pandas as pd
import re
import unicodedata
from ai4bharat.transliteration import XlitEngine


indic_to_latin_engine = XlitEngine( beam_width=10, rescore=False)
latin_to_indic_engine = XlitEngine("mr", beam_width=10, rescore=True)


# Function to read training data from CSV file using pandas
def read_training_data_from_csv(file_path):
    df = pd.read_csv(file_path)
    training_data = dict(zip(df['ahirani_phrase'].str.strip(), df['marathi_phrases'].str.strip()))
    return training_data

training_data = read_training_data_from_csv('./data/Ahirani-Marathi Parallel Corpus - Sheet1.csv')


def translit_from_indic_to_latin(text):
  return indic_to_latin_engine.translit_sentence(text, lang_code="mr")

def translit_from_latin_to_indic(text):
  return latin_to_indic_engine.translit_sentence(text)

def lower_and_split_punct(text):
    # Split accented characters.
    text = unicodedata.normalize('NFKD', text)
    text = translit_from_indic_to_latin(text)
    text = text.lower()
    # Define the regular expression pattern to match punctuation marks
    punctuation_pattern = r'[?!.,"\':;\[\]\(\)\{\}]'
    # Remove punctuation marks from the sentence
    text = re.sub(punctuation_pattern, '', text)
    # Strip whitespace.
    text = text.strip()
    return text

# Transformation function
training_data = {lower_and_split_punct(key): lower_and_split_punct(value) for key, value in training_data.items()}

# Function to train IBM Model 1
def train_ibm_model1(training_data):
    translation_model = {}
    source_vocab = set()
    target_vocab = set()

    # Collect unique words in source and target sentences
    for src_sentence, tgt_translation in training_data.items():
        source_tokens = src_sentence.split()
        target_tokens = tgt_translation.split()
        source_vocab.update(source_tokens)
        target_vocab.update(target_tokens)

    # Initialize translation probabilities uniformly
    initial_prob = 1 / len(target_vocab)
    for src_word in source_vocab:
        translation_model[src_word] = {tgt_word: initial_prob for tgt_word in target_vocab}

    # Iteratively improve translation probabilities using EM algorithm (Expectation-Maximization)
    num_iterations = 1
    for _ in range(num_iterations):
        count = {src_word: {tgt_word: 0 for tgt_word in target_vocab} for src_word in source_vocab}
        total = {src_word: 0 for src_word in source_vocab}

        # E-step: Estimate expected counts
        for src_sentence, tgt_translation in training_data.items():
            source_tokens = src_sentence.split()
            target_tokens = tgt_translation.split()
            for src_word in source_tokens:
                total_prob = sum(translation_model[src_word][tgt_word] for tgt_word in target_tokens)
                for tgt_word in target_tokens:
                    count[src_word][tgt_word] += translation_model[src_word][tgt_word] / total_prob
                    total[src_word] += translation_model[src_word][tgt_word] / total_prob

        # M-step: Update translation probabilities
        for src_word in source_vocab:
            for tgt_word in target_vocab:
                translation_model[src_word][tgt_word] = count[src_word][tgt_word] / total[src_word]

    return translation_model

translation_model = train_ibm_model1(training_data)

# Function for translation using IBM Model 1
def translate(sentence, translation_model = translation_model):
    sentence = lower_and_split_punct(sentence)
    source_tokens = sentence.split()
    translation = []
    for src_word in source_tokens:
        if src_word in translation_model:
            tgt_word = max(translation_model[src_word], key=translation_model[src_word].get)
            translation.append(tgt_word)
    translated_text = ' '.join(translation)
    return translit_from_latin_to_indic(translated_text)


