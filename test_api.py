import requests


def is_api_key_valid(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get("https://api.openai.com/v1/models", headers=headers)

    if response.status_code == 200:
        return True
    else:
        return False
