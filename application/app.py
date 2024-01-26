from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

app = Flask(__name__)

# Charger vos données
imdb_comments = pd.read_csv('imdb_comments.csv')

# Créez un objet TfidfVectorizer en dehors de la fonction
tfidf_vectorizer = TfidfVectorizer()

# Créez un objet Pipeline en dehors de la fonction
pipeline = Pipeline([
    ('model', SVC(kernel='rbf', C=10.0, random_state=42))  # SVC
])

# Définir une fonction pour équilibrer les données et entraîner un modèle
def train_and_evaluate_model(data, target_col, over_sampling_rate, under_sampling_rate):
    # Divisez l'ensemble de données en caractéristiques (X) et étiquettes (y)
    X = data['Commentaire']
    y = data[target_col]

    # Divisez l'ensemble de données équilibré en un ensemble d'entraînement (70%) et un ensemble de test (30%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Ajustez le vectoriseur sur les données d'entraînement et transformez-les
    X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
    X_test_tfidf = tfidf_vectorizer.transform(X_test)

    # Définissez les taux de suréchantillonnage et de sous-échantillonnage
    sampling_strategy_over = {
        'positif': int(len(y_train[y_train == 'positif'])),
        'négatif': int(over_sampling_rate * len(y_train[y_train == 'négatif'])),
        'neutre': int(over_sampling_rate * len(y_train[y_train == 'neutre']))
    }

    # Créez un objet RandomOverSampler
    over_sampler = RandomOverSampler(sampling_strategy=sampling_strategy_over, random_state=42)

    # Appliquez le suréchantillonnage
    X_over, y_over = over_sampler.fit_resample(X_train_tfidf, y_train)

    sampling_strategy_under = {
        'positif': int(under_sampling_rate * len(y_over[y_over == 'positif'])),
        'négatif': int(len(y_over[y_over == 'négatif'])),
        'neutre': int(len(y_over[y_over == 'neutre']))
    }

    # Créez un objet RandomUnderSampler
    under_sampler = RandomUnderSampler(sampling_strategy=sampling_strategy_under, random_state=42)

    # Appliquez le sous-échantillonnage
    X_balanced, y_balanced = under_sampler.fit_resample(X_over, y_over)

    # Entraînez le modèle sur l'ensemble d'entraînement prétraité
    pipeline.fit(X_balanced, y_balanced)

    return pipeline

# Expérimentez avec différents taux de suréchantillonnage et de sous-échantillonnage
over_sampling_rate = 2.5
under_sampling_rate = 0.5
trained_model = train_and_evaluate_model(imdb_comments, 'sentiment', over_sampling_rate, under_sampling_rate)

# Route principale pour afficher le formulaire
@app.route('/')
def home():
    return render_template('index.html')

# Route pour la prédiction
@app.route('/predict', methods=['POST'])
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Obtenir le commentaire à partir du formulaire
        comment = request.form['comment']

        # Vectoriser le commentaire
        comment_tfidf = tfidf_vectorizer.transform([comment])

        # Prédire le sentiment
        predicted_sentiment = trained_model.predict(comment_tfidf)[0]

        return predicted_sentiment

if __name__ == '__main__':
    app.run(debug=True)
