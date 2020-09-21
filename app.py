import dotenv
import api
import os, ssl

def create_app():
    dotenv.load_dotenv()
    app = api.AgayaApi()
    return app

if __name__ == "__main__":
    app = create_app()
    debug = bool(os.getenv("DEBUG"))
    port = os.getenv("PORT") or 4700

    if os.getenv("HTTPS") == "true":
        ssl_contxt = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ssl_contxt.load_cert_chain(certfile=os.getenv("CERT"), keyfile=os.getenv("KEY"))

        app.run(port=port, debug=debug, ssl_context=ssl_contxt)
    else:
        app.run(port=port, debug=debug)

