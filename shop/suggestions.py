from django.contrib.auth.models import User
from sklearn.cluster import KMeans
from scipy.sparse import dok_matrix, csr_matrix
import numpy as np

from .models import Review, Cluster


def update_clusters(is_new_user):
    """Update user clusters based on review patterns for better recommendations."""
    num_reviews = Review.objects.count()
    update_step = 6
    
    # Only update clusters periodically to avoid overhead
    if num_reviews < update_step or (num_reviews % update_step != 0 and not is_new_user):
        return
    
    all_user_names = list(map(lambda x: x.username, User.objects.only("username")))
    all_product_ids = set(map(lambda x: x.product.id, Review.objects.only("product")))
    num_users = len(all_user_names)
    
    if num_users == 0 or not all_product_ids:
        Cluster.objects.all().delete()
        return

    # Handle edge cases
    if num_users < 2 or num_reviews < 2:
        Cluster.objects.all().delete()
        singleton = Cluster.objects.create(name="cluster-0")
        singleton.users.add(*User.objects.filter(username__in=all_user_names))
        return

    # Build user-product rating matrix
    ratings_m = dok_matrix((num_users, max(all_product_ids) + 1), dtype=np.float32)
    for i in range(num_users):
        user_reviews = Review.objects.filter(user_name=all_user_names[i])
        for user_review in user_reviews:
            # Normalize ratings to 0-1 scale for better clustering
            normalized_rating = user_review.rating / 5.0
            ratings_m[i, user_review.product.id] = normalized_rating

    # Determine optimal number of clusters (roughly 1 per 10 users, min 1, max num_users)
    k = min(max(1, int(num_users / 10) + 1), num_users)
    
    try:
        # Use K-means clustering with improved parameters
        kmeans = KMeans(
            n_clusters=k,
            n_init=10,
            random_state=42,
            max_iter=300,
            tol=1e-4
        )
        clustering = kmeans.fit(ratings_m.tocsr())

        # Clear old clusters and create new ones
        Cluster.objects.all().delete()
        new_clusters = {i: Cluster(name=f"cluster-{i}") for i in range(k)}
        for cluster in new_clusters.values():
            cluster.save()
        
        # Assign users to clusters
        for i, cluster_label in enumerate(clustering.labels_):
            user = User.objects.get(username=all_user_names[i])
            new_clusters[cluster_label].users.add(user)
    
    except Exception as e:
        # Fallback to simple singleton cluster on error
        print(f"Clustering error: {e}. Using fallback cluster.")
        Cluster.objects.all().delete()
        singleton = Cluster.objects.create(name="cluster-0")
        singleton.users.add(*User.objects.filter(username__in=all_user_names))
