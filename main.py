from app.logging import setup_logging
from app import setup_app


setup_logging()

app = setup_app()
