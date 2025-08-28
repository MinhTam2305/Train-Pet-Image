from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
USE_LIGHT = os.environ.get('LIGHT_MODE', '1') in ('1', 'true', 'True')

if USE_LIGHT:
    # lightweight, OpenCV-based feature extractor (no TensorFlow)
    from result_light import load_saved_features, find_similar_images
else:
    from result import load_saved_features, find_similar_images
import os
from PIL import Image
import subprocess

app = Flask(__name__)
CORS(app, resources={r"/search": {"origins": "*"}}) 
# prefer light-weight features file when LIGHT_MODE is enabled
features_file = os.environ.get('FEATURES_FILE') or ('features_light.pkl' if USE_LIGHT else 'features.pkl')
features_dict = load_saved_features(features_file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/image/<path:filename>')
def serve_image(filename):
    try:
        return send_file(filename)
    except:
        return "Image not found", 404

@app.route('/search', methods=['POST'])
def search_image():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        print("Received file:", file.filename)  # In ra tên file nhận được
        file_path = 'temp_image.jpg'
        file.save(file_path)

        # Kiểm tra file đã được lưu không
        if not os.path.isfile(file_path):
            return jsonify({"error": "File not saved"}), 500

        # Kiểm tra ảnh
        try:
            img = Image.open(file_path)
            img.verify()  # Kiểm tra tính hợp lệ của file ảnh
            print(f"Image {file.filename} verified successfully.")
        except Exception as e:
            return jsonify({"error": f"Image verification failed: {str(e)}"}), 500

        # Tìm các ảnh tương đồng
        similar_images = find_similar_images(file_path, features_dict)

        # Kiểm tra nếu không tìm thấy ảnh tương tự
        if similar_images:
            return jsonify({
                "similar_images": similar_images  # Trả về toàn bộ danh sách ảnh tương tự
            })
        else:
            return jsonify({"message": "No similar images found"}), 404
    
    except Exception as e:
        print("Error occurred:", str(e))  # In ra thông báo lỗi
        return jsonify({"error": str(e)}), 500

@app.route('/train', methods=['POST'])
def train_features():
    try:
        if USE_LIGHT:
            # Train light features (color histogram)
            import subprocess
            result = subprocess.run(['python', 'build_features_light.py'], 
                                  capture_output=True, text=True, check=True)
            
            # Reload features
            global features_dict
            features_dict = load_saved_features('features_light.pkl')
            
            return jsonify({
                'message': 'Light training completed!', 
                'mode': 'LIGHT_MODE',
                'features_count': len(features_dict),
                'output': result.stdout
            }), 200
        else:
            # Import TensorFlow-based feature extraction only when needed
            from dactrung import extract_and_save_features
            
            # Tải toàn bộ ảnh mới nhất từ Firebase Storage về trước khi train
            subprocess.run(['python', 'firebase_download.py'], check=True)
            # Train lại đặc trưng cho toàn bộ ảnh trong data/
            extract_and_save_features('data/', 'features.pkl')
            global features_dict
            features_dict = load_saved_features('features.pkl')
            return jsonify({
                'message': 'TensorFlow training completed!',
                'mode': 'TENSORFLOW_MODE', 
                'features_count': len(features_dict)
            }), 200
    except Exception as e:
        return jsonify({'error': str(e), 'mode': 'LIGHT_MODE' if USE_LIGHT else 'TENSORFLOW_MODE'}), 500

@app.route('/train/light', methods=['POST'])
def train_light_features():
    """Force train with light mode (color histogram) regardless of current mode"""
    try:
        import subprocess
        result = subprocess.run(['python', 'build_features_light.py'], 
                              capture_output=True, text=True, check=True)
        
        # Count features
        import pickle
        with open('features_light.pkl', 'rb') as f:
            light_features = pickle.load(f)
        
        return jsonify({
            'message': 'Light features training completed!',
            'features_count': len(light_features),
            'output': result.stdout
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get current app status and features info"""
    try:
        return jsonify({
            'status': 'running',
            'mode': 'LIGHT_MODE' if USE_LIGHT else 'TENSORFLOW_MODE',
            'features_file': features_file,
            'features_count': len(features_dict),
            'sample_images': list(features_dict.keys())[:5] if features_dict else []
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
