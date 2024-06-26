# -*- coding: utf-8 -*-
"""Plagiarism detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13OUb72VJwE-p8-uRfZ2CcnB3BWhQgk-0

## **LSA WITH COSINE SIMILARITY**

**The below code is plagiarism detection implementation without explicit preprocessing function on custom dataset**
"""

from google.colab import drive
drive.mount('/content/drive', force_remount=True)

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import accuracy_score, f1_score
import numpy as np
import string
import warnings
warnings.filterwarnings('ignore')


def calculate_similarity(text1, text2):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    svd = TruncatedSVD(n_components=2)
    if tfidf_matrix.shape == (2, 1):
      return None
    lsa_matrix = svd.fit_transform(tfidf_matrix)
    similarity = cosine_similarity(lsa_matrix[0].reshape(1, -1), lsa_matrix[1].reshape(1, -1))[0][0]
    return similarity

# Load dataset
df = pd.read_csv('/content/drive/MyDrive/plagiarism_dataset.csv')

# similarity threshold
threshold = 0.7

# Below code calculates similarity and predict plagiarism
predictions = []

#print(df.head(2))
ignored_idx = []

for index, row in df.iterrows():
    similarity = calculate_similarity(row['text1'], row['text2'])
    if not similarity:
      df.at[index,'is_plagiarized'] = np.nan
      continue
    is_plagiarized = int(similarity > threshold)
    predictions.append(is_plagiarized)


# model eavluation
predicted = np.array(predictions)
actual = df['is_plagiarized'].dropna()
actual=actual.values

accuracy = accuracy_score(actual, predicted)
f1 = f1_score(actual, predicted)

Text1="The quick brown fox jumps over the lazy dog."
Text2="A swift fox of brown color leaps above a dog that is not active."
similarity = calculate_similarity(Text1, Text2)
is_plagiarized = int(similarity > threshold)
similarity_percentage = similarity * 100
output = 'Plagiarized' if is_plagiarized == 1 else 'Not Plagiarized'
print(f"Similarity for the two input documents is {output} with a similarity score of: {similarity_percentage:.2f}%")
print(f"Accuracy: {accuracy}")
print(f"F1 Score: {f1}")

"""The below code is plagiarism detection implementation with explicit preprocessing function on custom dataset along with additional lemmatization handled by TfidfVectorizer"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import accuracy_score, f1_score
import numpy as np
import string
import warnings
warnings.filterwarnings('ignore')

def preprocess(sentence):
    sentence = sentence.lower()
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))
    return ''.join(sentence)

def calculate_similarity_and_common_words(text1, text2):
    #This function calculates cosine similarity between 2 texts and identifies common high-scoring words.
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores_1 = tfidf_matrix[0].toarray().flatten()
    tfidf_scores_2 = tfidf_matrix[1].toarray().flatten()

    common_words_scores = {feature_names[i]: min(tfidf_scores_1[i], tfidf_scores_2[i])
                           for i in range(len(feature_names))
                           if tfidf_scores_1[i] > 0 and tfidf_scores_2[i] > 0}

    sorted_common_words = sorted(common_words_scores.items(), key=lambda x: x[1], reverse=True)

    return similarity, sorted_common_words




# Load dataset
df = pd.read_csv('/content/drive/MyDrive/plagiarism_dataset.csv')

# Define similarity threshold
threshold = 0.7

# Below code calculates similarity and predict plagiarism
predictions = []

#print(df.head(2))
ignored_idx = []

for index, row in df.iterrows():
    similarity,_ = calculate_similarity_and_common_words(row['text1'], row['text2'])
    if not similarity:
      df.at[index,'is_plagiarized'] = np.nan
      continue
    is_plagiarized = int(similarity > threshold)
    predictions.append(is_plagiarized)


# model evaluation
predicted = np.array(predictions)
actual = df['is_plagiarized'].dropna()
actual=actual.values

accuracy = accuracy_score(actual, predicted)
f1 = f1_score(actual, predicted)

Text1 = "This is a simple test document."
Text2 = "This document is a test, not a real document."
preprocessed_text1 = preprocess(Text1)
preprocessed_text2 = preprocess(Text2)

print(preprocessed_text1)
print(preprocessed_text2)
similarity, common_words = calculate_similarity_and_common_words(preprocessed_text1, preprocessed_text2)
similarity_percentage = similarity * 100
print(f"Similarity: {similarity_percentage:.2f}%")

if common_words:
    print("Common words contributing to similarity:")
    for word, score in common_words:
        print(f"{word}")
else:
    print("No common high-scoring words identified.")

"""The below code is plagiarism detection implementation with explicit preprocessing function on custom dataset along with additional lemmatization handled by TfidfVectorizer and POS Tagging"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import accuracy_score, f1_score
import numpy as np
import string
import warnings
import re
import nltk
from nltk.corpus import stopwords
from nltk import pos_tag
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
warnings.filterwarnings('ignore')

