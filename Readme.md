# Client-Centric Product Attribution Engine



This repository contains a production-ready prototype of a full-scale data pipeline that intelligently maps raw e-commerce product data into client-specific taxonomies. It demonstrates a hybrid approach that combines a **high-precision SQL rule-based engine** with a **flexible hierarchical machine learning model** to achieve both scale and accuracy.

---

## 1. The Business Problem: Beyond a "One-Size-Fits-All" Taxonomy
In market research and retail analytics, corporate clients view their product catalogs through unique strategic lenses. A generic taxonomy is insufficient for generating actionable insights.

This project tackles this challenge by building a system to ingest raw product data and map it into two distinct, client-driven taxonomies:

- **Client A ("The Alpha Seeker")**: Requires deep, feature-rich granularity for market opportunity analysis.  
  *Example:* `Audio > Headphones > Over-Ear (Noise Cancelling)`

- **Client B ("The Category Manager")**: Needs broad, department-level categories with clear price segmentation for high-level performance tracking.  
  *Example:* `Electronics, Premium Tier`

---

## 2. The Solution: A Hybrid Rules + ML Engine
To solve this, we developed a hybrid attribution engine that leverages the strengths of both deterministic rules and probabilistic machine learning.

- **High-Precision Rules First**:  
  A robust SQL engine (BigQuery) classifies products with near-100% confidence based on keywords, brands, or price points.  

- **Intelligent ML for Ambiguity**:  
  Products not covered by rules are routed to a hierarchical ML pipeline.  
  - Level 1 models predict top-level categories.  
  - Level 2 models use Level 1 predictions as features, improving accuracy for fine-grained categories.  

---

## 3. Tech Stack & Architecture
- **Cloud Platform (Target):** Google Cloud Platform (GCP)  
- **Data Warehousing:** Google BigQuery  
- **Machine Learning (Local):** Python, Scikit-learn, Pandas  
- **Visualization & Insights:** Matplotlib, Seaborn, Plotly  
- **Languages:** SQL, Python  

The pipeline is built locally but designed for seamless deployment on GCP using **Vertex AI** (model hosting) and **Cloud Functions/Workflows** (orchestration).

---

## 4. Key Features
- **Hierarchical ML Model:**  
  A chained prediction pipeline where sub-category models are guided by parent predictions, mirroring human decision-making.  

- **Hybrid Tagging Logic:**  
  Combines rule-based precision with ML flexibility.  

- **Multi-Client Architecture:**  
  Onboard new clients by training new model heads on their unique taxonomies.  

- **Automated Insights Generation:**  
  Outputs are not just tagged data, but **strategic visualizations** that create immediate business value.  

---

## 5. Business Impact & Strategic Insights
This engine goes beyond tagging—it acts as a **strategic analysis tool**.  

Deliverables include visualizations that answer critical business questions:

- **Interactive Market Overview:**  
  Sunburst charts highlight catalog structure, resource allocation, and gaps.  

- **Competitive Price Landscape:**  
  Violin plots show market saturation and premium opportunities by price distribution.  

- **Market Opportunity Matrix:**  
  Bubble charts map sub-categories by **market size (product count)** and **market position (average price)**, revealing:  
  - *Mass-Market Battlegrounds*  
  - *Niche & Premium Opportunities*  
  - *Established Market Leaders*  

---

## 6. Project Deliverables
- **Trained ML Models**:  
  Five saved `.joblib` model files for Client A (hierarchical) and Client B (two-tier).  

- **Reusable SQL Rule Engine**:  
  BigQuery script at `sql/rule_based_tagging.sql` for deterministic first-pass categorization.  

- **End-to-End Local Pipeline**:  
  `run_pipeline.py` to train models and predict categories on new data.  

- **Client-Ready Insights Module**:  
  `generate_insights.py` to produce dashboards and visualizations from final tagged datasets.  

---

## 📌 Next Steps
This pipeline is extensible to:  
- New clients with custom taxonomies.  
- Cloud-native deployment on GCP (BigQuery + Vertex AI).  
- Integration with APIs (FastAPI/Flask) for real-time product tagging.  

- Add CI/CD pipeline for automatic model retraining using GitHub Actions.  
- Expand taxonomy rules for additional product categories.  
- Integrate a web dashboard (Streamlit) for reviewing outputs.

---

