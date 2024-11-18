from hexbytes import HexBytes
from dotenv import load_dotenv
import json
import csv
import os

load_dotenv()

def get_api_key(key):
    return os.getenv(key)

def load_transaction_receipts(filename):
    print("Opening file " + filename)

    with open(filename, 'r') as f:
        return json.load(f)

def extract_block_data_to_dict(filename):
    print(f"Extracting blocks data from {filename}...")
    block_data = {}
    with open(filename, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            block_data[int(row['block_number'])] = row['timestamp']
    return block_data

def convert_hex_to_int(hex_value):
    return int(hex_value, 16)

def get_token_mapping(col_search, col_retrieve, token_address, token_mappings):
    # in the form [SOURCE_CHAIN_ID, TARGET_CHAIN_ID, TOKEN_ADDRESS_SOURCE_CHAIN, TOKEN_ADDRESS_TARGET_CHAIN, STANDARD]

    for mapping in token_mappings:
        if mapping[col_search] == token_address:
            return mapping[col_retrieve]
 
    return None

def convert_topics_to_hex(log):
    hex_topics = []
    for topic in log['topics']:
        hex_topics.append(HexBytes(topic))
    
    log['topics'] = hex_topics
    return log

def confirm_api_keys_loaded():
    ethereum = get_api_key('ETHEREUM_API_KEY')
    ronin = get_api_key('RONIN_CHAIN_API_KEY')
    moonbeam = get_api_key('MOONBEAM_API_KEY')

    if ethereum == "" or ronin == "" or moonbeam == "":
        raise Exception("API keys not found in .env file")