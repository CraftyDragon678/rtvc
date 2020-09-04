import dotenv
import api
import os, ssl

if __name__ == "__main__":
    dotenv.load_dotenv()

    app = api.AgayaApi()
    debug = bool(os.getenv("DEBUG"))

    if os.getenv("HTTPS") == "true":
        ssl_contxt = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ssl_contxt.load_cert_chain(certfile=os.getenv("CERT"), keyfile=os.getenv("KEY"))

        app.run('0.0.0.0', debug=debug, ssl_context=ssl_contxt)
    else:
        app.run('0.0.0.0', debug=debug)