default_similarity_value = 1;

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()


def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return 'a'
    elif treebank_tag.startswith('V'):
        return 'v'
    elif treebank_tag.startswith('N'):
        return 'n'
    elif treebank_tag.startswith('R'):
        return 'r'
    else:
        return 'n'

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove non-alphanumeric characters
    tokens = word_tokenize(text)  # Tokenize text
    tagged_tokens = pos_tag(tokens)  # Get POS tags for tokens
    # Remove stop words and lemmatize
    tokens = [lemmatizer.lemmatize(word, get_wordnet_pos(pos)) for word, pos in tagged_tokens if word not in stop_words]
    return ' '.join(tokens)

def calculate_similarity(text1, text2):
    #This function calculates cosine similarity between 2 texts.
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    svd = TruncatedSVD(n_components=2)
    if tfidf_matrix.shape == (2, 1):
      return None
    lsa_matrix = svd.fit_transform(tfidf_matrix)
    similarity = cosine_similarity(lsa_matrix[0].reshape(1, -1), lsa_matrix[1].reshape(1, -1))[0][0]
    return similarity

# Load dataset
df = pd.read_csv('/content/drive/MyDrive/plagiarism_dataset.csv')

# Define similarity threshold
threshold = 0.7

# Below code calculates similarity and predict plagiarism
predictions = []

#print(df.head(2))
ignored_idx = []

for index, row in df.iterrows():
    similarity = calculate_similarity(row['text1'], row['text2'])
    if similarity is None:
      df.at[index,'is_plagiarized'] = np.nan
      continue
    is_plagiarized = int(similarity > threshold)
    predictions.append(is_plagiarized)

# model evaluation
predicted = np.array(predictions)
actual = df['is_plagiarized'].dropna()
actual=actual.values

accuracy = accuracy_score(actual, predicted)
f1 = f1_score(actual, predicted)

Text1="The paint on the canvas looks vibrant."
Text2="They paint the wall with vibrant colors."
preprocessed_text1 = preprocess_text(Text1)
preprocessed_text2 = preprocess_text(Text2)
print(preprocessed_text1)
print(preprocessed_text2)
similarity = calculate_similarity(preprocessed_text1, preprocessed_text2)
if similarity is None:
  similarity = default_similarity_value
is_plagiarized = int(similarity > threshold)
similarity_percentage = similarity * 100
output = 'Plagiarized' if is_plagiarized == 1 else 'Not Plagiarized'
print(f"Similarity for the two input documents is {output} with a similarity score of: {similarity_percentage:.2f}%")
print(f"Accuracy: {accuracy}")
print(f"F1 Score: {f1}")

"""## **MACHINE LEARNING MODEL**

***SVM and Random Forest Classifier with custom dataset***
"""

import pandas as pd
from gensim.models import Word2Vec
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from nltk.tokenize import word_tokenize
import numpy as np
import nltk

nltk.download('punkt')

