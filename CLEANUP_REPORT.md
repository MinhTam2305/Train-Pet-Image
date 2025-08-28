# Files có thể xóa để tối ưu deployment

## ✅ ĐÃ XÓA (bởi cleanup.ps1)
- `__pycache__/` - compiled Python cache
- `temp_image.jpg` - temporary upload file  
- `cert.pem`, `key.pem` - SSL certificates (dùng secrets thay thế)

## ⚠️ CÓ THỂ XÓA (tùy deployment mode)

### Nếu chỉ dùng LIGHT_MODE (không TensorFlow):
- `dactrung.py` - chỉ cần cho /train endpoint với TensorFlow
- `result.py` - chỉ cần khi LIGHT_MODE=0  
- `features.pkl` - features từ TensorFlow model
- `firebase_download.py` - chỉ cần cho /train endpoint

### Files dev/testing (không cần production):
- `test_smoke.py` - smoke test script
- `init_repo.ps1` - git initialization helper
- `cleanup.ps1` - maintenance script  
- `Dockerfile.light` - alternative lightweight Dockerfile

## 🔒 GIỮ LẠI NHƯNG CẦN BẢO MẬT
- `serviceAccountKey.json` - di chuyển vào secrets thay vì commit

## 📊 KÍCH THƯỚC THƯ MỤC
- `data/`: 17.29 MB - có thể exclude khỏi Docker và download runtime
- Toàn bộ repo: ~18 MB

## 🚀 KHUYẾN NGHỊ CHO DEPLOYMENT
1. Dùng `Dockerfile.light` cho build nhanh hơn (chỉ 4 files cần thiết)
2. Exclude `data/` khỏi Docker image, rebuild features khi start
3. Di chuyển credentials vào environment secrets
4. Remove TensorFlow files nếu không dùng /train endpoint

## LỆNH XÓA AN TOÀN (nếu chỉ dùng LIGHT_MODE):
```powershell
Remove-Item dactrung.py, result.py, features.pkl, firebase_download.py
Remove-Item test_smoke.py, init_repo.ps1, cleanup.ps1  
```

**Lưu ý**: Backup trước khi xóa. Các file TensorFlow cần thiết nếu muốn dùng /train endpoint.
