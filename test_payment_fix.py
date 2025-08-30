import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_local_payment():
    try:
        # Start local server if not running
        print("🧪 Testing local payment intent creation...")
        
        data = {
            'amount': 1000,  # $10.00
            'currency': 'usd'
        }
        
        response = requests.post(
            'http://localhost:5000/payment/create-intent',
            headers={'Content-Type': 'application/json'},
            json=data,
            timeout=10
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Local payment intent success!")
            client_secret = result.get('client_secret', 'Not found')
            print(f"🔑 Client secret: {client_secret[:50]}...")
            return True
        else:
            print(f"❌ Local error: {response.text}")
            return False
            
    except requests.ConnectionError:
        print("⚠️ Local server not running. Testing production...")
        return test_production_payment()
    except Exception as e:
        print(f"❌ Local test failed: {e}")
        return False

def test_production_payment():
    try:
        print("🌐 Testing production payment intent creation...")
        
        data = {
            'amount': 1000,  # $10.00
            'currency': 'usd'
        }
        
        response = requests.post(
            'https://train-pet-image.onrender.com/payment/create-intent',
            headers={'Content-Type': 'application/json'},
            json=data,
            timeout=30
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Production payment intent success!")
            client_secret = result.get('client_secret', 'Not found')
            print(f"🔑 Client secret: {client_secret[:50]}...")
            return True
        else:
            print(f"❌ Production error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Production test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_local_payment()
    if not success:
        print("\n" + "="*50)
        test_production_payment()
