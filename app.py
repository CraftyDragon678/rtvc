import dotenv
import api
import db

if __name__ == "__main__":
    dotenv.load_dotenv()

    db.AgayaDBClient()
    app = api.AgayaApi()
    app.run('0.0.0.0', debug=True)

