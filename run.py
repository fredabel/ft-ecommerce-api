from app import create_app
from app.models import db
from flask import redirect
from flask_cors import CORS

app = create_app('ProductionConfig')
CORS(
    app,
    resources={r"/*": {"origins": [
        "https://ft-store.up.railway.app",
        "http://localhost:5173"
    ]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)
@app.route('/', methods=['GET'])
def index():
    return redirect('/api/docs')

with app.app_context():
    # db.drop_all()
    db.create_all()

    
