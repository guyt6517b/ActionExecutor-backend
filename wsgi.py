from app import app

# This exposes the Flask app to Render's WSGI server
application = app

# Optional: if you want to run standalone:
if __name__ == "__main__":
    application.run()