df = pd.read_csv('/content/drive/MyDrive/plagiarism_dataset.csv')
df['text1_tokens'] = df['text1'].apply(lambda x: word_tokenize(x.lower()))
df['text2_tokens'] = df['text2'].apply(lambda x: word_tokenize(x.lower()))
all_tokens = pd.concat([df['text1_tokens'], df['text2_tokens']]).tolist()

word2vec_model = Word2Vec(sentences=all_tokens, vector_size=100, window=5, min_count=1, workers=4)

def document_vector(word_list, model):
    word_list = [word for word in word_list if word in model.wv.index_to_key]
    if len(word_list) == 0:
        return np.zeros(model.vector_size)
    else:
        return np.mean(model.wv[word_list], axis=0)

df['text1_vector'] = df['text1_tokens'].apply(lambda x: document_vector(x, word2vec_model))
df['text2_vector'] = df['text2_tokens'].apply(lambda x: document_vector(x, word2vec_model))
X = np.array(df.apply(lambda row: row['text1_vector'] - row['text2_vector'], axis=1).tolist())
y = df['is_plagiarized'].values

# Spliting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)

# Training SVM classifier
svm_clf = SVC(kernel='linear')
svm_clf.fit(X_train, y_train)

# Training Random Forest classifier
rf_clf = RandomForestClassifier(n_estimators=100, random_state=42)
rf_clf.fit(X_train, y_train)

svm_predictions = svm_clf.predict(X_test)
rf_predictions = rf_clf.predict(X_test)
print("SVM Classifier Report")
print(classification_report(y_test, svm_predictions))

print("Random Forest Classifier Report")
print(classification_report(y_test, rf_predictions))

def preprocess_and_tokenize(text):
    return word_tokenize(text.lower())

def create_feature_vector(text1, text2, model):
    text1_vector = document_vector(preprocess_and_tokenize(text1), model)
    text2_vector = document_vector(preprocess_and_tokenize(text2), model)
    return text1_vector - text2_vector

new_text1 = "hi"
new_text2 = "A swift fox of brown color leaps above a dog that is not active."
new_feature_vector = create_feature_vector(new_text1, new_text2, word2vec_model).reshape(1, -1)

# Prediction with SVM
svm_prediction = svm_clf.predict(new_feature_vector)
print(f"SVM Prediction for plagiarism: {'Plagiarized' if svm_prediction[0] == 1 else 'Not Plagiarized'}")

# Prediction with Random Forest
rf_prediction = rf_clf.predict(new_feature_vector)
print(f"Random Forest Prediction for plagiarism: {'Plagiarized' if rf_prediction[0] == 1 else 'Not Plagiarized'}")

"""## **BERT**"""

!pip install torch transformers

import pandas as pd
from transformers import BertTokenizer
from sklearn.model_selection import train_test_split
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
import torch

# Load the dataset
df = pd.read_csv('/content/drive/MyDrive/plagiarism_dataset.csv')  # Update the path to your dataset

# Initializing the BERT tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

def tokenize_for_bert(text1, text2):
    return tokenizer(text1, text2, padding='max_length', max_length=512, truncation=True, return_tensors="pt")

df['bert_tokens'] = df.apply(lambda row: tokenize_for_bert(row['text1'], row['text2']), axis=1)

# Extract input_ids, attention_masks, and token_type_ids
input_ids = torch.cat([x['input_ids'] for x in df['bert_tokens']], dim=0)
attention_masks = torch.cat([x['attention_mask'] for x in df['bert_tokens']], dim=0)
token_type_ids = torch.cat([x['token_type_ids'] for x in df['bert_tokens']], dim=0)
labels = torch.tensor(df['is_plagiarized'].values)

train_inputs, validation_inputs, train_labels, validation_labels = train_test_split(
    input_ids, labels, random_state=2018, test_size=0.7, stratify=labels)

train_masks, validation_masks, _, _ = train_test_split(
    attention_masks, labels, random_state=2018, test_size=0.7, stratify=labels)

train_token_types, validation_token_types, _, _ = train_test_split(
    token_type_ids, labels, random_state=2018, test_size=0.7, stratify=labels)

