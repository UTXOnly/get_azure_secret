#!/usr/bin/env python3
import json
import sys
import requests
import logging
from datetime import datetime
import os

# Configuration
VAULT_URI = "https://brian-hartford-key-vault.vault.azure.net"
API_VERSION = "7.3"

# Setup logging
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = os.path.join(log_directory, f"azure_secrets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

def get_managed_identity_token(resource="https://vault.azure.net"):
    """Fetch an access token from Azure Managed Identity endpoint."""
    try:
        logger.debug("Attempting to fetch managed identity token")
        token_url = "http://169.254.169.254/metadata/identity/oauth2/token"
        params = {
            "api-version": "2018-02-01",
            "resource": resource
        }
        headers = {
            "Metadata": "true"
        }
        response = requests.get(token_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info("Successfully obtained managed identity token")
        return response.json()["access_token"]
    except Exception as e:
        logger.error(f"Failed to get access token from Managed Identity: {e}")
        sys.exit(1)

def fetch_secret_from_azure(token, secret_name):
    """Retrieve a secret from Azure Key Vault using the provided token."""
    try:
        logger.debug(f"Attempting to fetch secret: {secret_name}")
        url = f"{VAULT_URI}/secrets/{secret_name}?api-version={API_VERSION}"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logger.info(f"Successfully retrieved secret: {secret_name}")
        return response.json()["value"]
    except Exception as e:
        logger.error(f"Failed to retrieve secret {secret_name}: {e}")
        return None

def retrieve_secrets():
    try:
        logger.debug("Starting secrets retrieval process")
        secret_request = json.load(sys.stdin)
        logger.debug(f"Received request for secrets: {secret_request['secrets']}")
        
        token = get_managed_identity_token()
        secret_response = {}
        
        for secret in secret_request["secrets"]:
            secret_value = fetch_secret_from_azure(token, secret)
            if secret_value is not None:
                secret_response[secret] = {
                    "value": str(secret_value),
                    "error": None
                }
                logger.debug(f"Successfully processed secret: {secret}")
            else:
                secret_response[secret] = {
                    "value": None,
                    "error": "Unable to retrieve secret."
                }
                logger.warning(f"Failed to process secret: {secret}")
                
    except Exception as e:
        logger.error(f"There was an error retrieving secrets: {e}")
        sys.exit(1)
        
    sys.stdin.close()
    logger.info("Completed secrets retrieval process")
    return secret_response

if __name__ == "__main__":
    try:
        logger.info("Starting secret retrieval script")
        secrets = retrieve_secrets()
        print(json.dumps(secrets))
        logger.info("Script completed successfully")
    except Exception as e:
        logger.error(f"Script failed with error: {e}")
        sys.exit(1)
