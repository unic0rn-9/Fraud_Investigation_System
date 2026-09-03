# Databricks notebook source
# ============================================================
# Fraud Investigation System — Dataset Inspection
# ============================================================
# Source: /Volumes/workspace/default/fraud_data/transactions.csv
# Goal: Read the CSV and inspect the data (no cleaning yet).
# ============================================================

from pyspark.sql.functions import col, count, when, isnull

CSV_PATH = "/Volumes/workspace/default/fraud_data/transactions.csv"

# 1. Read the CSV into a DataFrame
#    header=True   -> first row is column names
#    inferSchema=True -> automatically detect data types
df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(CSV_PATH)
)

# 2. Display the first 10 rows
print("=== First 10 rows ===")
display(df.limit(10))

# 3. Show the column names
print("=== Column names ===")
print(df.columns)

# 4. Show the number of rows and columns
num_rows = df.count()
num_cols = len(df.columns)
print(f"\n=== Shape ===")
print(f"Rows    : {num_rows}")
print(f"Columns : {num_cols}")

# 5. Display the data types (schema)
print("\n=== Schema (column name -> data type) ===")
df.printSchema()

# 6. Basic data-quality information
#    a) Null / missing value count per column
print("\n=== Null / missing values per column ===")
null_counts = df.select([
    count(when(isnull(c), c)).alias(c) for c in df.columns
])
display(null_counts)

#    b) Duplicate rows (entire-row duplicates)
total_rows = df.count()
distinct_rows = df.distinct().count()
duplicate_rows = total_rows - distinct_rows
print(f"\n=== Duplicate rows ===")
print(f"Total rows        : {total_rows}")
print(f"Distinct rows     : {distinct_rows}")
print(f"Duplicate rows     : {duplicate_rows}")

#    c) Summary statistics for numeric columns
print("\n=== Summary statistics (numeric columns) ===")
display(df.summary())


# COMMAND ----------

# ============================================================
# Fraud Investigation System — Data Dictionary & EDA
# ============================================================
# Source 1: /Volumes/workspace/default/fraud_data/data_dictionary.csv
# Source 2: /Volumes/workspace/default/fraud_data/transactions.csv  (already loaded as `df`)
# Goal: Understand the dataset before building fraud investigation agents.
# Rules : No modifications to either dataset; no tables created.
# ============================================================

from pyspark.sql.functions import col, count, when, isnull, round as spark_round

# ----------------------------------------------------------------
# 1. Read the data dictionary CSV
# ----------------------------------------------------------------
DATA_DICT_PATH = "/Volumes/workspace/default/fraud_data/data_dictionary.csv"

data_dict = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(DATA_DICT_PATH)
)

print("=== Data Dictionary: schema ===")
data_dict.printSchema()

print("=== Data Dictionary: contents ===")
display(data_dict)

# ----------------------------------------------------------------
# 2. Unique values & distributions for categorical columns in transactions.csv
# ----------------------------------------------------------------
categorical_cols = ["country", "device", "channel", "coupon_applied", "is_fraud"]

for c in categorical_cols:
    print(f"\n=== Unique values & distribution for '{c}' ===")
    value_dist = (
        df.groupBy(c)
        .count()
        .withColumn("percentage", spark_round(col("count") / df.count() * 100, 2))
        .orderBy(col("count").desc())
    )
    display(value_dist)

# ----------------------------------------------------------------
# 3. Descriptive statistics for numerical columns
# ----------------------------------------------------------------
numerical_cols = ["amount", "hour", "dayofweek", "num_items"]

print("\n=== Descriptive statistics (numerical columns) ===")
display(df.select(*numerical_cols).summary())

# ----------------------------------------------------------------
# 4. Overall fraud rate
# ----------------------------------------------------------------
total_txn      = df.count()
fraud_txn      = df.filter(col("is_fraud") == 1).count()
fraud_rate     = round(fraud_txn / total_txn * 100, 4)
legitimate_txn = total_txn - fraud_txn

print("\n=== Overall Fraud Rate ===")
print(f"Total transactions      : {total_txn}")
print(f"Fraudulent transactions : {fraud_txn}")
print(f"Legitimate transactions : {legitimate_txn}")
print(f"Fraud rate (%)          : {fraud_rate}%")


