from dotenv import load_dotenv
import os

env = load_dotenv()

port = os.getenv('PORT')
server_ip = os.getenv('SERVER_IP')

