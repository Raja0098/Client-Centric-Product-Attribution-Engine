import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# --- Configuration: Define file paths ---
DATA_DIR = "data"
MODELS_DIR = "models"
GROUND_TRUTH_FILE = os.path.join(DATA_DIR, "ground_truth_v2 - Sheet1.csv")
NEW_PRODUCTS_FILE = os.path.join(DATA_DIR, "new_data.csv")

# Ensure the models directory exists
os.makedirs(MODELS_DIR, exist_ok=True)


def load_and_clean_data(filepath):
    """Loads and performs initial cleaning on the dataset."""
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: The file {filepath} was not found.")
        return None

    df['actual_price'] = df['actual_price'].astype(str).str.replace(r'[₹,]', '', regex=True)
    df['actual_price'] = pd.to_numeric(df['actual_price'], errors='coerce')
    df.dropna(subset=['actual_price'], inplace=True)
    df['combined_text'] = df['product_name'].fillna('') + " " + df['about_product'].fillna('')
    return df


def train_and_save_models(data_filepath):
    """
    Trains and saves all models for Client A (L1, L2, L3) and Client B.
    """
    print("--- Starting Model Training ---")
    df = load_and_clean_data(data_filepath)
    if df is None: return

    # --- Prepare Client A Data ---
    split_cols = df['Client A Catgories'].str.split(' > ', expand=True)
    df['clienta_level_1'] = split_cols[0]
    df['clienta_level_2'] = split_cols[1]
    df['clienta_level_3'] = split_cols[2]
    df.fillna('None', inplace=True)

    # --- Train Client A: Level 1 Model ---
    print("\nTraining Client A: Level 1 Model...")
    model_df_l1 = df[df['clienta_level_1'] != 'None'].copy()
    
    category_counts_l1 = model_df_l1['clienta_level_1'].value_counts()
    
    categories_to_keep_l1 = category_counts_l1[category_counts_l1 >= 2].index
    
    model_df_l1 = model_df_l1[model_df_l1['clienta_level_1'].isin(categories_to_keep_l1)]
    
    X_l1 = model_df_l1[['combined_text', 'actual_price']]
    
    y_l1 = model_df_l1['clienta_level_1']
    
    preprocessor_l1 = ColumnTransformer(transformers=[('text', TfidfVectorizer(stop_words='english'), 'combined_text'), ('numeric', StandardScaler(), ['actual_price'])])
    
    pipeline_l1 = Pipeline([('preprocessor', preprocessor_l1), ('clf', RandomForestClassifier(random_state=42, class_weight='balanced'))])
    
    pipeline_l1.fit(X_l1, y_l1)
    
    joblib.dump(pipeline_l1, os.path.join(MODELS_DIR, "pipeline_l1.joblib"))
    
    print("Level 1 model trained and saved.")

    # --- Train Client A: Level 2 Model ---
    
    print("\nTraining Client A: Level 2 Model --------")
    
    model_df_l2 = df[df['clienta_level_2'] != 'None'].copy()
    
    model_df_l2['predicted_level_1'] = pipeline_l1.predict(model_df_l2[['combined_text', 'actual_price']])
    
    category_counts_l2 = model_df_l2['clienta_level_2'].value_counts()
    
    categories_to_keep_l2 = category_counts_l2[category_counts_l2 >= 2].index
    
    model_df_l2 = model_df_l2[model_df_l2['clienta_level_2'].isin(categories_to_keep_l2)]
    
    X_l2 = model_df_l2[['combined_text', 'actual_price', 'predicted_level_1']]
    
    y_l2 = model_df_l2['clienta_level_2']
    
    preprocessor_l2 = ColumnTransformer(transformers=[('text', TfidfVectorizer(stop_words='english'), 'combined_text'), ('numeric', StandardScaler(), ['actual_price']), ('categorical', OneHotEncoder(handle_unknown='ignore'), ['predicted_level_1'])])
    
    pipeline_l2 = Pipeline([('preprocessor', preprocessor_l2), ('clf', RandomForestClassifier(random_state=42, class_weight='balanced'))])
    
    pipeline_l2.fit(X_l2, y_l2)
    
    joblib.dump(pipeline_l2, os.path.join(MODELS_DIR, "pipeline_l2.joblib"))
    
    print("Level 2 model trained and saved.")

    # --- Train Client A: Level 3 Model ---
    print("\nTraining Client A: Level 3 Model...")

    model_df_l3 = df[df['clienta_level_3'] != 'None'].copy()
    
    if not model_df_l3.empty:
        model_df_l3['predicted_level_1'] = pipeline_l1.predict(model_df_l3[['combined_text', 'actual_price']])
        model_df_l3['predicted_level_2'] = pipeline_l2.predict(model_df_l3[['combined_text', 'actual_price', 'predicted_level_1']])
        category_counts_l3 = model_df_l3['clienta_level_3'].value_counts()
        categories_to_keep_l3 = category_counts_l3[category_counts_l3 >= 2].index
        model_df_l3 = model_df_l3[model_df_l3['clienta_level_3'].isin(categories_to_keep_l3)]
        if model_df_l3.shape[0] > 1:
            X_l3 = model_df_l3[['combined_text', 'actual_price', 'predicted_level_1', 'predicted_level_2']]
            y_l3 = model_df_l3['clienta_level_3']
            preprocessor_l3 = ColumnTransformer(transformers=[('text', TfidfVectorizer(stop_words='english'), 'combined_text'), ('numeric', StandardScaler(), ['actual_price']), ('categorical', OneHotEncoder(handle_unknown='ignore'), ['predicted_level_1', 'predicted_level_2'])])
            pipeline_l3 = Pipeline([('preprocessor', preprocessor_l3), ('clf', RandomForestClassifier(random_state=42, class_weight='balanced'))])
            pipeline_l3.fit(X_l3, y_l3)
            joblib.dump(pipeline_l3, os.path.join(MODELS_DIR, "pipeline_l3.joblib"))
            print("Level 3 model trained and saved.")
        else: print("Skipping Level 3 model: Not enough data after filtering.")
    else: print("Skipping Level 3 model: No data to process.")

    # ==============================================================================
    # == NEW: Train Models for Client B
    # ==============================================================================

    print("\nTraining Client B: Department Model...")
    model_df_b_dept = df[df['Client B department'] != 'None'].copy()
    category_counts_b_dept = model_df_b_dept['Client B department'].value_counts()
    categories_to_keep_b_dept = category_counts_b_dept[category_counts_b_dept >= 2].index
    model_df_b_dept = model_df_b_dept[model_df_b_dept['Client B department'].isin(categories_to_keep_b_dept)]
    
    X_b_dept = model_df_b_dept[['combined_text', 'actual_price']]
    y_b_dept = model_df_b_dept['Client B department']

    pipeline_b_dept = Pipeline([('preprocessor', preprocessor_l1), ('clf', RandomForestClassifier(random_state=42, class_weight='balanced'))])
    pipeline_b_dept.fit(X_b_dept, y_b_dept)
    joblib.dump(pipeline_b_dept, os.path.join(MODELS_DIR, "pipeline_clientb_dept.joblib"))
    print("Client B Department model trained and saved.")

    # --- Train Client B: Price Tier Model ---
    print("\nTraining Client B: Price Tier Model...")
    model_df_b_price = df[df['Client b Price Tier'] != 'None'].copy()
    X_b_price = model_df_b_price[['combined_text', 'actual_price']]
    y_b_price = model_df_b_price['Client b Price Tier']

    pipeline_b_price = Pipeline([('preprocessor', preprocessor_l1), ('clf', RandomForestClassifier(random_state=42, class_weight='balanced'))])
    pipeline_b_price.fit(X_b_price, y_b_price)
    joblib.dump(pipeline_b_price, os.path.join(MODELS_DIR, "pipeline_clientb_price.joblib"))
    print("Client B Price Tier model trained and saved.")

    print("\n--- Model Training Complete ---")