# COMMAND ----------

# ============================================================
# Fraud Investigation System — Create Investigation-Ready DataFrame
# ============================================================
# Input : df  (raw transactions DataFrame from Cell 1)
# Output: investigation_df  (typed, de-duplicated, investigation-ready)
# Rules :
#   - Keep ALL original columns
#   - Cast columns to proper types
#   - De-duplicate on transaction_id ONLY if duplicates exist
#   - Never drop or alter legitimate fraud records
#   - Do NOT overwrite the original df
#   - Do NOT create a permanent table
# ============================================================

from pyspark.sql.functions import col, count

# ----------------------------------------------------------------
# 1. Start from the original DataFrame (do not overwrite `df`)
# ----------------------------------------------------------------
investigation_df = df

# ----------------------------------------------------------------
# 2. Cast columns to proper data types
# ----------------------------------------------------------------
inferred = {f.name: f.dataType.simpleString() for f in df.schema.fields}
print("=== Inferred schema (before casting) ===")
for name, dtype in inferred.items():
    print(f"  {name:20s} -> {dtype}")

# timestamp -> timestamp type (try common formats; Spark auto-parse)
if "timestamp" in df.columns and inferred.get("timestamp") != "timestamp":
    investigation_df = investigation_df.withColumn(
        "timestamp", col("timestamp").cast("timestamp")
    )

# transaction_id, user_id -> integer (or long)
for c in ["transaction_id", "user_id"]:
    if c in df.columns and inferred.get(c) not in ("int", "bigint"):
        investigation_df = investigation_df.withColumn(c, col(c).cast("long"))

# amount -> double
if "amount" in df.columns and inferred.get("amount") != "double":
    investigation_df = investigation_df.withColumn("amount", col("amount").cast("double"))

# hour, dayofweek, coupon_applied, num_items -> integer
for c in ["hour", "dayofweek", "coupon_applied", "num_items"]:
    if c in df.columns and inferred.get(c) not in ("int", "bigint"):
        investigation_df = investigation_df.withColumn(c, col(c).cast("int"))

# country, device, channel -> string (ensure even if inferred differently)
for c in ["country", "device", "channel"]:
    if c in df.columns and inferred.get(c) != "string":
        investigation_df = investigation_df.withColumn(c, col(c).cast("string"))

# is_fraud -> integer (keep as-is if already int)
if "is_fraud" in df.columns and inferred.get("is_fraud") not in ("int", "bigint"):
    investigation_df = investigation_df.withColumn("is_fraud", col("is_fraud").cast("int"))

# ----------------------------------------------------------------
# 3. De-duplicate on transaction_id ONLY if duplicate IDs exist
#    (preserves every legitimate fraud record — drops only exact
#     transaction_id duplicates, keeping the first occurrence)
# ----------------------------------------------------------------
total_before = investigation_df.count()
dup_count = (
    investigation_df
    .groupBy("transaction_id")
 .agg(count("*").alias("cnt"))
    .filter(col("cnt") > 1)
    .count()
)

print(f"\n=== Duplicate transaction_id check ===")
print(f"Total rows before de-dup : {total_before}")
print(f"Duplicate transaction_ids: {dup_count}")

if dup_count > 0:
    investigation_df = investigation_df.dropDuplicates(["transaction_id"])
    print("Duplicates found — removed (kept first occurrence per transaction_id).")
else:
    print("No duplicate transaction_ids found — no rows removed.")

# ----------------------------------------------------------------
# 4. Cache so downstream agent cells don't recompute
# ----------------------------------------------------------------
investigation_df = investigation_df.cache()

# ----------------------------------------------------------------
# 5. Display results
# ----------------------------------------------------------------
print("\n=== investigation_df — first 10 rows ===")
display(investigation_df.limit(10))

print("\n=== investigation_df — schema ===")
investigation_df.printSchema()

final_count = investigation_df.count()
print(f"\n=== investigation_df — final row count ===")
print(f"Rows: {final_count}")

print(f"\n=== Original df is untouched (rows: {df.count()}) ===")


# COMMAND ----------

