import requests
import json
import time
import os

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables only.")

BASE_URL = "http://localhost:5000"

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            print("✅ Backend is healthy")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_create_payment_intent():
    """Test creating payment intent"""
    try:
        data = {
            "amount": 2500,  # $25.00 in cents
            "currency": "usd"
        }
        
        response = requests.post(
            f"{BASE_URL}/payment/create-intent",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Payment intent created successfully")
            print(f"Client Secret: {result.get('client_secret', 'N/A')[:50]}...")
            print(f"Payment Intent ID: {result.get('payment_intent_id')}")
            return result
        else:
            print(f"❌ Failed to create payment intent: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception creating payment intent: {e}")
        return None

def test_get_orders():
    """Test getting orders"""
    try:
        response = requests.get(
            f"{BASE_URL}/payment/orders",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            orders = result.get('orders', [])
            print(f"✅ Retrieved {len(orders)} orders")
            if orders:
                print("Recent orders:")
                for order in orders[-3:]:  # Show last 3 orders
                    print(f"  - Order ID: {order.get('order_id')}")
                    print(f"    Amount: ${order.get('total_amount', 0)}")
                    print(f"    Status: {order.get('status')}")
                    print(f"    Created: {order.get('created_at')}")
            return orders
        else:
            print(f"❌ Failed to get orders: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception getting orders: {e}")
        return None

def test_full_payment_flow():
    """Test complete payment flow (without actual Stripe payment)"""
    print("\n🔄 Testing full payment flow...")
    
    # Step 1: Create payment intent
    payment_intent = test_create_payment_intent()
    if not payment_intent:
        return False
    
    # Step 2: Simulate order confirmation
    # Note: In real scenario, Stripe payment would happen between step 1 and 2
    order_data = {
        "customer_info": {
            "name": "Test Customer",
            "phone": "0901234567",
            "address": "123 Test Street, Ho Chi Minh City",
            "email": "test@example.com"
        },
        "items": [
            {
                "productId": "test_pet_001",
                "name": "Golden Retriever",
                "breed": "Golden Retriever",
                "price": 25.00,
                "imageUrl": "https://example.com/image.jpg",
                "quantity": 1
            }
        ],
        "total_amount": 25.00,
        "metadata": {
            "source": "test_script",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/payment/confirm",
            json={
                "payment_intent_id": payment_intent.get('payment_intent_id'),
                "order_data": order_data
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Payment confirmed successfully")
            print(f"Order ID: {result.get('order_id')}")
            print(f"Status: {result.get('payment_status')}")
            return True
        else:
            print(f"❌ Failed to confirm payment: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception confirming payment: {e}")
        return False

def main():
    print("🧪 Testing Payment API System")
    print("=" * 50)
    
    # Test 1: Backend health
    print("\n1️⃣ Testing backend health...")
    if not test_backend_health():
        print("❌ Backend not available. Please start the backend first.")
        return
    
    # Test 2: Create payment intent
    print("\n2️⃣ Testing payment intent creation...")
    test_create_payment_intent()
    
    # Test 3: Get existing orders
    print("\n3️⃣ Testing orders retrieval...")
    test_get_orders()
    
    # Test 4: Full payment flow
    print("\n4️⃣ Testing full payment flow...")
    test_full_payment_flow()
    
    # Test 5: Get orders again to see the new one
    print("\n5️⃣ Testing orders after new payment...")
    test_get_orders()
    
    print("\n🎉 Testing completed!")
    print("\n📝 Note: This test creates a payment intent with Stripe")
    print("   but does not complete actual payment. In real app,")
    print("   Flutter would handle the Stripe payment UI.")

if __name__ == "__main__":
    main()
