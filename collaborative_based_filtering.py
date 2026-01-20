import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
# def collaborative_filtering_recommendations(data, target_user_id, top_n = 10):
#   user_item_matrix = data.pivot_table(index= 'ID', columns='ProdID', values='Rating', aggfunc= 'mean').fillna(0)
#   user_similarity = cosine_similarity(user_item_matrix)
#   target_user_index = user_item_matrix.index.get_loc(target_user_id)
#   user_similarities = user_similarity[target_user_index]
#   similar_users_indices = user_similarities.argsort()[::-1][1:]
#   recommended_items = []

#   for user_index in similar_users_indices:
#     rated_by_similar_user = user_item_matrix.iloc[user_index]
#     not_rated_by_target_user = (rated_by_similar_user!=0) & (user_item_matrix.iloc[target_user_index]==0)

#     recommended_items.extend(user_item_matrix.columns[not_rated_by_target_user][:top_n])
#   recommended_items_details = data[data['ProdID'].isin(recommended_items)][['Name','ReviewCount','Brand','ImageURL','Rating']]
#   return recommended_items_details
#Example usage
def collaborative_filtering_recommendations(data, target_user_id, top_n=10):
    user_item_matrix = data.pivot_table(
        index='ID',
        columns='ProdID',
        values='Rating',
        aggfunc='mean'
    ).fillna(0)
    # similarity matrix
    user_similarity=cosine_similarity(user_item_matrix)
    # target user index
    target_user_index= user_item_matrix.index.get_loc(target_user_id)
    user_similarities =user_similarity[target_user_index]
    #--limit to TOP-K similar users
    TOP_K_USERS =2
    similar_users_indices = user_similarities.argsort()[::-1][1:TOP_K_USERS+1]
    #--score items
    candidate_items={}
    for user_index in similar_users_indices:
        similarity_score= user_similarities[user_index]
        user_ratings= user_item_matrix.iloc[user_index]
        for prod_id, rating in user_ratings.items():# recommend only items target user has not rated
            if rating > 0 and user_item_matrix.iloc[target_user_index][prod_id] == 0:
                candidate_items[prod_id] = candidate_items.get(prod_id, 0) + (rating * similarity_score)
    #--rank items   
    ranked_items =sorted(candidate_items.items(),key=lambda x:x[1], reverse=True)
    recommended_prod_ids= [item[0] for item in ranked_items[:top_n]]
    recommended_items_details= data[
        data['ProdID'].isin(recommended_prod_ids)
    ][['Name', 'ReviewCount', 'Brand', 'ImageURL', 'Rating']]
    return recommended_items_details

if __name__ == "__main__":
    import pandas as pd
    from preprocess_data import process_data

    raw_data = pd.read_csv("clean_data.csv")
    data = process_data(raw_data)

    target_user_id = 4
    print(collaborative_filtering_recommendations(data, target_user_id))