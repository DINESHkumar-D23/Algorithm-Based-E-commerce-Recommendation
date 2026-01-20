import pandas as pd
from preprocess_data import process_data 
from collaborative_based_filtering import collaborative_filtering_recommendations
from hybrid_approach import hybrid_recommendation_filtering
from rating_based_recommendation import get_top_rated_items
from content_based_filtering import content_based_recommendation
def get_relevant_items(data, target_user_id):
    filtered_data = data[
        (data['ID'] == target_user_id) &
        (data['Rating'] >= 4)
    ]

    relevant_items = (
        filtered_data['Name']
        .drop_duplicates()
        .tolist()
    )
    return relevant_items

    