from flask import request
from datetime import datetime
from server.utils.logger import logger  
from server.routers.globalAgent import registerGlobalAgentRoutes

def registerRoutes(app, path):
    # Optional: Request timing
    @app.before_request
    def before_request():
        request.start_time = datetime.now()

    @app.after_request
    def after_request(response):
        if hasattr(request, 'start_time'):
            duration = datetime.now() - request.start_time
            logger.info(f"Done in {duration.total_seconds():.2f}s - {response.status_code}")
        return response

    # Register your global agent routes
    registerGlobalAgentRoutes(app, prefix=f"{path}/globalAgent")
