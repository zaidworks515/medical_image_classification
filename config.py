from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

env = load_dotenv()

port = os.getenv("PORT")
server_ip = os.getenv("SERVER_IP")
HOST = os.getenv("HOST")
USER = "root"
# PASSWORD = os.getenv("PASSWORD")
PASSWORD = quote_plus(
    os.getenv("PASSWORD")
)  # Handles special characters like @, :, etc.
DATABASE = os.getenv("DATABASE")

print("Connecting with:", USER, PASSWORD, HOST, DATABASE)


class Config:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
