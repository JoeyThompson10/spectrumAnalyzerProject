from flask import Flask, request, jsonify
from flask_cors import CORS
import main  # Assuming your Python script is named main.py

app = Flask(__name__)
CORS(app)

@app.route('/analyze_video', methods=['POST'])
def analyze_video():
    video = request.files['video']
    # Save the video temporarily
    video.save('temp_video.mp4')
    
    # Analyze using your existing main function
    main.VIDEO_PATH = 'temp_video.mp4'  # set video path to the uploaded video
    main.main()
    
    # TODO: Return the results in a structured format (e.g., JSON)
    # For this example, let's just return a simple message
    return jsonify({"message": "Video processed successfully!"})

@app.route('/get_constants', methods=['GET'])
def get_constants():
    constants = {
        "LOWER_GREEN": LOWER_GREEN.tolist(),
        "UPPER_GREEN": UPPER_GREEN.tolist(),
        "LOWER_WAVE_COLOR": LOWER_WAVE_COLOR.tolist(),
        "UPPER_WAVE_COLOR": UPPER_WAVE_COLOR.tolist(),
        "KERNEL_SIZE": KERNEL_SIZE.tolist(),
        "DILATE_ITERATIONS": DILATE_ITERATIONS,
        "ERODE_ITERATIONS": ERODE_ITERATIONS,
        "VIDEO_PATH": VIDEO_PATH
    }
    return jsonify(constants)


if __name__ == "__main__":
    app.run(debug=True)
