# =============================================================================
# 00_LoadReferenceData
#
# Fabric IQ workshop -- Module 01/02 supporting notebook.
#
# Loads the three cold-chain reference CSVs (Stores, Freezers, Customers)
# from this Lakehouse's Files section into three managed Delta tables of the
# same names. This is the "static/contextual data" half of the RTI +
# ontology pattern this workshop follows: live freezer telemetry streams in
# via FreezerTelemetryEventstream (see artifacts/Eventstream/), while the
# slower-changing "who/where/what" reference data lands here, in the
# Lakehouse, where a Fabric IQ ontology (built live in Module 03) can bind to
# it as entity properties.
#
# PREREQUISITES (see ../Notebooks/HOW-TO-EXPORT.md for full steps):
#   1. This notebook must have ColdChainLakehouse attached as its default
#      Lakehouse (so relative "Files/..." paths resolve correctly).
#   2. The three CSVs must already be uploaded to:
#        Files/SampleData/stores.csv
#        Files/SampleData/freezers.csv
#        Files/SampleData/customers.csv
#
# RUNNING THIS NOTEBOOK:
#   Paste this file's contents into a Fabric notebook cell (or split at the
#   "# %%" markers below into separate cells for a more granular live demo)
#   and select "Run all". On success, three Delta tables appear under this
#   Lakehouse's Tables section: Customers, Stores, Freezers.
# =============================================================================

# %%
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DateType,
)

# Base path for the reference CSVs, relative to the attached default
# Lakehouse's Files section. If you prefer an absolute OneLake path instead
# (e.g. when running this notebook without a default Lakehouse attached),
# replace this with:
#   abfss://<workspace-id>@onelake.dfs.fabric.microsoft.com/<lakehouse-id>/Files/SampleData
SAMPLE_DATA_PATH = "Files/SampleData"


# %%
def load_csv(file_name: str, schema: StructType):
    """Read one reference CSV from the Lakehouse Files section with an
    explicit schema (safer than schema inference for a workshop -- it fails
    loudly and immediately if a column is missing or misnamed, rather than
    silently inferring the wrong type)."""
    path = f"{SAMPLE_DATA_PATH}/{file_name}"
    return (
        spark.read.option("header", True)
        .schema(schema)
        .csv(path)
    )


# %%
# --- Stores -------------------------------------------------------------
# StoreId, StoreName, Region, City
stores_schema = StructType(
    [
        StructField("StoreId", StringType(), nullable=False),
        StructField("StoreName", StringType(), nullable=False),
        StructField("Region", StringType(), nullable=False),
        StructField("City", StringType(), nullable=False),
    ]
)

stores_df = load_csv("stores.csv", stores_schema)

(
    stores_df.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("Stores")
)

print(f"Stores loaded: {stores_df.count()} rows")
display(stores_df)


# %%
# --- Freezers -------------------------------------------------------------
# FreezerId, StoreId, Model, Capacity, InstallDate
freezers_schema = StructType(
    [
        StructField("FreezerId", StringType(), nullable=False),
        StructField("StoreId", StringType(), nullable=False),
        StructField("Model", StringType(), nullable=False),
        StructField("Capacity", IntegerType(), nullable=False),
        StructField("InstallDate", DateType(), nullable=False),
    ]
)

freezers_df = load_csv("freezers.csv", freezers_schema)

(
    freezers_df.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("Freezers")
)

print(f"Freezers loaded: {freezers_df.count()} rows")
display(freezers_df)


# %%
# --- Customers -------------------------------------------------------------
# CustomerId, Name, HomeStoreId, LoyaltyTier
customers_schema = StructType(
    [
        StructField("CustomerId", StringType(), nullable=False),
        StructField("Name", StringType(), nullable=False),
        StructField("HomeStoreId", StringType(), nullable=False),
        StructField("LoyaltyTier", StringType(), nullable=False),
    ]
)

customers_df = load_csv("customers.csv", customers_schema)

(
    customers_df.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("Customers")
)

print(f"Customers loaded: {customers_df.count()} rows")
display(customers_df)


# %%
# --- Verification -----------------------------------------------------------
# Quick sanity check: join Freezers -> Stores to confirm referential
# integrity of the reference data before attendees move on to Module 02's
# streaming-enrichment lab (which mirrors this same join, but in KQL, over
# live telemetry -- see artifacts/Eventhouse/ColdChainKQLDB.kql).
verification_df = freezers_df.join(stores_df, on="StoreId", how="left").select(
    "FreezerId", "Model", "Capacity", "StoreId", "StoreName", "Region", "City"
)

print("Freezers joined to Stores (spot-check -- every row should have a StoreName):")
display(verification_df.orderBy("FreezerId"))

unmatched = verification_df.filter(F.col("StoreName").isNull()).count()
if unmatched > 0:
    raise ValueError(
        f"{unmatched} freezer(s) reference a StoreId not present in stores.csv. "
        "Check artifacts/SampleData/freezers.csv and stores.csv for a typo."
    )

print("00_LoadReferenceData completed successfully: Stores, Freezers, Customers tables are ready.")