batch_size = 16

train_data = TensorDataset(train_inputs, train_masks, train_token_types, train_labels)
train_sampler = RandomSampler(train_data)
train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=batch_size, pin_memory=True)

validation_data = TensorDataset(validation_inputs, validation_masks, validation_token_types, validation_labels)
validation_sampler = SequentialSampler(validation_data)
validation_dataloader = DataLoader(validation_data, sampler=validation_sampler, batch_size=batch_size, pin_memory=True)

from transformers import BertForSequenceClassification, AdamW

model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels = 2, # Binary classification (plagiarized or not)
    output_attentions = False,
    output_hidden_states = False,
)

optimizer = AdamW(model.parameters(), lr=2e-5, eps=1e-8)

# Check if CUDA is available, otherwise use CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f'Using device: {device}')
model.to(device)

from transformers import get_linear_schedule_with_warmup
import numpy as np
from sklearn.metrics import accuracy_score

epochs = 2
total_steps = len(train_dataloader) * epochs

scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

for epoch_i in range(0, epochs):
    print('======== Epoch {:} / {:} ========'.format(epoch_i + 1, epochs))
    model.train()
    total_loss = 0

    for step, batch in enumerate(train_dataloader):
        b_input_ids = batch[0].to(device)
        b_input_mask = batch[1].to(device)
        b_labels = batch[3].to(device)
        b_token_type_ids = batch[2].to(device)

        model.zero_grad()
        outputs = model(b_input_ids, token_type_ids=b_token_type_ids, attention_mask=b_input_mask, labels=b_labels)
        loss = outputs.loss
        total_loss += loss.item()
        loss.backward()
        optimizer.step()
        scheduler.step()

    avg_train_loss = total_loss / len(train_dataloader)
    print("  Average training loss: {0:.2f}".format(avg_train_loss))

    # Validation
    model.eval()
    predictions , true_labels = [], []
    for batch in validation_dataloader:
        batch = tuple(t.to(device) for t in batch)
        b_input_ids, b_input_mask, b_token_type_ids, b_labels = batch
        with torch.no_grad():
            outputs = model(b_input_ids, token_type_ids=b_token_type_ids, attention_mask=b_input_mask)

        logits = outputs.logits
        logits = logits.detach().cpu().numpy()
        label_ids = b_labels.to('cpu').numpy()

        predictions.append(logits)
        true_labels.append(label_ids)

    # Calculating the accuracy for current batch of test sentences.
    flat_predictions = np.concatenate(predictions, axis=0)
    flat_predictions = np.argmax(flat_predictions, axis=1).flatten()
    flat_true_labels = np.concatenate(true_labels, axis=0)
    val_accuracy = accuracy_score(flat_true_labels, flat_predictions)

    print("  Validation Accuracy: {0:.2f}".format(val_accuracy))

"""Evaluate the BERT Model with new inputs"""

sentence1 = "This is the first sentence."
sentence2 = "This is the second sentence."

encoded_pair = tokenizer(sentence1, sentence2, padding='max_length', truncation=True, max_length=512, return_tensors="pt")

input_ids = encoded_pair['input_ids']
attention_mask = encoded_pair['attention_mask']
token_type_ids = encoded_pair['token_type_ids']

from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np
predictions, true_labels = [], []

model.eval()
for batch in validation_dataloader:
    batch = tuple(t.to(device) for t in batch)
    b_input_ids, b_attention_mask, b_token_type_ids, b_labels = batch

    with torch.no_grad():
        outputs = model(b_input_ids, token_type_ids=b_token_type_ids, attention_mask=b_attention_mask)

    logits = outputs.logits
    logits = logits.detach().cpu().numpy()
    label_ids = b_labels.to('cpu').numpy()

    batch_predictions = np.argmax(logits, axis=1)
    predictions.extend(batch_predictions)
    true_labels.extend(label_ids)


logits = outputs.logits

probabilities = torch.softmax(logits, dim=1).cpu().numpy()
plagiarism_probability = probabilities[0][1]

