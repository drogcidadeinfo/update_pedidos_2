import os
import glob
import gspread
import json
import time
import re
import logging
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

# config logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_latest_file(extension='csv', directory='.'):
    # Get the most recently modified file with a given extension.
    files = glob.glob(os.path.join(directory, f'*.{extension}'))
    if not files:
        logging.warning("No files found with the specified extension.")
        return None
    return max(files, key=os.path.getmtime)

def retry_api_call(func, retries=3, delay=2):
    for i in range(retries):
        try:
            return func()
        except HttpError as error:
            if hasattr(error, "resp") and error.resp.status == 500:
                logging.warning(f"APIError 500 encountered. Retrying {i + 1}/{retries}...")
                time.sleep(delay)
            else:
                raise
    raise Exception("Max retries reached.")


def update_worksheet(df, sheet_id, worksheet_name, client):
    df = df.fillna("")
    rows = [df.columns.tolist()] + df.values.tolist()

    try:
        sheet = client.open_by_key(sheet_id).worksheet(worksheet_name)
    except Exception as e:
        logging.error(f"Error accessing '{worksheet_name}' worksheet: {e}")
        return

    logging.info(f"Clearing worksheet '{worksheet_name}'...")
    sheet.clear()

    logging.info(f"Updating worksheet '{worksheet_name}'...")
    sheet.update(rows)

    logging.info(f"Worksheet '{worksheet_name}' updated successfully.")
    
def update_google_sheet(df, sheet_id):
    logging.info("Loading Google credentials...")

    creds_env = os.getenv("GSA_CREDENTIALS")
    scope = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]

    creds = Credentials.from_service_account_info(json.loads(creds_env), scopes=scope)
    client = gspread.authorize(creds)

    update_worksheet(df, sheet_id, "APP", client)

def main():
    # Get the latest CSV file
    csv_file = get_latest_file('csv')
    
    if csv_file is None:
        logging.error("No CSV file found in the directory.")
        return
    
    logging.info(f"Found CSV file: {csv_file}")
    
    # Read CSV file with correct delimiter
    try:
        df = pd.read_csv(
            csv_file,
            delimiter=';',           # Semicolon delimiter
            encoding='utf-8',        # UTF-8 encoding
            decimal=',',             # Decimal comma (for numbers like "59,90")
            quotechar='"',           # Quoted fields with double quotes
            thousands='.',           # Thousands separator (like in CPF: 000.00.00-00)
            dtype=str                # Read all as string to preserve formatting
        )
        logging.info(f"CSV file loaded successfully. Shape: {df.shape}")
        
        # Show column names to verify
        logging.info(f"Columns found: {df.columns.tolist()}")
        logging.info(f"Sample data (first 3 rows):")
        print(df.head(3))
        
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        return
    
    # Your Google Sheet ID
    sheet_id = os.getenv("sheet_id") # Replace with your actual Google Sheet ID
    
    # Update Google Sheet
    update_google_sheet(df, sheet_id)

if __name__ == "__main__":
    main()
