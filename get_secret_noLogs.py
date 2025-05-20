#!/usr/bin/env python3
import json
import sys
import requests

# Configuration
VAULT_URI = "https://brian-hartford-key-vault.vault.azure.net"
API_VERSION = "7.3"

def get_managed_identity_token(resource="https://vault.azure.net"):
    """Fetch an access token from Azure Managed Identity endpoint."""
    try:
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
        return response.json()["access_token"]
    except Exception as e:
        sys.exit(1)

def fetch_secret_from_azure(token, secret_name):
    """Retrieve a secret from Azure Key Vault using the provided token."""
    try:
        url = f"{VAULT_URI}/secrets/{secret_name}?api-version={API_VERSION}"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["value"]
    except Exception:
        return None

def retrieve_secrets():
    try:
        secret_request = json.load(sys.stdin)
        token = get_managed_identity_token()
        secret_response = {}
        
        for secret in secret_request["secrets"]:
            secret_value = fetch_secret_from_azure(token, secret)
            if secret_value is not None:
                secret_response[secret] = {
                    "value": str(secret_value),
                    "error": None
                }
            else:
                secret_response[secret] = {
                    "value": None,
                    "error": "Unable to retrieve secret."
                }
                
    except Exception:
        sys.exit(1)
        
    sys.stdin.close()
    return secret_response

if __name__ == "__main__":
    secrets = retrieve_secrets()
    print(json.dumps(secrets))
