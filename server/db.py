from cs50 import SQL
import os

# Configure CS50 Library to use SQLite database (for local testing)
db = SQL("sqlite:///cs50Final.db")

# Configure CS50 Library to use Heroku Postgres if on prod
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://")
    db = SQL(uri)
