import pickle
import cv2
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# simple color-histogram based features to avoid heavy TF models
def extract_features(img_path, bins=(8, 8, 8)):
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Cannot read image: {img_path}")
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1, 2], None, bins, [0, 180, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist.flatten()

def load_saved_features(features_file):
    with open(features_file, 'rb') as f:
        return pickle.load(f)

def find_similar_images(query_image_path, features_dict, threshold=0.6):
    q = extract_features(query_image_path)
    similar = []
    for img_path, feat in features_dict.items():
        sim = cosine_similarity([q], [feat])[0][0]
        sim = float(sim)
        if sim >= threshold:
            similar.append({"image_path": img_path, "similarity": sim})
    similar.sort(key=lambda x: x['similarity'], reverse=True)
    return similar
