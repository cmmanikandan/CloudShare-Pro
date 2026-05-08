import os
from dotenv import load_dotenv
from app import create_app
from app.services.telegram_bot import get_telegram_service

# Load environment variables
load_dotenv()

def start_bot():
    app = create_app()
    with app.app_context():
        service = get_telegram_service()
        if service and service.token:
            print("--- CloudShare Pro Bot Starting ---")
            service.run_bot()
        else:
            print("ERROR: TELEGRAM_BOT_TOKEN not found in environment.")

if __name__ == "__main__":
    start_bot()
