from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import utils


app = Flask(__name__, static_folder='.')

# Enable CORS for all routes - this is crucial for browser requests
CORS(app)

# Alternative: Enable CORS only for specific routes
# CORS(app, resources={r"/process-coordinates": {"origins": "*"}})


@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route("/process-coordinates", methods=["POST"])
def process_coordinates():
    
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        lat = data.get("lat")
        lng = data.get("lng")
        
        # Validate coordinates
        if lat is None or lng is None:
            return jsonify({"error": "Missing lat or lng coordinates"}), 400
        
        # Validate coordinate ranges
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return jsonify({"error": "Invalid coordinate values"}), 400
        
        # Your Python logic here
        result = f"Received: lat={lat}, lng={lng}"
        print('Processing coordinates...')
        print(result)
        
        # Get scores using your utils function
        try:
            scores = utils.get_all_scores(lat, lng)
            print("Scores:", scores)
            
            # Return both the message and the scores
            return jsonify({
                "message": result,
                "coordinates": {"lat": lat, "lng": lng},
                "scores": scores,
                "status": "success"
            })
            
        except Exception as utils_error:
            print(f"Error in utils.get_all_scores: {utils_error}")
            import traceback
            traceback.print_exc()  # Print full error traceback
            return jsonify({
                "message": result,
                "coordinates": {"lat": lat, "lng": lng},
                "error": f"Error calculating scores: {str(utils_error)}",
                "status": "partial_success"
            }), 200  # Changed from 500 to 200
    
    except Exception as e:
        print(f"Error processing coordinates: {e}")
        import traceback
        traceback.print_exc()  # Print full error traceback
        return jsonify({
            "error": f"Server error: {str(e)}",
            "status": "error"
        }), 200  # Changed from 500 to 200

# Add a health check endpoint
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "message": "Flask server is running"})

# Remove manual CORS headers since flask-cors handles this
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#     return response

if __name__ == "__main__":
    print("Starting Flask server...")
    print("Server will be available at: http://localhost:5000")
    print("Health check available at: http://localhost:5000/health")
    app.run(debug=True, host='0.0.0.0', port=5000)