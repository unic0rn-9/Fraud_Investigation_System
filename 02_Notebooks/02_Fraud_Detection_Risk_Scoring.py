# Databricks notebook source
# DBTITLE 1,Fraud Detection Risk Scoring - Module 2
# MAGIC %sql
# MAGIC
# MAGIC -- ========================================
# MAGIC -- MODULE 2: Fraud Detection & Risk Scoring
# MAGIC -- ========================================
# MAGIC -- Source: workspace.default.fraud_transactions
# MAGIC -- Target: workspace.default.fraud_detection_results
# MAGIC
# MAGIC CREATE OR REPLACE TABLE workspace.default.fraud_detection_results AS
# MAGIC
# MAGIC WITH
# MAGIC
# MAGIC -- ========================================
# MAGIC -- 1. Calculate overall transaction amount statistics
# MAGIC -- ========================================
# MAGIC amount_stats AS (
# MAGIC     SELECT
# MAGIC         PERCENTILE_APPROX(amount, 0.90) AS p90_amount,
# MAGIC         PERCENTILE_APPROX(amount, 0.95) AS p95_amount,
# MAGIC         AVG(amount) AS avg_amount,
# MAGIC         STDDEV(amount) AS stddev_amount
# MAGIC     FROM workspace.default.fraud_transactions
# MAGIC ),
# MAGIC
# MAGIC -- ========================================
# MAGIC -- 2. Calculate transaction frequency
# MAGIC -- ========================================
# MAGIC transaction_frequency AS (
# MAGIC     SELECT
# MAGIC         transaction_id,
# MAGIC         user_id,
# MAGIC
# MAGIC         -- Transactions by the same user in the previous 1 hour
# MAGIC         COUNT(*) OVER (
# MAGIC             PARTITION BY user_id
# MAGIC             ORDER BY UNIX_TIMESTAMP(timestamp)
# MAGIC             RANGE BETWEEN 3600 PRECEDING AND CURRENT ROW
# MAGIC         ) - 1 AS txn_count_1hr,
# MAGIC
# MAGIC         -- Transactions by the same user in the previous 24 hours
# MAGIC         COUNT(*) OVER (
# MAGIC             PARTITION BY user_id
# MAGIC             ORDER BY UNIX_TIMESTAMP(timestamp)
# MAGIC             RANGE BETWEEN 86400 PRECEDING AND CURRENT ROW
# MAGIC         ) - 1 AS txn_count_24hr
# MAGIC
# MAGIC     FROM workspace.default.fraud_transactions
# MAGIC ),
# MAGIC
# MAGIC -- ========================================
# MAGIC -- 3. Count distinct countries per user
# MAGIC -- ========================================
# MAGIC user_country_counts AS (
# MAGIC     SELECT
# MAGIC         user_id,
# MAGIC         COUNT(DISTINCT country) AS distinct_countries_user
# MAGIC     FROM workspace.default.fraud_transactions
# MAGIC     GROUP BY user_id
# MAGIC ),
# MAGIC
# MAGIC -- ========================================
# MAGIC -- 4. Count distinct devices per user
# MAGIC -- ========================================
# MAGIC user_device_counts AS (
# MAGIC     SELECT
# MAGIC         user_id,
# MAGIC         COUNT(DISTINCT device) AS distinct_devices_user
# MAGIC     FROM workspace.default.fraud_transactions
# MAGIC     GROUP BY user_id
# MAGIC ),
# MAGIC
# MAGIC -- ========================================
# MAGIC -- 5. Find user's primary country
# MAGIC -- ========================================
# MAGIC country_frequency AS (
# MAGIC     SELECT
# MAGIC         user_id,
# MAGIC         country,
# MAGIC         COUNT(*) AS country_count
# MAGIC     FROM workspace.default.fraud_transactions
# MAGIC     GROUP BY user_id, country
# MAGIC ),
# MAGIC
# MAGIC primary_country AS (
# MAGIC     SELECT
# MAGIC         user_id,
# MAGIC         country AS user_primary_country
# MAGIC     FROM (
# MAGIC         SELECT
# MAGIC             user_id,
# MAGIC             country,
# MAGIC             country_count,
# MAGIC             ROW_NUMBER() OVER (
# MAGIC                 PARTITION BY user_id
# MAGIC                 ORDER BY country_count DESC, country
# MAGIC             ) AS rn
# MAGIC         FROM country_frequency
# MAGIC     )
# MAGIC     WHERE rn = 1
# MAGIC ),
# MAGIC
# MAGIC -- ========================================
# MAGIC -- 6. Find user's primary device
# MAGIC -- ========================================
# MAGIC device_frequency AS (
# MAGIC     SELECT
# MAGIC         user_id,
# MAGIC         device,
# MAGIC         COUNT(*) AS device_count
# MAGIC     FROM workspace.default.fraud_transactions
# MAGIC     GROUP BY user_id, device
# MAGIC ),
# MAGIC
# MAGIC primary_device AS (
# MAGIC     SELECT
# MAGIC         user_id,
# MAGIC         device AS user_primary_device
# MAGIC     FROM (
# MAGIC         SELECT
# MAGIC             user_id,
# MAGIC             device,
# MAGIC             device_count,
# MAGIC             ROW_NUMBER() OVER (
# MAGIC                 PARTITION BY user_id
# MAGIC                 ORDER BY device_count DESC, device
# MAGIC             ) AS rn
# MAGIC         FROM device_frequency
# MAGIC     )
# MAGIC     WHERE rn = 1
# MAGIC ),
# MAGIC
# MAGIC -- ========================================
# MAGIC -- 7. Combine all user behavior information
# MAGIC -- ========================================
# MAGIC user_patterns AS (
# MAGIC     SELECT
# MAGIC         tf.transaction_id,
# MAGIC         tf.user_id,
# MAGIC         tf.txn_count_1hr,
# MAGIC         tf.txn_count_24hr,
# MAGIC         ucc.distinct_countries_user,
# MAGIC         udc.distinct_devices_user,
# MAGIC         pc.user_primary_country,
# MAGIC         pd.user_primary_device
# MAGIC
# MAGIC     FROM transaction_frequency tf
# MAGIC
# MAGIC     LEFT JOIN user_country_counts ucc
# MAGIC         ON tf.user_id = ucc.user_id
# MAGIC
# MAGIC     LEFT JOIN user_device_counts udc
# MAGIC         ON tf.user_id = udc.user_id
# MAGIC
# MAGIC     LEFT JOIN primary_country pc
# MAGIC         ON tf.user_id = pc.user_id
# MAGIC
# MAGIC     LEFT JOIN primary_device pd
# MAGIC         ON tf.user_id = pd.user_id
# MAGIC ),
# MAGIC
# MAGIC -- ========================================
# MAGIC -- 8. Create fraud indicators
# MAGIC -- ========================================
# MAGIC fraud_indicators AS (
# MAGIC     SELECT
# MAGIC         t.*,
# MAGIC
# MAGIC         up.txn_count_1hr,
# MAGIC         up.txn_count_24hr,
# MAGIC         up.distinct_countries_user,
# MAGIC         up.distinct_devices_user,
# MAGIC         up.user_primary_country,
# MAGIC         up.user_primary_device,
# MAGIC
# MAGIC         ast.p90_amount,
# MAGIC         ast.p95_amount,
# MAGIC         ast.avg_amount,
# MAGIC         ast.stddev_amount,
# MAGIC
# MAGIC         -- Indicator 1: High transaction amount
# MAGIC         CASE
# MAGIC             WHEN t.amount > ast.p95_amount THEN 1
# MAGIC             ELSE 0
# MAGIC         END AS indicator_high_amount,
# MAGIC
# MAGIC         -- Indicator 2: Extreme transaction amount
# MAGIC         CASE
# MAGIC             WHEN t.amount > (ast.avg_amount + 3 * ast.stddev_amount) THEN 1
# MAGIC             ELSE 0
# MAGIC         END AS indicator_extreme_amount,
# MAGIC
# MAGIC         -- Indicator 3: High transaction frequency in 1 hour
# MAGIC         CASE
# MAGIC             WHEN up.txn_count_1hr >= 3 THEN 1
# MAGIC             ELSE 0
# MAGIC         END AS indicator_high_frequency_1hr,
# MAGIC
# MAGIC         -- Indicator 4: High transaction frequency in 24 hours
# MAGIC         CASE
# MAGIC             WHEN up.txn_count_24hr >= 10 THEN 1
# MAGIC             ELSE 0
# MAGIC         END AS indicator_high_frequency_24hr,
# MAGIC
# MAGIC         -- Indicator 5: User has transactions from multiple countries
# MAGIC         CASE
# MAGIC             WHEN up.distinct_countries_user >= 3 THEN 1
# MAGIC             ELSE 0
# MAGIC         END AS indicator_multiple_countries,
# MAGIC
# MAGIC         -- Indicator 6: Transaction country differs from primary country
# MAGIC         CASE
# MAGIC             WHEN t.country != up.user_primary_country THEN 1
# MAGIC             ELSE 0
# MAGIC         END AS indicator_unusual_country,
# MAGIC
# MAGIC         -- Indicator 7: User has multiple devices
# MAGIC         CASE
# MAGIC             WHEN up.distinct_devices_user >= 3 THEN 1
# MAGIC             ELSE 0
# MAGIC         END AS indicator_multiple_devices,
# MAGIC
# MAGIC         -- Indicator 8: Transaction device differs from primary device
# MAGIC         CASE
# MAGIC             WHEN t.device != up.user_primary_device THEN 1
# MAGIC             ELSE 0
# MAGIC         END AS indicator_unusual_device,
# MAGIC
# MAGIC         -- Indicator 9: Unusual transaction hour
# MAGIC         CASE
# MAGIC             WHEN t.hour >= 2 AND t.hour < 5 THEN 1
# MAGIC             ELSE 0
# MAGIC         END AS indicator_unusual_hour
# MAGIC
# MAGIC     FROM workspace.default.fraud_transactions t
# MAGIC
# MAGIC     CROSS JOIN amount_stats ast
# MAGIC
# MAGIC     LEFT JOIN user_patterns up
# MAGIC         ON t.transaction_id = up.transaction_id
# MAGIC         AND t.user_id = up.user_id
# MAGIC ),
# MAGIC
# MAGIC -- ========================================
# MAGIC -- 9. Calculate risk score
# MAGIC -- ========================================
# MAGIC risk_calculation AS (
# MAGIC     SELECT
# MAGIC         *,
# MAGIC
# MAGIC         LEAST(
# MAGIC             100,
# MAGIC
# MAGIC             (indicator_extreme_amount * 25) +
# MAGIC             (indicator_high_amount * 15) +
# MAGIC             (indicator_high_frequency_1hr * 20) +
# MAGIC             (indicator_high_frequency_24hr * 10) +
# MAGIC             (indicator_multiple_countries * 12) +
# MAGIC             (indicator_unusual_country * 8) +
# MAGIC             (indicator_multiple_devices * 10) +
# MAGIC             (indicator_unusual_device * 5) +
# MAGIC             (indicator_unusual_hour * 5)
# MAGIC
# MAGIC         ) AS risk_score
# MAGIC
# MAGIC     FROM fraud_indicators
# MAGIC )
# MAGIC
# MAGIC -- ========================================
# MAGIC -- 10. Final output
# MAGIC -- ========================================
# MAGIC SELECT
# MAGIC
# MAGIC     -- Original transaction information
# MAGIC     transaction_id,
# MAGIC     user_id,
# MAGIC     timestamp,
# MAGIC     amount,
# MAGIC     country,
# MAGIC     device,
# MAGIC     channel,
# MAGIC     hour,
# MAGIC     dayofweek,
# MAGIC     coupon_applied,
# MAGIC     num_items,
# MAGIC     is_fraud,
# MAGIC
# MAGIC     -- User behavior information
# MAGIC     txn_count_1hr,
# MAGIC     txn_count_24hr,
# MAGIC     distinct_countries_user,
# MAGIC     distinct_devices_user,
# MAGIC     user_primary_country,
# MAGIC     user_primary_device,
# MAGIC
# MAGIC     -- Fraud indicators
# MAGIC     indicator_high_amount,
# MAGIC     indicator_extreme_amount,
# MAGIC     indicator_high_frequency_1hr,
# MAGIC     indicator_high_frequency_24hr,
# MAGIC     indicator_multiple_countries,
# MAGIC     indicator_unusual_country,
# MAGIC     indicator_multiple_devices,
# MAGIC     indicator_unusual_device,
# MAGIC     indicator_unusual_hour,
# MAGIC
# MAGIC     -- Final risk score
# MAGIC     risk_score,
# MAGIC
# MAGIC     -- Risk classification
# MAGIC     CASE
# MAGIC         WHEN risk_score <= 30 THEN 'Low'
# MAGIC         WHEN risk_score <= 70 THEN 'Medium'
# MAGIC         ELSE 'High'
# MAGIC     END AS risk_level
# MAGIC
# MAGIC FROM risk_calculation;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SELECT
# MAGIC     COUNT(*) AS total_transactions,
# MAGIC     COUNT(CASE WHEN risk_level = 'High' THEN 1 END) AS high_risk,
# MAGIC     COUNT(CASE WHEN risk_level = 'Medium' THEN 1 END) AS medium_risk,
# MAGIC     COUNT(CASE WHEN risk_level = 'Low' THEN 1 END) AS low_risk
# MAGIC FROM workspace.default.fraud_detection_results;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SELECT
# MAGIC     transaction_id,
# MAGIC     user_id,
# MAGIC     amount,
# MAGIC     country,
# MAGIC     device,
# MAGIC     channel,
# MAGIC     hour,
# MAGIC     indicator_high_amount,
# MAGIC     indicator_extreme_amount,
# MAGIC     indicator_high_frequency_1hr,
# MAGIC     indicator_high_frequency_24hr,
# MAGIC     indicator_multiple_countries,
# MAGIC     indicator_unusual_country,
# MAGIC     indicator_multiple_devices,
# MAGIC     indicator_unusual_device,
# MAGIC     indicator_unusual_hour,
# MAGIC     risk_score,
# MAGIC     risk_level,
# MAGIC     is_fraud
# MAGIC FROM workspace.default.fraud_detection_results
# MAGIC ORDER BY risk_score DESC, transaction_id
# MAGIC LIMIT 20;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SELECT *
# MAGIC FROM workspace.default.fraud_detection_results
# MAGIC WHERE risk_level = 'High'
# MAGIC ORDER BY risk_score DESC;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SELECT
# MAGIC     risk_score,
# MAGIC     risk_level,
# MAGIC     COUNT(*) AS transaction_count,
# MAGIC     SUM(is_fraud) AS actual_fraud_count
# MAGIC FROM workspace.default.fraud_detection_results
# MAGIC GROUP BY risk_score, risk_level
# MAGIC ORDER BY risk_score DESC;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SELECT
# MAGIC     risk_level,
# MAGIC     COUNT(*) AS total_transactions,
# MAGIC     SUM(is_fraud) AS actual_fraud,
# MAGIC     ROUND(100.0 * SUM(is_fraud) / COUNT(*), 2) AS fraud_rate_percent
# MAGIC FROM workspace.default.fraud_detection_results
# MAGIC GROUP BY risk_level
# MAGIC ORDER BY
# MAGIC     CASE risk_level
# MAGIC         WHEN 'High' THEN 1
# MAGIC         WHEN 'Medium' THEN 2
# MAGIC         WHEN 'Low' THEN 3
# MAGIC     END;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM workspace.default.fraud_detection_results
# MAGIC LIMIT 10;
# MAGIC
