import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

from agent_feedback import analyze_charts_with_gemini  # keep your Gemini agent

# --- Configuration ---
DATA_DIR = "data"
FINAL_DATA_FILE = os.path.join(DATA_DIR, "predicted.csv")
sns.set_theme(style="whitegrid")


def generate_strategic_insights(filepath=FINAL_DATA_FILE, output_dir="outputs"):
    """
    Loads the final tagged dataset and generates three expert-level
    visualizations with business insights + Gemini feedback summary.
    """
    os.makedirs(output_dir, exist_ok=True)

    # --- Load Data ---
    print("--- Loading Final Dataset ---")
    try:
        df = pd.read_csv(filepath)
        print(f"✅ Loaded {len(df)} tagged products.")
    except FileNotFoundError:
        print(f"❌ File not found at '{filepath}'.")
        return None

    # --- Prepare Data ---
    split_cols = df['predicted_clienta_category'].str.split(' > ', expand=True, n=2)
    df['cat_level_1'] = split_cols[0]
    df['cat_level_2'] = split_cols[1]
    df['cat_level_3'] = split_cols[2]
    df.fillna({'cat_level_2': 'N/A', 'cat_level_3': 'N/A'}, inplace=True)

    df['actual_price'] = (
        df['actual_price'].astype(str).str.replace(r'[₹,]', '', regex=True)
    )
    df['actual_price'] = pd.to_numeric(df['actual_price'], errors='coerce').dropna()

    # ==============================================================================
    # INSIGHT 1: Strategic Market Overview (Sunburst Chart)
    # ==============================================================================
    print("\n🧭 Generating Insight 1: Market Overview ...")
    sunburst_df = df.groupby(['cat_level_1', 'cat_level_2', 'cat_level_3']).size().reset_index(name='count')

    fig1 = px.sunburst(
        sunburst_df,
        path=['cat_level_1', 'cat_level_2', 'cat_level_3'],
        values='count',
        title='<b>Client A: Product Catalog Hierarchy</b>',
        color='cat_level_1',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig1.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    sunburst_path = os.path.join(output_dir, "insight_1_market_overview.html")
    fig1.write_html(sunburst_path)

    # ==============================================================================
    # INSIGHT 2: Competitive Price Landscape (Violin Plot)
    # ==============================================================================
    print("💰 Generating Insight 2: Price Landscape ...")
    top_categories = df['cat_level_1'].value_counts().nlargest(5).index
    price_df = df[df['cat_level_1'].isin(top_categories)]

    plt.figure(figsize=(15, 9))
    sns.violinplot(
        data=price_df,
        x='cat_level_1',
        y='actual_price',
        hue='cat_level_1',
        inner='quartile',
        palette='viridis',
        legend=False
    )
    plt.yscale('log')
    plt.title('Client A: Price Distribution & Market Concentration', fontsize=18, weight='bold')
    plt.xlabel('Top-Level Category', fontsize=12)
    plt.ylabel('Product Price (₹, log scale)', fontsize=12)
    plt.xticks(rotation=15)
    violin_path = os.path.join(output_dir, "insight_2_price_landscape.png")
    plt.savefig(violin_path, dpi=300)
    plt.close()

    # ==============================================================================
    # INSIGHT 3: Market Opportunity Matrix (Bubble Chart)
    # ==============================================================================
    print("📈 Generating Insight 3: Opportunity Matrix ...")
    opportunity_df = df.groupby(['cat_level_1', 'cat_level_2']).agg(
        avg_price=('actual_price', 'mean'),
        product_count=('product_name', 'count')
    ).reset_index()

    plt.figure(figsize=(16, 10))
    sns.scatterplot(
        data=opportunity_df,
        x='product_count',
        y='avg_price',
        size='product_count',
        sizes=(50, 2000),
        hue='cat_level_1',
        palette='muted',
        alpha=0.7
    )
    plt.title('Client A: Market Opportunity Matrix', fontsize=18, weight='bold')
    plt.xlabel('Number of Products (Market Size)', fontsize=12)
    plt.ylabel('Average Price (₹)', fontsize=12)
    plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    for i in range(opportunity_df.shape[0]):
        if opportunity_df['product_count'][i] > 5:
            plt.text(
                x=opportunity_df['product_count'][i] + 0.3,
                y=opportunity_df['avg_price'][i],
                s=opportunity_df['cat_level_2'][i],
                fontdict=dict(color='black', size=9)
            )

    opportunity_path = os.path.join(output_dir, "insight_3_opportunity_matrix.png")
    plt.savefig(opportunity_path, dpi=300)
    plt.close()

    # ==============================================================================
    # GEMINI FEEDBACK
    # ==============================================================================
    print("\n🧠 Generating strategic feedback using Gemini ...")
    feedback = analyze_charts_with_gemini(output_dir)

    feedback_path = os.path.join(output_dir, "client_feedback.txt")
    with open(feedback_path, "w") as f:
        f.write(feedback)

    print("✅ All insights generated successfully!")
    print("📊 Charts saved in:", output_dir)
    print("📝 Feedback saved in:", feedback_path)

    return {
        "sunburst": sunburst_path,
        "violin": violin_path,
        "bubble": opportunity_path,
        "feedback": feedback,
    }


if __name__ == "__main__":
    generate_strategic_insights()
