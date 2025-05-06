import numpy as np
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from sklearn.metrics.pairwise import cosine_similarity

# Load model once globally
model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def get_feature_vector(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_data = image.img_to_array(img)
    img_data = np.expand_dims(img_data, axis=0)
    img_data = preprocess_input(img_data)
    feature_vector = model.predict(img_data)
    return feature_vector

def compare_images(img1_path, img2_path):
    vec1 = get_feature_vector(img1_path)
    vec2 = get_feature_vector(img2_path)
    similarity = cosine_similarity(vec1, vec2)[0][0]
    return similarity
