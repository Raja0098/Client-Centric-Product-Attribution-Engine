SQL Rule Engine for Product Attribution
-- This query applies a set of high-precision rules to categorize products
-- for two simulated clients. Null results are intended to be handled by a
-- downstream machine learning model.


SELECT
  product_name,

  -- =================================================================
  -- Rule Engine for Client A (The "Alpha Seeker" Fund)
  -- Logic: High precision, feature-focused.
  -- =================================================================
  CASE
    -- Rule A1: Identify Smartwatches
    WHEN LOWER(product_name) LIKE '%smart%' AND LOWER(product_name) LIKE '%watch%' THEN 'Mobile > Wearables > Smartwatches'

    -- Rule A2: Identify Premium Charging Cables
    WHEN LOWER(product_name) LIKE '%cable%' AND LOWER(product_name) LIKE '%braided%' THEN 'Computing > Accessories > Premium Cables'

    -- Rule A3: Identify Wireless Headphones
    WHEN LOWER(product_name) LIKE '%bluetooth%' AND (LOWER(product_name) LIKE '%headphone%' OR LOWER(product_name) LIKE '%earbud%') THEN 'Audio > Headphones > Wireless'

    ELSE NULL 
  END AS client_a_category,

  -- =================================================================
  -- Rule Engine for Client B (The "Category Manager")
  -- Logic: High recall, broad department-focused.
  -- =================================================================
  CASE
    -- Rule B3: Group All Watches (This rule should come BEFORE the 'Cable' rule to avoid misclassifying charging watches)
    WHEN LOWER(product_name) LIKE '%watch%' THEN 'Apparel > Accessories > Watches'

    -- Rule B1: Group All Cables & Chargers
    WHEN LOWER(product_name) LIKE '%cable%' OR LOWER(product_name) LIKE '%charger%' OR LOWER(product_name) LIKE '%adapter%' THEN 'Electronics > Accessories > Cables & Chargers'

    -- Rule B2: Group Small Electric Appliances
    WHEN LOWER(product_name) LIKE '%heater%' OR LOWER(product_name) LIKE '%electric%' THEN 'Home > Small Appliances'

    ELSE NULL -- Let ML handle the rest
  END AS client_b_category

FROM
  `your-project-id.product_data_raw.raw_products`
LIMIT 1000;
