from flask import Flask
from flask_migrate import Migrate
from models import db
import config

# Import Blueprints
from routes.points import points_bp
from routes.polygons import polygons_bp


def create_app():
    """
    Application factory for the Spatial API
    """
    app = Flask(__name__)
    app.config.from_object(config.Config)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    # Register API blueprints
    app.register_blueprint(points_bp)
    app.register_blueprint(polygons_bp)

    # Optional root route
    @app.route('/')
    def index():
        return {'message': 'Spatial API is up and running'}

    return app


if __name__ == '__main__':
    # Create and run the app
    application = create_app()
    application.run(host='0.0.0.0', port=5000, debug=True)