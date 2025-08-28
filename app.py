from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
import json
import requests
from datetime import datetime
import uuid

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Environment variables will be loaded from system only.")
    print("   Install with: pip install python-dotenv")

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
CORS(app, resources={
    r"/search": {"origins": "*"},
    r"/payment/*": {"origins": "*"}
}) 
# prefer light-weight features file when LIGHT_MODE is enabled
features_file = os.environ.get('FEATURES_FILE') or ('features_light.pkl' if USE_LIGHT else 'features.pkl')
features_dict = load_saved_features(features_file)

# Stripe configuration
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_API_URL = "https://api.stripe.com/v1"

if not STRIPE_SECRET_KEY:
    print("⚠️  WARNING: STRIPE_SECRET_KEY environment variable not set!")
    print("   Please set STRIPE_SECRET_KEY in your environment or .env file")
    print("   Payment functionality will not work without this key")

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
    global features_dict  # Declare at the beginning
    try:
        if USE_LIGHT:
            # Train light features (color histogram)
            import subprocess
            result = subprocess.run(['python', 'build_features_light.py'], 
                                  capture_output=True, text=True, check=True)
            
            # Reload features
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

# ============ PAYMENT APIs ============

@app.route('/payment/create-intent', methods=['POST'])
def create_payment_intent():
    """Create Stripe Payment Intent"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'amount' not in data:
            return jsonify({'error': 'Amount is required'}), 400
            
        amount = data['amount']  # Amount in cents
        currency = data.get('currency', 'usd')
        
        # Create payment intent with Stripe
        stripe_data = {
            "amount": str(amount),
            "currency": currency,
            "payment_method_types[]": "card",
            "automatic_payment_methods[enabled]": "true"
        }
        
        headers = {
            "Authorization": f"Bearer {STRIPE_SECRET_KEY}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        response = requests.post(
            f"{STRIPE_API_URL}/payment_intents",
            data=stripe_data,
            headers=headers
        )
        
        if response.status_code != 200:
            return jsonify({
                'error': 'Failed to create payment intent',
                'details': response.text
            }), 400
            
        payment_intent = response.json()
        
        return jsonify({
            'client_secret': payment_intent['client_secret'],
            'payment_intent_id': payment_intent['id'],
            'amount': payment_intent['amount'],
            'currency': payment_intent['currency']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/payment/confirm', methods=['POST'])
def confirm_payment():
    """Confirm payment and save order"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['payment_intent_id', 'order_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        payment_intent_id = data['payment_intent_id']
        order_data = data['order_data']
        
        # Verify payment with Stripe
        headers = {
            "Authorization": f"Bearer {STRIPE_SECRET_KEY}",
        }
        
        stripe_response = requests.get(
            f"{STRIPE_API_URL}/payment_intents/{payment_intent_id}",
            headers=headers
        )
        
        if stripe_response.status_code != 200:
            return jsonify({
                'error': 'Failed to verify payment',
                'details': stripe_response.text
            }), 400
            
        payment_intent = stripe_response.json()
        
        # Check if payment is successful
        if payment_intent['status'] != 'succeeded':
            return jsonify({
                'error': 'Payment not completed',
                'status': payment_intent['status']
            }), 400
        
        # Generate order ID
        order_id = str(uuid.uuid4())
        
        # Prepare order data
        order_record = {
            'order_id': order_id,
            'payment_intent_id': payment_intent_id,
            'amount': payment_intent['amount'],
            'currency': payment_intent['currency'],
            'status': 'completed',
            'customer_info': order_data.get('customer_info', {}),
            'items': order_data.get('items', []),
            'total_amount': order_data.get('total_amount', 0),
            'payment_method': 'stripe',
            'created_at': datetime.now().isoformat(),
            'metadata': order_data.get('metadata', {})
        }
        
        # Save order to file (you can replace this with database storage)
        orders_file = 'orders.json'
        orders = []
        
        if os.path.exists(orders_file):
            try:
                with open(orders_file, 'r', encoding='utf-8') as f:
                    orders = json.load(f)
            except:
                orders = []
        
        orders.append(order_record)
        
        with open(orders_file, 'w', encoding='utf-8') as f:
            json.dump(orders, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'payment_status': 'completed',
            'message': 'Payment confirmed and order saved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/payment/orders', methods=['GET'])
def get_orders():
    """Get all orders"""
    try:
        orders_file = 'orders.json'
        
        if not os.path.exists(orders_file):
            return jsonify({'orders': []}), 200
            
        with open(orders_file, 'r', encoding='utf-8') as f:
            orders = json.load(f)
            
        # Optional: filter by email or user
        email = request.args.get('email')
        if email:
            orders = [order for order in orders if order.get('customer_info', {}).get('email') == email]
            
        return jsonify({'orders': orders}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/payment/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get specific order by ID"""
    try:
        orders_file = 'orders.json'
        
        if not os.path.exists(orders_file):
            return jsonify({'error': 'Order not found'}), 404
            
        with open(orders_file, 'r', encoding='utf-8') as f:
            orders = json.load(f)
            
        order = next((o for o in orders if o['order_id'] == order_id), None)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
            
        return jsonify({'order': order}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
