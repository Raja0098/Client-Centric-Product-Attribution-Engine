# Product Attribution Tagging Guide

This document outlines the official rules and procedures for manually tagging the ground-truth dataset. Consistent application of these rules is critical for training a high-quality machine learning model.

---

## 1. Core Principles

- **Consistency is Key:** Always refer back to this guide to ensure each product is evaluated using the same logic.  
- **Use Your Judgment:** The rules will not cover every product. When a case is ambiguous, make a logical choice and document your reasoning in the `notes` column.  
- **Prioritize Primary Function:** For products that could fit multiple categories (e.g., a "smart mug"), classify them based on their primary, most obvious function.  

---

## 2. Client A: The "Alpha Seeker" Fund

**Objective:** Achieve maximum granularity. Track specific features and premium product lines.

### Rule A1: Phone Tier Classification
- **IF** `product_name` contains `"Pro"`, `"Max"`, or `"Ultra"` **OR** `actual_price > ₹60,000`,  
  **THEN** `client_a_category = Mobile > Phones > Premium Tier`.  

- **ELSE IF** `actual_price` is between `₹20,000` and `₹60,000`,  
  **THEN** `client_a_category = Mobile > Phones > Mid-Tier`.  

- **ELSE IF** the product is a phone,  
  **THEN** `client_a_category = Mobile > Phones > Value Tier`.  

### Rule A2: Specific Computing Accessories
- **IF** `product_name` contains `"keyboard"` **AND** `"mechanical"`,  
  **THEN** `client_a_category = Computing > Accessories > Keyboards (Mechanical)`.  

- **IF** `product_name` contains `"webcam"`,  
  **THEN** `client_a_category = Computing > Accessories > Webcams`.  

### Rule A3: Specific Audio Devices
- **IF** `product_name` contains `"headphone"` **AND** (`"noise cancelling"` OR `"ANC"`),  
  **THEN** `client_a_category = Audio > Headphones > Over-Ear (Noise Cancelling)`.  

- **IF** `product_name` contains `"speaker"` **AND** `"bluetooth"`,  
  **THEN** `client_a_category = Audio > Speakers > Portable Bluetooth`.  

---

## 3. Client B: The "Category Manager"

**Objective:** Create broad, shoppable departments and segment products by price.

### Rule B1: Broad Department Classification
- **IF** `product_name` contains `"phone"`, `"cable"`, `"charger"`, `"speaker"`, `"headphone"`, `"webcam"`, or `"keyboard"`,  
  **THEN** `client_b_department = Electronics`.  

- **IF** `product_name` contains `"heater"`, `"kettle"`, `"blender"`, `"purifier"`, `"cookware"`, or `"kitchen"`,  
  **THEN** `client_b_department = Home & Kitchen`.  

- **IF** `product_name` contains `"shirt"`, `"shoes"`, `"watch"`, `"jeans"`, or `"women's"`,  
  **THEN** `client_b_department = Apparel & Accessories`.  

### Rule B2: Price Tier Classification (Applies to ALL products)
- **IF** `actual_price < ₹2,000`,  
  **THEN** `client_b_price_tier = Value`.  

- **IF** `actual_price` is between `₹2,000` and `₹8,000`,  
  **THEN** `client_b_price_tier = Mid-Range`.  

- **IF** `actual_price > ₹8,000`,  
  **THEN** `client_b_price_tier = Premium`.  
