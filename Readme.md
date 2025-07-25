# Client-Centric Product Attribution Engine  
**Project Status:** *In Progress*  

This repository demonstrates the design and prototyping of a **full-scale data pipeline** that combines **rule-based logic** with **machine learning** to map raw e-commerce product data into **client-specific taxonomies**. The project reflects the real-world challenges faced by data operations teams, like those at YipitData.

---

## **1. Problem Statement**  
In the world of market research and retail analytics, a single, standardized product taxonomy is often insufficient.  
Corporate clients organize their product categories in unique ways.  

This project simulates that challenge by building a scalable system on **Google Cloud Platform (GCP)** to ingest raw product data and map it into **two distinct taxonomies**:

- **Client A ("The Alpha Seeker")**: Requires deep, feature-rich granularity.  
  *Example:* `Audio > Headphones > Over-Ear (Noise Cancelling)`.  
- **Client B ("The Category Manager")**: Needs broad, department-level categories with price segmentation.  
  *Example:* `Electronics, Value Tier`.  

---

## **2. Tech Stack & Architecture**  

**Cloud Platform:** Google Cloud Platform (GCP)  
**Data Storage & Warehousing:** Google Cloud Storage (GCS), BigQuery  
**Data Processing:** PySpark on Dataproc  
**Machine Learning:** Scikit-learn & Vertex AI (Model Training & Endpoints)  
**Languages:** Python, SQL  

**Architecture Overview:**  

*See `architecture.png` for the complete pipeline diagram.*

---

## **3. Methodology**  

The engine uses a **hybrid Rules + ML approach**:  
1. **Data Curation & Ground Truth**  
   - Manually tagged **100+ products** using a custom [Tagging Guide](data_curation/Tagging_Guide.md).  
   - Simulates "judgment and interpretation" required for high-quality mapping.  

2. **Rule-Based Engine**  
   - A SQL-based rules engine in BigQuery handles **high-confidence cases** (e.g., specific brands or keywords).  

3. **Machine Learning Model**  
   - **RandomForestClassifier** trained on curated ground-truth data to predict ambiguous product categories.  
   - Model deployed using **Vertex AI Endpoints** for inference.  

4. **End-to-End Orchestration**  
   - A **PySpark pipeline** automates rules, calls Vertex AI predictions, merges outputs, and loads results into BigQuery.

---

## **4. Key Outcomes & Deliverables**  
- **Deployed ML Endpoint:** Two models (Client A & B taxonomy) hosted on Vertex AI.  
- **Reusable Rule Engine:** SQL scripts for high-precision categorization.  
- **High-Quality Training Dataset:** 1,400+ products tagged for accuracy and completeness.  
- **Pipeline Blueprint:** A production-ready PySpark orchestration script (`scripts/attribution_pipeline.py`).  

---


---

## **6. How to Run**  
1. **Set up GCP environment** and enable BigQuery, Dataproc, and Vertex AI APIs.  
2. Upload `attribution_pipeline.py` to GCS.  
3. Submit a PySpark job on **Dataproc** to execute the complete pipeline.  
4. View final outputs in BigQuery's `final_product_attributions` table.

---

## **7. Next Steps**  
- Add CI/CD pipeline for automatic model retraining using GitHub Actions.  
- Expand taxonomy rules for additional product categories.  
- Integrate a web dashboard (Streamlit) for reviewing outputs.

---

