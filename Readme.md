# 🧠 Client-Centric Product Attribution Engine

This repository contains a **production-ready prototype** of a full-scale **data pipeline** that intelligently maps **raw e-commerce product data** into **client-specific taxonomies**.  
It demonstrates a **hybrid approach** combining a **high-precision SQL rule-based engine** with a **hierarchical machine learning model** and an **AI agent** for automated insight generation and reporting.

---

## 1. The Business Problem: Beyond a "One-Size-Fits-All" Taxonomy

In market research and retail analytics, corporate clients view their product catalogs through **unique strategic lenses**.  
A generic taxonomy is insufficient for generating actionable insights.

This project builds a system to ingest raw product data and map it into **distinct, client-driven taxonomies**:

- **Client A ("The Alpha Seeker")** – Requires **deep, feature-rich granularity** for detailed market opportunity analysis.  
  *Example: Audio > Headphones > Over-Ear (Noise Cancelling)*  

- **Client B ("The Category Manager")** – Needs **broad, department-level categories** with **price segmentation** for high-level performance tracking.  
  *Example: Electronics, Premium Tier*

---

## 2. The Solution: A Hybrid Rules + ML + Agent Engine

This project implements a **hybrid attribution system** that unites deterministic SQL rules, probabilistic ML, and intelligent insight automation.

### 🧩 Components:

**1️⃣ High-Precision Rule Engine:**  
A robust SQL logic classifies products with near-100% confidence using keywords, brand patterns, or price points.

**2️⃣ Hierarchical ML Pipeline:**  
Unmapped records are passed to a two-level machine learning hierarchy:
- **Level 1:** Predicts top-level category.
- **Level 2:** Uses Level 1 output as a feature for fine-grained sub-category classification.

**3️⃣ Automated Insight Agent:**  
An **LLM-based agent** analyzes the charts and metrics generated,  
produces a **summary of findings**, identifies anomalies or opportunities,  
and can **generate a client-ready report** or request additional data for deeper analysis.

---

## 3. Tech Stack & Architecture

### 🧠 Tech Stack

- **Languages:** Python, SQL  
- **Libraries:** Pandas, Scikit-learn, Matplotlib, Seaborn, Plotly  
- **App Framework:** FastAPI (for agent integration & reporting)  
- **Model Serialization:** Joblib  
- **Visualization:** Matplotlib / Seaborn / Plotly  
- **LLM Integration:** LangGraph-based agent  

---

### 🏗️ System Architecture

```mermaid
graph TD
    %% Define Nodes
    A[📦 Raw Product Data]
    B[⚙️ Rule Engine (SQL)]
    C[❓ Unmapped Records]
    D[🤖 Hierarchical ML Attribution]
    E[🗂️ Final Tagged Dataset]
    F[🧠 Insight Generator Agent]
    G[📊 Interactive Client Report]

    %% Define Flow
    A --> B
    B -- Unmapped Flow --> C
    C --> D
    D --> E
    E --> F
    F --> G

    %% Group by functional stages
    subgraph Data_Preprocessing [🧾 Data Processing]
        A
        B
        C
    end

    subgraph ML_Attribution [🤖 ML Attribution Layer]
        D
        E
    end

    subgraph Insights [📈 Insights & Reporting]
        F
        G
    end

    %% Apply Styles
    style A fill:#DCEBFF,stroke:#0047AB,stroke-width:2px,color:#000
    style B fill:#FFF3B0,stroke:#C59A00,stroke-width:2px,color:#000
    style C fill:#FFD6A5,stroke:#E67E22,stroke-width:2px,color:#000
    style D fill:#E0BBE4,stroke:#6A1B9A,stroke-width:2px,color:#000
    style E fill:#C1FFD7,stroke:#2E8B57,stroke-width:2px,color:#000
    style F fill:#FFE6E6,stroke:#B22222,stroke-width:2px,color:#000
    style G fill:#FFCCD5,stroke:#C21807,stroke-width:2px,color:#000

    %% Subgraph colors (borders)
    style Data_Preprocessing fill:#F7FBFF,stroke:#4682B4,stroke-width:2px
    style ML_Attribution fill:#F9F7FF,stroke:#8A2BE2,stroke-width:2px
    style Insights fill:#FFF9F9,stroke:#B22222,stroke-width:2px


```
---

## 4. Key Features

### 🔗 Hierarchical ML Model  
Chained prediction pipeline where **sub-category models** are guided by **parent-level predictions**, mirroring real decision-making.

### ⚙️ Hybrid Tagging Logic  
Combines **rule-based precision** with **ML flexibility** for high accuracy even in ambiguous cases.

### 👥 Multi-Client Architecture  
Easily onboard new clients by training **custom model heads** aligned with their taxonomy.

### 📊 Automated Insights Generation  
Outputs include not just tagged data, but **visual reports and analytical charts** ready for client presentations.

### 🤖 AI Agent Integration  
The agent:
- Analyzes the visualizations and data summaries.
- Generates a **narrative business summary**.
- Provides **data-driven recommendations**.
- Can automatically **create client-ready reports** in text or HTML.

---

## 5. Business Impact & Strategic Insights

This engine goes **beyond tagging** — it acts as a **strategic analysis tool** for market researchers and analysts.

### Deliverables include:
- **Interactive Market Overview:**  
  Sunburst charts reveal catalog hierarchy, coverage, and focus areas.  
- **Competitive Price Landscape:**  
  Violin plots visualize pricing tiers and premium gaps.  
- **Market Opportunity Matrix:**  
  Bubble charts show market saturation vs. price opportunities.

### Example Business Insights:
- Identify **mass-market vs. premium gaps**.  
- Discover **underrepresented sub-categories**.  
- Highlight **growth segments** based on pricing trends.

---

## 6. Project Deliverables

- **Trained ML Models:**  
  Five saved `.joblib` models for Client A (hierarchical) and Client B (two-tier).

- **Reusable SQL Rule Engine:**  
  SQL script for deterministic first-pass categorization (`sql/rule_based_tagging.sql`).

- **End-to-End Local Pipeline:**  
  `run_pipeline.py` to train, infer, and generate tagged datasets.

- **Insights & Visualization Module:**  
  `generate_insights.py` creates interactive and static visualizations.

- **AI Agent & Report Generator:**  
  `agent_summary.py` (or `insight_agent.py`) generates natural-language summaries and business reports.

---

## 7. Example Insights Generated

| Chart Type | Description |
|-------------|--------------|
| 🌀 **Sunburst Chart** | Product hierarchy and depth visualization |
| 💎 **Violin Plot** | Price distribution across category tiers |
| 🫧 **Bubble Chart** | Market size vs. price-position analysis |
| 🧠 **Agent Summary** | Auto-generated insights and recommendations |

Example output:
> “Premium headphone market dominates 32% of total SKUs, while mid-tier wired headphones show underrepresentation — potential category expansion opportunity.”

---

## 8. How to Run

```bash
# Create environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python run_pipeline.py

# Generate charts and insights
python generate_insights.py

# Start the FastAPI app (agent summary interface)
uvicorn main:app --reload


