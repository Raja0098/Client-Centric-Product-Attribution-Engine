-- This query cleans and applies rule-based tagging to a large product dataset.
-- It creates a final table ready for ML prediction on the remaining items.

CREATE OR REPLACE TABLE `project_id.product_raw_data.products_with_rules` AS (

WITH
  -- Step 1: Clean the raw data, especially the price column.
  cleaned_data AS (
    SELECT
      *,
      -- FIX: First, CAST the numeric actual_price to a STRING before using REPLACE.
      SAFE_CAST(REPLACE(REPLACE(CAST(actual_price AS STRING), '₹', ''), ',', '') AS NUMERIC) AS cleaned_price
    FROM
      `numeric-vehicle-466708-q3.product_raw_data.raw_data`
  ),

  -- Step 2: Apply the rule-based logic for both Client A and Client B
  rule_based_tagging AS (
    SELECT
      *,
      -- Client A Rules
      CASE
        WHEN LOWER(product_name) LIKE '%headphone%' AND (LOWER(product_name) LIKE '%noise cancelling%' OR LOWER(product_name) LIKE '%anc%') THEN 'Audio > Headphones > Over-Ear (Noise Cancelling)'
        WHEN LOWER(product_name) LIKE '%speaker%' AND LOWER(product_name) LIKE '%bluetooth%' THEN 'Audio > Speakers > Portable Bluetooth'
        WHEN LOWER(product_name) LIKE '%mechanical keyboard%' THEN 'Computing > Accessories > Keyboards (Mechanical)'
        WHEN LOWER(product_name) LIKE '%webcam%' THEN 'Computing > Accessories > Webcams'
        WHEN (LOWER(product_name) LIKE '%pro%' OR LOWER(product_name) LIKE '%max%' OR LOWER(product_name) LIKE '%ultra%') OR cleaned_price > 40000 THEN 'Mobile > Phones > Premium Tier'
        WHEN cleaned_price BETWEEN 20000 AND 60000 AND LOWER(product_name) LIKE '%phone%' THEN 'Mobile > Phones > Mid-Tier'
        WHEN LOWER(product_name) LIKE '%phone%' THEN 'Mobile > Phones > Value Tier'
        ELSE 'Needs_ML_Prediction' -- Default value for products the rules miss
      END AS rule_based_clienta_category,

      -- Client B Rules
      CASE
        WHEN LOWER(product_name) LIKE ANY ('%phone%', '%cable%', '%charger%', '%speaker%', '%headphone%', '%webcam%', '%keyboard%', '%earbuds%', '%power bank%', '%mouse%') THEN 'Electronics'
        WHEN LOWER(product_name) LIKE ANY ('%heater%', '%kettle%', '%blender%', '%purifier%', '%cookware%', '%kitchen%', '%geyser%') THEN 'Home & Kitchen'
        WHEN LOWER(product_name) LIKE ANY ('%shirt%', '%shoes%', '%watch%', '%jeans%') THEN 'Apparel & Accessories'
        ELSE 'Needs_ML_Prediction'
      END AS rule_based_clientb_department,

      CASE
        WHEN cleaned_price < 2000 THEN 'Value'
        WHEN cleaned_price BETWEEN 2000 AND 8000 THEN 'Mid-Range'
        WHEN cleaned_price > 8000 THEN 'Premium'
        ELSE NULL
      END AS rule_based_clientb_price_tier
    FROM
      cleaned_data
  )

-- Step 3: Create the final table with split columns for Client A
SELECT
  product_id,
  product_name,
  about_product,
  actual_price,
  rule_based_clienta_category,
  rule_based_clientb_department,
  rule_based_clientb_price_tier,
  SPLIT(rule_based_clienta_category, ' > ')[SAFE_OFFSET(0)] AS clienta_level_1,
  SPLIT(rule_based_clienta_category, ' > ')[SAFE_OFFSET(1)] AS clienta_level_2,
  SPLIT(rule_based_clienta_category, ' > ')[SAFE_OFFSET(2)] AS clienta_level_3
FROM
  rule_based_tagging

);

-- Check how many products were tagged by rules vs. how many need the ML model
SELECT
  rule_based_clienta_category,
  COUNT(*) AS product_count
FROM
  `Project_id.product_raw_data.products_with_rules`
GROUP BY
  1
ORDER BY
  product_count DESC;
