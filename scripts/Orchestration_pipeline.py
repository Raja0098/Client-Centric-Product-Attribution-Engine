# Product Attribution Pipeline - PySpark Orchestrator
# =================================================================
# This script is designed to be run as a PySpark job on Dataproc.
# It orchestrates the entire attribution process:
# 1. Loads all products from BigQuery.
# 2. Applies a rule-based engine.
# 3. For products not covered by rules, it calls deployed Vertex AI models for predictions.
# 4. Combines the results and writes the final, clean data back to BigQuery.

import pandas as pd
import joblib
from google.cloud import storage, aiplatform

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lower, lit, udf
from pyspark.sql.types import StringType

# Here remove my project I Have and other detail
GCP_PROJECT_ID = "your-project-id"
GCS_BUCKET_NAME = "your-gcs-bucket-name"
BIGQUERY_SOURCE_TABLE = "your-project-id.product_data_raw.raw_products"
BIGQUERY_FINAL_TABLE = "your-project-id.product_data_raw.final_product_attributions"
DATAPROC_TEMP_BUCKET = GCS_BUCKET_NAME 
VERTEX_ENDPOINT_ID = "your-vertex-ai-endpoint-id"
VERTEX_LOCATION = "us-central1"
DEPLOYED_MODEL_ID_A = "your_deployed_model_id_for_client_a"
DEPLOYED_MODEL_ID_B = "your_deployed_model_id_for_client_b"


# =================================================================
# Helper Functions to interact with GCP
# =================================================================

def load_gcs_artifact(bucket_name, gcs_path):
    """Downloads a model artifact from GCS to the local Dataproc node."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(gcs_path)
    local_path = f"/tmp/{gcs_path.split('/')[-1]}"
    blob.download_to_filename(local_path)
    return joblib.load(local_path)

# =================================================================
# Main Spark Job
# =================================================================

def main():
    # 1. Initialize Spark Session
    spark = SparkSession.builder.appName("ProductAttributionPipeline").getOrCreate()
    spark.conf.set('temporaryGcsBucket', DATAPROC_TEMP_BUCKET)

    # 2. Load Data from BigQuery
    print("Loading data from BigQuery...")
    df = spark.read.format('bigquery').option('table', BIGQUERY_SOURCE_TABLE).load()
    df = df.filter(col("product_name").isNotNull())

    # 3. Apply the Rule-Based Engine
    print("Applying rule-based engine...")
    df_rules = df.withColumn(
        "client_a_category_rule",
        when(lower(col("product_name")).like("%smart%") & lower(col("product_name")).like("%watch%"), "Mobile > Wearables > Smartwatches")
        .when(lower(col("product_name")).like("%cable%") & lower(col("product_name")).like("%braided%"), "Computing > Accessories > Premium Cables")
        .when(lower(col("product_name")).like("%bluetooth%") & (lower(col("product_name")).like("%headphone%") | lower(col("product_name")).like("%earbud%")), "Audio > Headphones > Wireless")
        .otherwise(None)
    ).withColumn(
        "client_b_category_rule",
        when(lower(col("product_name")).like("%watch%"), "Apparel > Accessories > Watches")
        .when(lower(col("product_name")).like("%cable%") | lower(col("product_name")).like("%charger%") | lower(col("product_name")).like("%adapter%"), "Electronics > Accessories > Cables & Chargers")
        .when(lower(col("product_name")).like("%heater%") | lower(col("product_name")).like("%electric%"), "Home > Small Appliances")
        .otherwise(None)
    )

    # 4. Isolate Products for ML Prediction
    df_for_ml = df_rules.filter(col("client_a_category_rule").isNull() | col("client_b_category_rule").isNull())
    
    if df_for_ml.count() == 0:
        print("All products categorized by rules. No ML prediction needed.")
        final_df = df_rules.select(
            "product_id", "product_name", 
            col("client_a_category_rule").alias("final_category_a"),
            col("client_b_category_rule").alias("final_category_b")
        )
    else:
        print(f"Found {df_for_ml.count()} products for ML prediction.")
        
        # 5. Load ML Artifacts from GCS
        print("Loading ML artifacts from GCS...")
        vectorizer = load_gcs_artifact(GCS_BUCKET_NAME, "model_artifacts/v1/client_a/tfidf_vectorizer.joblib")
        le_a = load_gcs_artifact(GCS_BUCKET_NAME, "model_artifacts/v1/client_a/label_encoder_a.joblib")
        le_b = load_gcs_artifact(GCS_BUCKET_NAME, "model_artifacts/v1/client_b/label_encoder_b.joblib")

        # 6. Feature Engineering and Prediction
        pandas_for_ml = df_for_ml.toPandas()
        pandas_for_ml['combined_features'] = pandas_for_ml['product_name'] + " " + pandas_for_ml['about_product'].fillna('')
        X_to_predict = vectorizer.transform(pandas_for_ml['combined_features'])

        print("Getting predictions from Vertex AI...")
        aiplatform.init(project=GCP_PROJECT_ID, location=VERTEX_LOCATION)
        endpoint = aiplatform.Endpoint(VERTEX_ENDPOINT_ID)
        
        # Get predictions for Client A
        preds_a_raw = endpoint.predict(instances=X_to_predict.toarray().tolist(), parameters={"deployed_model_id": DEPLOYED_MODEL_ID_A})
        ml_preds_a = le_a.inverse_transform(preds_a_raw.predictions)
        
        # Get predictions for Client B
        preds_b_raw = endpoint.predict(instances=X_to_predict.toarray().tolist(), parameters={"deployed_model_id": DEPLOYED_MODEL_ID_B})
        ml_preds_b = le_b.inverse_transform(preds_b_raw.predictions)
        
        pandas_for_ml['ml_category_a'] = ml_preds_a
        pandas_for_ml['ml_category_b'] = ml_preds_b
        
        df_ml_results = spark.createDataFrame(pandas_for_ml[["product_id", "ml_category_a", "ml_category_b"]])

        # 8. Combine Rule and ML Results
        print("Combining rule and ML results...")
        final_df = df_rules.join(df_ml_results, "product_id", "left").withColumn(
            "final_category_a",
            when(col("client_a_category_rule").isNotNull(), col("client_a_category_rule")).otherwise(col("ml_category_a"))
        ).withColumn(
            "final_category_b",
            when(col("client_b_category_rule").isNotNull(), col("client_b_category_rule")).otherwise(col("ml_category_b"))
        ).select("product_id", "product_name", "final_category_a", "final_category_b")

    # 9. Write Final Data to BigQuery
    print(f"Writing final results to {BIGQUERY_FINAL_TABLE}...")
    final_df.write.format('bigquery').option('table', BIGQUERY_FINAL_TABLE).mode('overwrite').save()
    
    print("Pipeline finished successfully!")

if __name__ == "__main__":
    main()