# ============================================================
# Fraud Investigation System — Create Investigation-Ready DataFrame
# ============================================================
# Input : df  (raw transactions DataFrame from Cell 1)
# Output: investigation_df  (typed, de-duplicated, investigation-ready)
# Rules :
#   - Keep ALL original columns
#   - Cast columns to proper types
#   - De-duplicate on transaction_id ONLY if duplicates exist
#   - Never drop or alter legitimate fraud records
#   - Do NOT overwrite the original df
#   - Do NOT create a permanent table
#   - No persist / cache / PERSIST TABLE (Serverless does not support it)
# ============================================================

from pyspark.sql.functions import col, count

# ----------------------------------------------------------------
# 1. Start from the original DataFrame (do not overwrite `df`)
# ----------------------------------------------------------------
investigation_df = df

# ----------------------------------------------------------------
# 2. Cast columns to proper data types
# ----------------------------------------------------------------
inferred = {f.name: f.dataType.simpleString() for f in df.schema.fields}
print("=== Inferred schema (before casting) ===")
for name, dtype in inferred.items():
    print(f"  {name:20s} -> {dtype}")

# timestamp -> timestamp type (try common formats; Spark auto-parse)
if "timestamp" in df.columns and inferred.get("timestamp") != "timestamp":
    investigation_df = investigation_df.withColumn(
        "timestamp", col("timestamp").cast("timestamp")
    )

# transaction_id, user_id -> integer (or long)
for c in ["transaction_id", "user_id"]:
    if c in df.columns and inferred.get(c) not in ("int", "bigint"):
        investigation_df = investigation_df.withColumn(c, col(c).cast("long"))

# amount -> double
if "amount" in df.columns and inferred.get("amount") != "double":
    investigation_df = investigation_df.withColumn("amount", col("amount").cast("double"))

# hour, dayofweek, coupon_applied, num_items -> integer
for c in ["hour", "dayofweek", "coupon_applied", "num_items"]:
    if c in df.columns and inferred.get(c) not in ("int", "bigint"):
        investigation_df = investigation_df.withColumn(c, col(c).cast("int"))

# country, device, channel -> string (ensure even if inferred differently)
for c in ["country", "device", "channel"]:
    if c in df.columns and inferred.get(c) != "string":
        investigation_df = investigation_df.withColumn(c, col(c).cast("string"))

# is_fraud -> integer (keep as-is if already int)
if "is_fraud" in df.columns and inferred.get("is_fraud") not in ("int", "bigint"):
    investigation_df = investigation_df.withColumn("is_fraud", col("is_fraud").cast("int"))

# ----------------------------------------------------------------
# 3. De-duplicate on transaction_id ONLY if duplicate IDs exist
#    (preserves every legitimate fraud record — drops only exact
#     transaction_id duplicates, keeping the first occurrence)
# ----------------------------------------------------------------
total_before = investigation_df.count()
dup_count = (
    investigation_df
    .groupBy("transaction_id")
    .agg(count("*").alias("cnt"))
    .filter(col("cnt") > 1)
    .count()
)

print(f"\n=== Duplicate transaction_id check ===")
print(f"Total rows before de-dup : {total_before}")
print(f"Duplicate transaction_ids: {dup_count}")

if dup_count > 0:
    investigation_df = investigation_df.dropDuplicates(["transaction_id"])
    print("Duplicates found — removed (kept first occurrence per transaction_id).")
else:
    print("No duplicate transaction_ids found — no rows removed.")

# ----------------------------------------------------------------
# 4. No caching on Serverless compute
#    (persist / cache / PERSIST TABLE are not supported on Serverless)
# ----------------------------------------------------------------
# investigation_df is ready as-is; downstream cells can recompute as needed.

# ----------------------------------------------------------------
# 5. Display results
# ----------------------------------------------------------------
print("\n=== investigation_df — first 10 rows ===")
display(investigation_df.limit(10))

print("\n=== investigation_df — schema ===")
investigation_df.printSchema()

final_count = investigation_df.count()
print(f"\n=== investigation_df — final row count ===")
print(f"Rows: {final_count}")

print(f"\n=== Original df is untouched (rows: {df.count()}) ===")


# COMMAND ----------



# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN workspace.default;
