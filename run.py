"Run file"

from main import app

if __name__ == "__main__":
    app.run(port = 3399, debug=True, host = '0.0.0.0')
