import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# URLs
BASE_URL = "https://www.fnguide.com"
LOGIN_URL = f"{BASE_URL}/home/login"
ITEM_DETAIL_URL = f"{BASE_URL}/Fgdc/ItemDetail"

# Credentials
USERNAME = os.getenv("FNGUIDE_USERNAME")
PASSWORD = os.getenv("FNGUIDE_PASSWORD")

# CSS Selectors
SELECTORS = {
    # 로그인 폼 관련 선택자
    'login': {
        'id_field': "#txtID",
        'pw_field': "#txtPW",
        'submit_button': "#divLogin > div.lay--popFooter > form > button.btn--back",
        'success_check': ".user-profile, .welcome-message",
        'search_button': "#divAutoComp > div.result > ul > li > button"
    }
}

# Selenium Settings
WEBDRIVER_TIMEOUT = 30  # seconds
IMPLICIT_WAIT = 10  # seconds

# Request Settings
REQUEST_TIMEOUT = 30  # seconds
REQUEST_DELAY = 2  # seconds between requests

# File Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True) 