is_plagiarized = "Plagiarized" if plagiarism_probability > 0.3 else "Not Plagiarized"
print(f"Plagiarism Probability: {plagiarism_probability:.4f}")
print(f"Result: {is_plagiarized}")

accuracy = accuracy_score(true_labels, predictions)
precision, recall, f1, _ = precision_recall_fscore_support(true_labels, predictions, average='binary')

print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")

"""**SVM and Random Forest Classifier with PAN-PC-11 dataset(still in progress)**"""

from google.colab import drive
import os
import xml.etree.ElementTree as ET
import nltk
from nltk.tokenize import word_tokenize
from gensim.models import Word2Vec
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

nltk.download('punkt')

def read_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def parse_xml_for_plagiarism(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    plagiarism_cases = []
    for feature in root.iter('feature'):
        if feature.attrib.get('type') == 'plagiarism':
            plagiarism_cases.append({
                'source_offset': int(feature.attrib['source_offset']),
                'source_length': int(feature.attrib['source_length']),
                'suspicious_offset': int(feature.attrib['this_offset']),
                'suspicious_length': int(feature.attrib['this_length']),
                'source_reference': feature.attrib['source_reference']
            })
    return plagiarism_cases

# NOTE : base path below is path to the dataset, update below path with actual path
base_path = 'https://drive.google.com/drive/folders/1gwU9kIeii-VLU7SO8pi-ZKG12kXZKhk2?usp=sharing'

suspicious_path = os.path.join(base_path, 'suspicious-document')
source_path = os.path.join(base_path, 'source-document')
text_pairs = []
for root, dirs, files in os.walk(suspicious_path):
    for file in files:
        if file.endswith('.txt'):
            suspicious_file_path = os.path.join(root, file)
            suspicious_text = read_text(suspicious_file_path)
            xml_file_path = suspicious_file_path.replace('.txt', '.xml')
            plagiarism_cases = parse_xml_for_plagiarism(xml_file_path)

            for case in plagiarism_cases:
                start_pos = case['suspicious_offset']
                end_pos = start_pos + case['suspicious_length']
                suspicious_excerpt = suspicious_text[start_pos:end_pos]
                source_file_path = os.path.join(source_path, case['source_reference'] + '.txt')
                source_text = read_text(source_file_path)
                source_start_pos = case['source_offset']
                source_end_pos = source_start_pos + case['source_length']
                source_excerpt = source_text[source_start_pos:source_end_pos]
                suspicious_tokens = word_tokenize(suspicious_excerpt)
                source_tokens = word_tokenize(source_excerpt)
                text_pairs.append((source_tokens, suspicious_tokens))

flat_tokenized_texts = [token for pair in text_pairs for text in pair for token in text]

# Training Word2Vec model on the corpus
word2vec_model = Word2Vec(sentences=flat_tokenized_texts, vector_size=100, window=5, min_count=1, workers=4)

def feature_vector(text_pair, model):
    source_vector = np.mean([model.wv[token] for token in text_pair[0] if token in model.wv], axis=0)
    suspicious_vector = np.mean([model.wv[token] for token in text_pair[1] if token in model.wv], axis=0)
    return np.abs(source_vector - suspicious_vector)

feature_vectors = np.array([feature_vector(pair, word2vec_model) for pair in text_pairs])

# labels for the dataset: 1 for plagiarism, 0 for non-plagiarism
labels = [1 if pair else 0 for pair in text_pairs]

# Spliting the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(feature_vectors, labels, test_size=0.2, random_state=42)

# Training Random Forest classifier
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
rf_classifier.fit(X_train, y_train)

# Training SVM classifier
svm_classifier = SVC(kernel='linear')
svm_classifier.fit(X_train, y_train)
rf_predictions = rf_classifier.predict(X_test)
svm_predictions = svm_classifier.predict(X_test)

print("Random Forest Classification Report:")
print(classification_report(y_test, rf_predictions))

print("SVM Classification Report:")
print(classification_report(y_test, svm_predictions))