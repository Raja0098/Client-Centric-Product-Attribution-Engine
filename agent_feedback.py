from langchain_google_genai import ChatGoogleGenerativeAI
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

def analyze_charts_with_gemini(output_dir: str, df: pd.DataFrame = None):
    """
    Uses Gemini to analyze actual data and produce a data-driven markdown report.
    """
    
    if df is None or df.empty:
        return "No data available to analyze."
    
    # Extract key statistics from the data
    split_cols = df['predicted_clienta_category'].str.split(' > ', expand=True, n=2)
    df['cat_level_1'] = split_cols[0]
    df['cat_level_2'] = split_cols[1]
    df['cat_level_3'] = split_cols[2] if split_cols.shape[1] > 2 else None
    df.fillna({'cat_level_2': 'N/A', 'cat_level_3': 'N/A'}, inplace=True)
    
    # Market overview statistics
    total_products = len(df)
    category_counts = df['cat_level_1'].value_counts().head(10).to_dict()
    
    # Price statistics by category
    price_stats = df.groupby('cat_level_1')['actual_price'].agg([
        ('mean', 'mean'),
        ('median', 'median'),
        ('min', 'min'),
        ('max', 'max'),
        ('count', 'count')
    ]).round(2).to_dict('index')
    
    # Opportunity matrix data - top opportunities
    opportunity_data = df.groupby(['cat_level_1', 'cat_level_2']).agg(
        avg_price=('actual_price', 'mean'),
        product_count=('product_name', 'count')
    ).round(2).sort_values('product_count', ascending=False).head(15).to_dict('index')
    
    # Top and bottom priced categories
    avg_by_cat = df.groupby('cat_level_1')['actual_price'].mean().sort_values(ascending=False)
    top_priced = avg_by_cat.head(5).to_dict()
    bottom_priced = avg_by_cat.tail(5).to_dict()
    
    # Build detailed prompt with actual data
    template = f"""
You are a senior market analyst generating a client insight report based on ACTUAL product classification data.

## DATASET OVERVIEW:
- Total Products Analyzed: {total_products}
- Top Product Categories (by count):
{category_counts}

## PRICE LANDSCAPE DATA:
Price statistics by category (₹):

Top 5 Highest-Priced Categories (Average):
{top_priced}

Top 5 Lowest-Priced Categories (Average):
{bottom_priced}

Detailed Statistics by Category:
{price_stats}

## OPPORTUNITY MATRIX DATA:
Top 15 Category-Subcategory Combinations (by product count):
{opportunity_data}

## YOUR TASK:
Based on this ACTUAL DATA, create a professional strategic insight report with:

1. **Executive Summary**: Brief overview of market landscape and key findings

2. **Market Structure Insights**: Analyze the category distribution, market concentration, and competitive dynamics using the specific numbers provided

3. **Category Trends & Pricing Analysis**: 
   - Identify high-volume vs. niche categories
   - Analyze pricing tiers (premium, mid-market, budget)
   - Highlight price gaps and opportunities

4. **Business Opportunities**: 
   - White space opportunities (high growth potential, low competition)
   - Underserved price points
   - Category expansion recommendations

5. **Strategic Recommendations**: Provide 2-3 concrete, actionable recommendations with specific category/price targets

Use the actual numbers and category names from the data. Be specific and data-driven.

Output format: Clean Markdown with headers (##, ###), bullet points, and bold text for emphasis.
"""
    
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
    
    print("🧠 Calling Gemini model with actual data...")
    response = model.invoke(template)
    
    output_text = response.content if hasattr(response, "content") else str(response)
    
    if not output_text or output_text.strip() == "":
        output_text = "Error: No feedback content generated. Please try again."
    
    print(f"✅ Generated report: {len(output_text)} characters")
    print(f"✅ Preview: {output_text[:200]}...")
    
    # Save feedback
    report_path = os.path.join(output_dir, "client_feedback.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(output_text)
    
    print(f"✅ Report saved at: {report_path}")
    
    return output_text


