import dotenv
import api

if __name__ == "__main__":
    dotenv.load_dotenv()
    app = api.AgayaApi()
    app.run('0.0.0.0', debug=True)

