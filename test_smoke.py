import pickle
from result_light import find_similar_images

features = pickle.load(open('features_light.pkl','rb'))
query = next(iter(features.keys()))
print('query:', query)
res = find_similar_images(query, features, threshold=0.1)
print('found', len(res))
for r in res[:5]:
    print(r)
