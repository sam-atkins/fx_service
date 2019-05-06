from src.app import app
from manageconf import Config, get_config  # noqa F401


DEBUG = get_config("DEBUG")

if __name__ == "__main__":
    app.run(debug=DEBUG, host="0.0.0.0", port=3002)
