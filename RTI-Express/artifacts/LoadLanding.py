# LoadLanding
#
# RTI Express, Lab 05. Loads every CSV in the default Lakehouse's Files/landing/
# folder into a managed Delta table named after the file (rebalancing_crews.csv
# becomes table rebalancing_crews).
#
# Designed to be run by an Activator rule that fires on the OneLake
# Microsoft.Fabric.OneLake.FileCreated event for that folder, so it:
#   - exits cleanly when the folder is empty, so the manual validation run in
#     Lab 05 Part A succeeds before any file exists;
#   - overwrites each table on every run (idempotent; re-uploading a file is a
#     "replace" that raises FileCreated again).
#
# Requires BikeLakehouse attached as the notebook's default lakehouse.

import re

LANDING_PATH = "Files/landing"

try:
    entries = notebookutils.fs.ls(LANDING_PATH)  # type: ignore[name-defined]
except Exception as exc:  # folder missing, or no default lakehouse attached
    print(f"Could not list {LANDING_PATH}: {exc}")
    print("Attach BikeLakehouse as the default lakehouse and make sure Files/landing exists.")
    raise

csv_files = [e for e in entries if e.name.lower().endswith(".csv")]

if not csv_files:
    print(f"No CSV files in {LANDING_PATH} yet; nothing to load.")
else:
    for entry in csv_files:
        table = re.sub(r"[^0-9a-zA-Z_]", "_", entry.name[:-4]).lower()
        df = (
            spark.read.option("header", True)  # type: ignore[name-defined]
            .option("inferSchema", True)
            .csv(entry.path)
        )
        (
            df.write.format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable(table)
        )
        print(f"Loaded {df.count()} rows from {entry.name} into table {table}.")
        display(spark.table(table))  # type: ignore[name-defined]
