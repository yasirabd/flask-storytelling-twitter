from app import create_app, db
from app.models import Crawler, Tweet, Preprocess

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Crawler': Crawler, 'Tweet': Tweet, 'Preprocess': Preprocess}

# if __name__ == "__main__":
#     app.run(debug=True, use_reloader=True)
