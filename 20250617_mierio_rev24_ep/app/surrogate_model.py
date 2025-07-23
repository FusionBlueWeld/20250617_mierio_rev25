import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import joblib
from functools import lru_cache
import os

def _create_model(input_dim, output_dim):
    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=(input_dim,)),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(output_dim)
    ])
    return model

def train_and_save_model(df, feature_vars, target_vars, model_path, scaler_path, base_model_path=None, epochs=50, batch_size=32):
    X = df[feature_vars]
    y = df[target_vars]

    if base_model_path and os.path.exists(base_model_path):
        print(f"Loading base model from {base_model_path} for fine-tuning...")

        model, scaler = load_model_and_scaler(base_model_path, scaler_path)
        if model is None or scaler is None:
            raise ValueError(f"Failed to load base model or scaler from the provided paths.")
        
        X_scaled = scaler.transform(X)

        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001), loss='mean_squared_error')
        print("Continuing training on new data (fine-tuning)...")

    else:
        print("Creating and training a new model...")
        
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)

        joblib.dump(scaler, scaler_path)

        input_dim = len(feature_vars)
        output_dim = len(target_vars)
        model = _create_model(input_dim, output_dim)
        
        model.compile(optimizer='adam', loss='mean_squared_error')
    
    model.summary()
    
    model.fit(
        X_scaled,
        y,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.2,
        verbose=1
    )

    model.save(model_path)
    print(f"Model saved to {model_path}")


@lru_cache(maxsize=32)
def load_model_and_scaler(model_path, scaler_path):

    try:
        print(f"Loading model from: {model_path}")
        model = tf.keras.models.load_model(model_path)
        print(f"Loading scaler from: {scaler_path}")
        scaler = joblib.load(scaler_path)
        return model, scaler
    except Exception as e:
        print(f"Error loading model or scaler: {e}")
        return None, None

def predict_with_loaded_model(model, scaler, input_df):

    input_scaled = scaler.transform(input_df)
    predictions = model.predict(input_scaled)
    return predictions
