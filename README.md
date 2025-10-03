# Crypto ETL Pipeline (AWS)

This project is my ongoing journey into data engineering.  
So far, I’ve set up a local ETL pipeline that:

- Extracts cryptocurrency transaction data from CSV files stored in the `data/` folder.
- Cleans and transforms the data using Python (Pandas).
- Prepares the data for loading into AWS S3.

## Project Structure

crypto-etl/
│── data/ # Raw CSVs (local)
│── scripts/ # ETL scripts (local batch processing)
│ └── etl_local.py # Reads CSV, applies basic transforms
│── venv/ # Virtual environment (not committed)
│── README.md # Project overview
│── .gitignore # Git ignore rules


## Next Step
Connect the pipeline to AWS (S3, Glue, Lambda).
