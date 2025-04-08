from flask import jsonify

def registerGlobalAgentRoutes(app, prefix):
    
    @app.route(f"{prefix}/")
    def askQuestion():
        return jsonify({"message": "Welcome to the simplified API!"})
