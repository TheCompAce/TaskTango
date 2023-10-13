import os
import sqlite3
from gensim.models import Word2Vec
import numpy as np
import re
import logging
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk

# Set up logging
logging.basicConfig(level=logging.INFO, filename='vector_db.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')


class VectorDatabase:
    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.db_path = os.path.join(path, f'{name}.db')
        self.model_path = os.path.join(path, f'{name}.bin')
        
        # Ensure the path exists
        if not os.path.exists(path):
            os.makedirs(path)
        
        # Set up database and model connections
        self.conn = self.initialize_db()
        self.model = self.initialize_model()
    
    def initialize_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            with self.conn.cursor() as c:
            
                c.execute('CREATE TABLE IF NOT EXISTS responses (id INTEGER PRIMARY KEY, response TEXT, trained BOOLEAN DEFAULT 0)')
                c.execute('CREATE INDEX IF NOT EXISTS idx_responses_trained ON responses (trained)')  # Index on trained field
                c.execute('CREATE TABLE IF NOT EXISTS vector_data (id INTEGER PRIMARY KEY, vector BLOB, response_id INTEGER, FOREIGN KEY(response_id) REFERENCES responses(id))')
                c.execute('CREATE INDEX IF NOT EXISTS idx_vector_data_response_id ON vector_data (response_id)')  # Index on response_id field

                c.execute('ALTER TABLE responses ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP')  
                
                conn.commit()
            return conn  # Return the connection
        except Exception as e:
            logging.exception(f"An error occurred in initialize_db: {e}")

    
    def initialize_model(self):
        try:
            # Create a new Word2Vec model if it doesn't exist
            if not os.path.exists(self.model_path):
                # Assuming sentences is your data
                # Replace the following line with your data and model parameters
                sentences = [["hello", "world"], ["how", "are", "you"], ["goodbye", "world"]]

                model = Word2Vec(sentences, min_count=1)
                model.save(self.model_path)
            else:
                model = Word2Vec.load(self.model_path)

            return model  # Return the model
        except Exception as e:
            logging.exception(f"An error occurred in initialize_model: {e}")

    def ensure_connection(self):
        if self.conn is None:
            self.conn = self.initialize_db()
        if self.model is None:
            self.model = self.initialize_model()
    
    def create_response(self, response_text):
        # Insert a new response and its vector representation into the database
        try:
            with self.conn.cursor() as c:
                preprocess_text = self.preprocess_text(response_text)
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get the current date and time
                c.execute('INSERT INTO responses (response, timestamp) VALUES (?, ?)', (preprocess_text, now))
                
                response_id = c.lastrowid
                
                vector = self.model.wv[preprocess_text.split()]  # Assume response_text is a single sentence
                vector_bytes = vector.tobytes()
                
                c.execute('INSERT INTO vector_data (vector, response_id) VALUES (?, ?)', (vector_bytes, response_id))
                
                self.conn.commit()
        except Exception as e:
            logging.exception(f"An error occurred in create_response: {e}")

    
    def search_response(self, search_text):
        with self.conn.cursor() as c:
        
            # Use the LIKE operator to search for the search_text in the response field
            c.execute("SELECT id, response FROM responses WHERE response LIKE ?", ('%' + search_text + '%',))
            search_results = c.fetchall()
            
            return search_results
    
    def normalize_text(self, text):
        # Convert to lowercase
        text = text.lower()
        # Remove special characters and digits using regex
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text).strip()
        # Tokenize the text
        tokens = text.split()
        # Remove stopwords
        tokens = [word for word in tokens if word not in stopwords.words('english')]
        # Perform stemming
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(word) for word in tokens]
        # Join tokens back into a single string
        text = ' '.join(tokens)
        return text

    def close_connection(self):
        """Close the database connection gracefully."""
        try:
            if self.conn:
                self.conn.close()

                self.conn = None
        except Exception as e:
            logging.exception(f"An error occurred while closing the connection: {e}")


    def preprocess_text(self, text):
        """Example preprocessing function (can be expanded)."""
        # Placeholder for any preprocessing steps you want to implement
        return self.normalize_text(text)

    def get_vector(self, response_id):
        """Retrieve vector data for a given response_id."""
        with self.conn.cursor() as c:
        
            c.execute('SELECT vector FROM vector_data WHERE response_id = ?', (response_id,))
            vector_data = c.fetchone()
            
            if vector_data is None:
                error_message = f"No vector data found for response_id {response_id}"
                logging.error(error_message)
                raise ValueError(error_message)
            
            vector = np.frombuffer(vector_data[0], dtype=np.float32)  # Assuming the vector data is stored as float32
            
            return vector   
    
    def read_response(self, response_id):
        with self.conn.cursor() as c:
        
            c.execute('SELECT response FROM responses WHERE id = ?', (response_id,))
            response = c.fetchone()
                    
            if response is None:
                error_message = f"No response found for response_id {response_id}"
                logging.error(error_message)
                raise ValueError(error_message)
            
            return response[0]
    
    def update_response(self, response_id, new_response_text):
        try:
            with self.conn.cursor() as c:
            
                normalized_text = self.normalize_text(new_response_text)
                c.execute('UPDATE responses SET response = ? WHERE id = ?', (normalized_text, response_id))
                
                vector = self.model.wv[normalized_text.split()]
                vector_bytes = vector.tobytes()
                
                c.execute('UPDATE vector_data SET vector = ? WHERE response_id = ?', (vector_bytes, response_id))
                
                self.conn.commit()
        except Exception as e:
            logging.exception(f"An error occurred in update_response: {e}")
    
    def delete_response(self, response_id):
        try:
            with self.conn.cursor() as c:
            
                c.execute('DELETE FROM vector_data WHERE response_id = ?', (response_id,))
                c.execute('DELETE FROM responses WHERE id = ?', (response_id,))
                
                self.conn.commit()
        except Exception as e:
            logging.exception(f"An error occurred in delete_response: {e}")

    def train_untrained_responses(self):
        with self.conn.cursor() as c:
        
            c.execute("SELECT response FROM responses WHERE trained = 0")
            untrained_responses = c.fetchall()
            sentences = [response[0].split() for response in untrained_responses]  # Assuming one sentence per response
            
            self.model.build_vocab(sentences, update=True)  # Update the vocabulary with new words from untrained responses
            self.model.train(sentences, total_examples=len(sentences), epochs=self.model.epochs)  # Train the model with the new data
            
            self.model.save(self.model_path)  # Save the updated model
            
            c.execute("UPDATE responses SET trained = 1 WHERE trained = 0")  # Mark untrained responses as trained
            
            self.conn.commit()
    
    def reset_training_status(self):
        """Reset the trained status of all responses to untrained."""
        try:
            with self.conn.cursor() as c:
            
                c.execute("UPDATE responses SET trained = 0")
                
                self.conn.commit()
        except Exception as e:
            logging.exception(f"An error occurred in reset_training_status: {e}")


    def search_word_vector(self, word):
        """Search for words in the vector space similar to the given word."""
        try:
            similar_words = self.model.wv.similar_by_word(word)
            return similar_words
        except KeyError as e:
            logging.error(f"The word {word} is not in the model's vocabulary.")
            return []  # or raise a custom exception, or log an error and return None

    def get_vector_average(self, text):
        words = text.split()
        vectors = [self.model.wv[word] for word in words if word in self.model.wv.vocab]
        if vectors:
            vector_avg = np.mean(vectors, axis=0)
            return vector_avg
        else:
            return np.zeros(self.model.vector_size)

    def search_similar_conversations(self, text, top_n=5):
        processed_text = self.preprocess_text(text)
        query_vector = self.get_vector_average(processed_text)
        with self.conn:
            c = self.conn.cursor()
            c.execute('SELECT id, vector FROM vector_data')
            vector_data = c.fetchall()

        if not vector_data:
            return []

        ids, vectors = zip(*vector_data)
        vectors = np.array([np.frombuffer(vector, dtype=np.float32) for vector in vectors])
        similarities = cosine_similarity([query_vector], vectors)[0]
        sorted_indices = np.argsort(similarities)[::-1]
        top_indices = sorted_indices[:top_n]
        top_ids = [ids[i] for i in top_indices]
        top_similarities = [similarities[i] for i in top_indices]

        result = []
        for response_id, similarity in zip(top_ids, top_similarities):
            response_text = self.read_response(response_id)
            result.append((response_id, response_text, similarity))

        return result