from sklearn.metrics.pairwise import cosine_similarity
from src.feature_extractor import get_image_features

def compare_images(img1_path, img2_path):
    vec1 = get_image_features(img1_path)
    vec2 = get_image_features(img2_path)
    similarity = cosine_similarity(vec1, vec2)[0][0]
    return similarity
