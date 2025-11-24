import os
import requests

def check_environment_variables():
    """Check for required environment variables."""
    required_vars = ['OPENAI_API_KEY', 'TELEGRAM_BOT_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Missing environment variables:", missing_vars)
    else:
        print("All required environment variables are set.")

def check_openai_api():
    """Check OpenAI API connectivity."""
    try:
        response = requests.post("https://api.openai.com/v1/models", headers={
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
        })
        response.raise_for_status()  # Raise an error for bad responses
        print("OpenAI API connectivity is successful.")
    except requests.RequestException as e:
        print("OpenAI API connectivity failed:", e)

def check_telegram_bot_api():
    """Check Telegram Bot API connectivity."""
    try:
        response = requests.get(f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/getMe")
        response.raise_for_status()  # Raise an error for bad responses
        print("Telegram Bot API connectivity is successful.")
    except requests.RequestException as e:
        print("Telegram Bot API connectivity failed:", e)

def verify_repository_files():
    """Verify essential files in the repository."""
    expected_files = ['README.md', 'requirements.txt', 'main.py']
    for filename in expected_files:
        if os.path.isfile(filename):
            print(f"{filename} exists in the repository.")
        else:
            print(f"{filename} does not exist in the repository.")

if __name__ == "__main__":
    print("Running diagnostic tests...")
    check_environment_variables()
    check_openai_api()
    check_telegram_bot_api()
    verify_repository_files()
    print("Diagnostic tests completed.")
