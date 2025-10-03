# Crypto ETL Pipeline (AWS)

This project is my ongoing journey into data engineering.  
So far, I’ve set up a local ETL pipeline that:

- Extracts cryptocurrency transaction data from CSV files stored in the `data/` folder.
- Cleans and transforms the data using Python (Pandas).
- Prepares the data for loading into AWS S3.

## Project Structure

crypto-etl/
├── crypto_etl/ # reusable Python modules
├── scripts/ # runnable scripts
│ └── etl_local.py
├── data/ # raw CSV files (ignored in git)
├── venv/ # virtual environment
├── README.md
└── .gitignore


## Next Step
Connect the pipeline to AWS (S3, Glue, Lambda).
