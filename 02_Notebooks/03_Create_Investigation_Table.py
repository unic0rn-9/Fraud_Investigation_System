# Databricks notebook source
# MAGIC %sql
# MAGIC
# MAGIC SELECT *
# MAGIC FROM workspace.default.fraud_detection_results
# MAGIC LIMIT 20;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     COUNT(*) AS total_transactions,
# MAGIC     SUM(CASE WHEN risk_score >= 70 THEN 1 ELSE 0 END) AS high_risk_transactions,
# MAGIC     ROUND(
# MAGIC         100.0 * SUM(CASE WHEN risk_score >= 70 THEN 1 ELSE 0 END) / COUNT(*),
# MAGIC         2
# MAGIC     ) AS high_risk_percentage,
# MAGIC     ROUND(SUM(amount), 2) AS total_transaction_amount,
# MAGIC     ROUND(
# MAGIC         SUM(CASE WHEN risk_score >= 70 THEN amount ELSE 0 END),
# MAGIC         2
# MAGIC     ) AS high_risk_amount
# MAGIC FROM workspace.default.fraud_detection_results;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     CASE
# MAGIC         WHEN risk_score >= 70 THEN 'High Risk'
# MAGIC         WHEN risk_score >= 40 THEN 'Medium Risk'
# MAGIC         ELSE 'Low Risk'
# MAGIC     END AS risk_level,
# MAGIC     COUNT(*) AS transaction_count
# MAGIC FROM workspace.default.fraud_detection_results
# MAGIC GROUP BY
# MAGIC     CASE
# MAGIC         WHEN risk_score >= 70 THEN 'High Risk'
# MAGIC         WHEN risk_score >= 40 THEN 'Medium Risk'
# MAGIC         ELSE 'Low Risk'
# MAGIC     END
# MAGIC ORDER BY transaction_count DESC;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     device,
# MAGIC     SUM(is_fraud) AS fraud_transactions,
# MAGIC     COUNT(*) AS total_transactions
# MAGIC FROM workspace.default.fraud_detection_results
# MAGIC GROUP BY device
# MAGIC ORDER BY fraud_transactions DESC;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     country,
# MAGIC     SUM(is_fraud) AS fraud_transactions,
# MAGIC     COUNT(*) AS total_transactions
# MAGIC FROM workspace.default.fraud_detection_results
# MAGIC GROUP BY country
# MAGIC ORDER BY fraud_transactions DESC;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SELECT
# MAGIC     transaction_id,
# MAGIC     user_id,
# MAGIC     timestamp,
# MAGIC     amount,
# MAGIC     country,
# MAGIC     device,
# MAGIC     channel,
# MAGIC     risk_score,
# MAGIC     is_fraud
# MAGIC FROM workspace.default.fraud_detection_results
# MAGIC WHERE risk_score >= 70
# MAGIC ORDER BY risk_score DESC, amount DESC
# MAGIC LIMIT 100;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     channel,
# MAGIC     SUM(is_fraud) AS fraud_transactions,
# MAGIC     COUNT(*) AS total_transactions
# MAGIC FROM workspace.default.fraud_detection_results
# MAGIC GROUP BY channel
# MAGIC ORDER BY fraud_transactions DESC;
