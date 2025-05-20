#!/usr/bin/env python3

import requests
import sys

# Configuration
vault_uri = "https://brian-hartford-key-vault.vault.azure.net"
secret_name = "brian-hartford-secret"
api_version = "7.3"

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
        print(f"Failed to get access token from Managed Identity:\n{e}")
        sys.exit(1)

def get_secret(token):
    """Retrieve a secret from Azure Key Vault using the provided token."""
    try:
        url = f"{vault_uri}/secrets/{secret_name}?api-version={api_version}"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        secret = response.json()
        print("Secret retrieved successfully:")
        print(secret["value"])
    except Exception as e:
        print(f"Failed to retrieve secret:\n{e}")
        print(f"Response: {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    token = get_managed_identity_token()
    get_secret(token)
