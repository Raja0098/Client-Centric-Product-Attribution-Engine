import pandas as pd
import joblib
import os
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from agent_feedback import analyze_charts_with_gemini

MODELS_DIR = "models"

def load_and_clean_data(filepath):
    """Loads and performs initial cleaning on a CSV file."""
    df = pd.read_csv(filepath)
    df['actual_price'] = df['actual_price'].astype(str).str.replace(r'[₹,]', '', regex=True)
    df['actual_price'] = pd.to_numeric(df['actual_price'], errors='coerce')
    df.dropna(subset=['actual_price'], inplace=True)
    df['combined_text'] = df['product_name'].fillna('') + " " + df['about_product'].fillna('')
    return df


def predict_categories(df):
    """Takes a DataFrame and returns it with all predictions."""
    try:
        pipeline_l1 = joblib.load(os.path.join(MODELS_DIR, "pipeline_l1.joblib"))
        pipeline_l2 = joblib.load(os.path.join(MODELS_DIR, "pipeline_l2.joblib"))
        pipeline_l3 = joblib.load(os.path.join(MODELS_DIR, "pipeline_l3.joblib"))
        pipeline_b_dept = joblib.load(os.path.join(MODELS_DIR, "pipeline_clientb_dept.joblib"))
        pipeline_b_price = joblib.load(os.path.join(MODELS_DIR, "pipeline_clientb_price.joblib"))
    except FileNotFoundError:
        raise RuntimeError("Model files not found in the 'models' directory.")

    # Client A Hierarchical Prediction
    df['predicted_level_1'] = pipeline_l1.predict(df[['combined_text', 'actual_price']])
    df['predicted_level_2'] = pipeline_l2.predict(df[['combined_text', 'actual_price', 'predicted_level_1']])
    df['predicted_level_3'] = pipeline_l3.predict(df[['combined_text', 'actual_price', 'predicted_level_1', 'predicted_level_2']])
    df['predicted_clienta_category'] = df['predicted_level_1'] + ' > ' + df['predicted_level_2'] + ' > ' + df['predicted_level_3']

    # Client B Prediction
    df['predicted_clientb_department'] = pipeline_b_dept.predict(df[['combined_text', 'actual_price']])
    df['predicted_clientb_price_tier'] = pipeline_b_price.predict(df[['combined_text', 'actual_price']])
    
    return df  # Return FULL DataFrame, not just selected columns


def generate_strategic_insights(df, output_dir):
    """Generates charts and AI feedback from tagged DataFrame."""
    os.makedirs(output_dir, exist_ok=True)
    
    print("--- Generating Strategic Insights ---")
    print(f"📊 Working with {len(df)} products")
    
    # Ensure we have the category column
    if 'predicted_clienta_category' not in df.columns:
        print("❌ Error: predicted_clienta_category column missing")
        return None
    
    # Prep for analysis
    split_cols = df['predicted_clienta_category'].str.split(' > ', expand=True, n=2)
    df['cat_level_1'] = split_cols[0]
    df['cat_level_2'] = split_cols[1]
    df['cat_level_3'] = split_cols[2] if split_cols.shape[1] > 2 else None
    df.fillna({'cat_level_2': 'N/A', 'cat_level_3': 'N/A'}, inplace=True)

    # Chart 1: Sunburst
    print("\n🧭 Generating Insight 1: Market Overview ...")
    sunburst_df = df.groupby(['cat_level_1', 'cat_level_2', 'cat_level_3']).size().reset_index(name='count')
    fig1 = px.sunburst(
        sunburst_df,
        path=['cat_level_1', 'cat_level_2', 'cat_level_3'],
        values='count',
        title='<b>Product Catalog Hierarchy</b>',
        color='cat_level_1',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig1.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    sunburst_path = os.path.join(output_dir, "insight_1_market_overview.html")
    fig1.write_html(sunburst_path)

    # Chart 2: Violin Plot
    print("💰 Generating Insight 2: Price Landscape ...")
    top_categories = df['cat_level_1'].value_counts().nlargest(5).index
    price_df = df[df['cat_level_1'].isin(top_categories)]
    
    plt.figure(figsize=(15, 9))
    sns.violinplot(data=price_df, x='cat_level_1', y='actual_price', hue='cat_level_1', inner='quartile', palette='viridis', legend=False)
    plt.yscale('log')
    plt.title('Price Distribution & Market Concentration', fontsize=18, weight='bold')
    plt.xlabel('Category', fontsize=12)
    plt.ylabel('Price (₹, log scale)', fontsize=12)
    plt.xticks(rotation=15)
    violin_path = os.path.join(output_dir, 'insight_2_price_landscape.png')
    plt.savefig(violin_path, dpi=300, bbox_inches='tight')
    plt.close()

    # Chart 3: Bubble Chart
    print("📈 Generating Insight 3: Opportunity Matrix ...")
    opportunity_df = df.groupby(['cat_level_1', 'cat_level_2']).agg(
        avg_price=('actual_price', 'mean'),
        product_count=('product_name', 'count')
    ).reset_index()
    
    plt.figure(figsize=(16, 10))
    sns.scatterplot(data=opportunity_df, x='product_count', y='avg_price', size='product_count', sizes=(50, 2000), hue='cat_level_1', palette='muted', alpha=0.7)
    plt.title('Market Opportunity Matrix', fontsize=18, weight='bold')
    plt.xlabel('Product Count', fontsize=12)
    plt.ylabel('Average Price (₹)', fontsize=12)
    plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    opportunity_path = os.path.join(output_dir, 'insight_3_opportunity_matrix.png')
    plt.savefig(opportunity_path, dpi=300, bbox_inches='tight')
    plt.close()

    # AI Feedback with DataFrame
    print("\n🧠 Generating strategic feedback with Gemini...")
    print(f"📊 Passing DataFrame with {len(df)} rows to Gemini")
    
    try:
        feedback = analyze_charts_with_gemini(output_dir, df)  # CRITICAL: Pass df here
        print(f"✅ Feedback generated: {len(feedback)} chars")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        feedback = f"Error generating feedback: {str(e)}"
    
    print(f"✅ All insights saved to '{output_dir}'")
    
    return {
        "sunburst": sunburst_path,
        "violin": violin_path,
        "bubble": opportunity_path,
        "feedback": feedback,
    }