def predict_categories(data_filepath):
    """
    Loads new, untagged data and predicts all categories for Client A and B.
    """
    print("\n--- Starting Prediction on New Data ---")
    new_df = load_and_clean_data(data_filepath)
    if new_df is None: return None

    # Load all trained models
    try:
        pipeline_l1 = joblib.load(os.path.join(MODELS_DIR, "pipeline_l1.joblib"))
        pipeline_l2 = joblib.load(os.path.join(MODELS_DIR, "pipeline_l2.joblib"))
        pipeline_l3 = joblib.load(os.path.join(MODELS_DIR, "pipeline_l3.joblib"))
        pipeline_b_dept = joblib.load(os.path.join(MODELS_DIR, "pipeline_clientb_dept.joblib"))
        pipeline_b_price = joblib.load(os.path.join(MODELS_DIR, "pipeline_clientb_price.joblib"))
        print("All models loaded successfully.")
    except FileNotFoundError:
        print("Error: Model files not found. Please run the training function first.")
        return None

    # --- Client A Hierarchical Prediction ---
    new_df['predicted_level_1'] = pipeline_l1.predict(new_df[['combined_text', 'actual_price']])
    new_df['predicted_level_2'] = pipeline_l2.predict(new_df[['combined_text', 'actual_price', 'predicted_level_1']])
    new_df['predicted_level_3'] = pipeline_l3.predict(new_df[['combined_text', 'actual_price', 'predicted_level_1', 'predicted_level_2']])
    new_df['predicted_clienta_category'] = new_df['predicted_level_1'] + ' > ' + new_df['predicted_level_2'] + ' > ' + new_df['predicted_level_3']

    # --- NEW: Client B Prediction ---
    new_df['predicted_clientb_department'] = pipeline_b_dept.predict(new_df[['combined_text', 'actual_price']])
    new_df['predicted_clientb_price_tier'] = pipeline_b_price.predict(new_df[['combined_text', 'actual_price']])
    
    print("--- Prediction Complete ---")
    
    # Return a clean dataframe with final predictions
    output_cols = [
        'product_name', 
        'actual_price', 
        'predicted_clienta_category', 
        'predicted_clientb_department', 
        'predicted_clientb_price_tier'
    ]
    return new_df[output_cols]


if __name__ == "__main__":
    # Step 1: Train all models.
    
    # train_and_save_models(GROUND_TRUTH_FILE)

    ml_input_file = os.path.join(DATA_DIR, "new_data.csv")

    # Step 3: Run the prediction pipeline on the new data
    predicted_df = predict_categories(ml_input_file)

    if predicted_df is not None:
        # Step 4: Save the results to a new CSV
        output_file = os.path.join(DATA_DIR, "predicted.csv")
        predicted_df.to_csv(output_file, index=False)
        print(f"\n--- Predictions saved to {output_file} ---")
        print(predicted_df.head().to_markdown(index=False))