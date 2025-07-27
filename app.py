from app import create_app
from app.models import db
from flask_cors import CORS

app = create_app('DevelopmentConfig')
CORS(app, origins=["http://localhost:5173"])
with app.app_context():
    # db.drop_all()
    
    # tables_to_drop = [table for table in db.metadata.sorted_tables if table.name != 'users']
    # for table in tables_to_drop:
    #     table.drop(db.engine)
    # db.metadata.tables['discounts'].drop(db.engine)
    db.create_all()

app.run()
    
