# Environment Setup Guide

## Cấu hình Environment Variables

Để đảm bảo bảo mật, các secret keys được lưu trong environment variables thay vì hard-code trong source code.

### 1. Tạo file .env

```bash
cd TrainImagePet
cp .env.example .env
```

### 2. Cập nhật .env với thông tin thực tế

Mở file `.env` và cập nhật các giá trị:

```env
# Stripe Configuration - Thay bằng key thực tế của bạn
STRIPE_SECRET_KEY=sk_test_your_actual_stripe_secret_key_here

# Application Configuration
LIGHT_MODE=1
FEATURES_FILE=features_light.pkl

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
```

### 3. Lấy Stripe Secret Key

1. Đăng nhập vào [Stripe Dashboard](https://dashboard.stripe.com/)
2. Chọn **Developers** → **API keys**
3. Copy **Secret key** (bắt đầu với `sk_test_` cho test mode)
4. Paste vào file `.env`

### 4. Kiểm tra cấu hình

Chạy test để đảm bảo mọi thứ hoạt động:

```bash
python test_payment_api.py
```

## Bảo mật

### ❌ KHÔNG BAO GIỜ:
- Commit file `.env` vào git
- Share Stripe Secret Key qua email/chat
- Hard-code secret keys trong source code
- Push secret keys lên GitHub

### ✅ NÊN:
- Sử dụng environment variables
- Giữ file `.env` ở local
- Sử dụng `.env.example` làm template
- Sử dụng test keys trong development
- Sử dụng production keys chỉ trong production

## Production Deployment

Khi deploy lên production (Heroku, Railway, etc.):

1. **Không upload file .env**
2. **Cấu hình environment variables trên platform:**

### Heroku:
```bash
heroku config:set STRIPE_SECRET_KEY=sk_live_your_production_key
```

### Railway:
Vào dashboard → Settings → Variables → Add variable

### Vercel:
Vào dashboard → Settings → Environment Variables

## Troubleshooting

### Lỗi "STRIPE_SECRET_KEY not set"
```
⚠️  WARNING: STRIPE_SECRET_KEY environment variable not set!
```

**Giải pháp:**
1. Kiểm tra file `.env` có tồn tại không
2. Kiểm tra format trong file `.env`
3. Restart application sau khi thay đổi .env

### Lỗi "python-dotenv not installed"
```
⚠️  python-dotenv not installed
```

**Giải pháp:**
```bash
pip install python-dotenv
```

### Lỗi Stripe API
```
Error creating payment intent: 401
```

**Giải pháp:**
1. Kiểm tra Stripe Secret Key có đúng không
2. Kiểm tra key có phải test key (sk_test_) hay live key (sk_live_)
3. Kiểm tra Stripe account có active không
