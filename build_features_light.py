import os
import pickle
from result_light import extract_features

DATA_DIR = 'data'
OUT_FILE = 'features_light.pkl'

features = {}
for root, _, files in os.walk(DATA_DIR):
    for fname in files:
        path = os.path.join(root, fname)
        try:
            features[path] = extract_features(path)
        except Exception as e:
            print('skip', path, '->', e)

with open(OUT_FILE, 'wb') as f:
    pickle.dump(features, f)

print(f'built {len(features)} features -> {OUT_FILE}')
