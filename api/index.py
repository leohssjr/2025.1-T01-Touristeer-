import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from vercel_wsgi import handle_request

from src.models.user import db
from src.routes.user_routes import user_bp
from src.routes.routes import routes_bp
from src.routes.tourist_spots import tourist_spots_bp
from src.routes.pdf_export import pdf_export_bp
from src.routes.notifications import notifications_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

CORS(app)

# Registrar Blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(routes_bp, url_prefix='/api')
app.register_blueprint(tourist_spots_bp, url_prefix='/api')
app.register_blueprint(pdf_export_bp, url_prefix='/api')
app.register_blueprint(notifications_bp, url_prefix='/api')

# Configurar banco de dados
database_dir = os.path.join(os.path.dirname(__file__), '..', 'database')
os.makedirs(database_dir, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(database_dir, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    from src.models.route import Route
    from src.models.tourist_spot import TouristSpot
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path == 'tourist_spots.json':
        return send_from_directory(os.path.dirname(__file__), '..', 'tourist_spots.json')

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# Função que o Vercel chama
def handler(event, context):
    return handle_request(app, event, context)
