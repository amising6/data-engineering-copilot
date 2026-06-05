from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, lower, regexp_replace, when, to_utc_timestamp

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Data Transformation") \
    .getOrCreate()

# Load source data
src_users_df = spark.read.format("parquet").load("path_to_src_users")

# Transformation logic
dim_customers_df = src_users_df.select(
    col("user_id").alias("customer_id"),
    # Cleaned phone number: strip whitespace, remove hyphens, add +1 prefix if missing
    when(
        col("raw_phone").rlike("^\+1"), 
        regexp_replace(trim(col("raw_phone")), "-", "")
    ).otherwise(
        regexp_replace(concat(lit("+1"), trim(col("raw_phone"))), "-", "")
    ).alias("cleaned_phone"),
    # Convert email to lowercase and trim spaces
    trim(lower(col("email_address"))).alias("primary_email"),
    # Convert signup timestamp from EST to UTC
    to_utc_timestamp(col("signup_timestamp"), "EST").alias("account_created_dt"),
    # Map account status to boolean flag
    when(col("account_status_id") == 1, True).otherwise(False).alias("is_active_flag")
)

# Write the transformed data to the target table
dim_customers_df.write.format("parquet").mode("overwrite").save("path_to_dim_customers")