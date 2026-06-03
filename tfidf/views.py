from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import pandas as pd
import scipy as sp
from sklearn.neighbors import NearestNeighbors
from django.contrib.auth.decorators import login_required

from shop.models import Product, Review
from . import contentbased as cb


def recommendation(request):
    ranked_product = Product.objects.filter(available=True).annotate(
        avg_rating=Avg('review__rating'),
        num_ratings=Count('review'),
        last_reviewed=Max('review__pub_date'),
    ).order_by('-avg_rating', '-num_ratings', '-last_reviewed', '-created')[:15]
    context = {
        "object_list": ranked_product,
        "title": "List"}

    return render(request, "tfidf/recommendation.html", context)


def detail(request, id):
    product = get_object_or_404(Product, pk=id)
    ds = pd.DataFrame(list(Product.objects.values('id', 'name', 'description')))
    if ds.empty:
        content = pd.DataFrame(columns=['id', 'name', 'description'])
    else:
        ds['name'] = ds['name'].fillna('')
        ds['description'] = ds['description'].fillna('')
        ds['search_text'] = ds['name'] + ' ' + ds['description']
        results = cb.getFrames(ds)
        content = cb.recommend(item_id=id, num=6, results=results, ds=ds)
    context = {
        "product": product,
        "content": content,
    }

    return render(request, "tfidf/detail.html", context)


def post_list(request):
    userId = request.user.id
    userName = request.user.username
    queryset = Review.objects.select_related('product')

    paginator = Paginator(queryset, 6)
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:

        queryset = paginator.page(1)
    except EmptyPage:

        queryset = paginator.page(paginator.num_pages)

    context = {
        "user_id": userId,
        "user_name": userName,
        "object_list": queryset,
        "title": "List"}
    return render(request, "tfidf/home.html", context)


def get_suggestions(request):
    all_user_names = list(map(lambda x: x.username, User.objects.only("username")))
    all_product_ids = sorted(set(map(lambda x: x.product.id, Review.objects.only("product"))))
    if len(all_user_names) < 2 or len(all_product_ids) < 2:
        context = Product.objects.filter(available=True).annotate(
            avg_rating=Avg('review__rating'),
            review_count=Count('review'),
        ).order_by('-avg_rating', '-review_count', '-created')[:8]
        return render(request, 'tfidf/cosinesim.html', {
            'username': request.user.username,
            'context': context,
            'message': 'Showing popular products because there are not enough reviews for cosine-similarity suggestions yet.',
        })

    product_index = {product_id: idx for idx, product_id in enumerate(all_product_ids)}
    product_ratings_m = sp.sparse.dok_matrix((len(all_user_names), len(all_product_ids)), dtype=float)
    for i in range(len(all_user_names)):
        user_reviews = Review.objects.filter(user_name=all_user_names[i])
        for user_review in user_reviews:
            product_ratings_m[i, product_index[user_review.product.id]] = user_review.rating

    product_ratings = product_ratings_m.transpose()
    coo = product_ratings.tocoo(copy=False)
    df = pd.DataFrame({'products': coo.row, 'users': coo.col, 'rating': coo.data})[
        ['products', 'users', 'rating']].sort_values(['products', 'users']).reset_index(drop=True)
    mo = df.pivot_table(index=['products'], columns=['users'], values='rating')
    mo.fillna(3, inplace=True)
    neighbor_count = min(7, len(mo))
    model_knn = NearestNeighbors(algorithm='brute', metric='cosine', n_neighbors=neighbor_count)
    model_knn.fit(mo.values)
    base_review = Review.objects.filter(user_name=request.user.username).order_by('-pub_date').first()
    if base_review and base_review.product_id in product_index:
        target_idx = product_index[base_review.product_id]
    else:
        target_idx = 0

    distances, indices = model_knn.kneighbors((mo.iloc[target_idx, :]).values.reshape(1, -1), return_distance=True)
    product_ids = []
    for idx in indices.flatten():
        product_id = all_product_ids[idx]
        if product_id != all_product_ids[target_idx]:
            product_ids.append(product_id)

    context = list(Product.objects.filter(id__in=product_ids, available=True))
    return render(request, 'tfidf/cosinesim.html', {
        'username': request.user.username,
        'context': context,
        'message': 'Cosine-similarity suggestions based on recent review patterns.',
    })
