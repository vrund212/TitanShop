from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.http import HttpResponseRedirect, JsonResponse
import datetime
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from django.contrib.auth.models import User

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from order.models import ShopCartForm
from .forms import ReviewForm
from .suggestions import update_clusters
from .models import Category, Product, SubCategory, Slider, Review, Cluster


def _product_score(product):
    avg_rating = product.review_set.aggregate(avg=Avg('rating'))['avg'] or 0
    return (avg_rating, product.review_set.count(), product.created)


def _popular_products(exclude_ids=None, limit=10):
    queryset = Product.objects.filter(available=True)
    if exclude_ids:
        queryset = queryset.exclude(id__in=exclude_ids)
    ranked = queryset.annotate(
        avg_rating=Avg('review__rating'),
        review_count=Count('review'),
    ).order_by('-avg_rating', '-review_count', '-created')
    products = list(ranked[:limit])
    if products:
        return products
    return list(queryset.order_by('-created')[:limit])


def _recommendation_payload(username, product_list, message):
    items = list(product_list)
    if items:
        return {
            'username': username,
            'product_list': items,
            'recommendation_message': message,
        }

    fallback = _popular_products(limit=12)
    return {
        'username': username,
        'product_list': fallback,
        'recommendation_message': 'Showing popular products because there are no unseen items left to recommend yet.',
    }


def _best_reviewed_products(limit=12):
    ranked = Product.objects.filter(available=True).annotate(
        avg_rating=Avg('review__rating'),
        review_count=Count('review'),
    ).order_by('-avg_rating', '-review_count', '-created')
    items = list(ranked[:limit])
    if items:
        return items
    return list(Product.objects.filter(available=True).order_by('-created')[:limit])


def _recommended_for_user(user, limit=12):
    """Generate personalized recommendations based on user's review history."""
    user_reviews = list(
        Review.objects.filter(user_name=user.username)
        .select_related('product', 'product__category', 'product__subCategory')
        .order_by('-pub_date')
    )
    if not user_reviews:
        return []

    reviewed_ids = {review.product_id for review in user_reviews if review.product_id}
    positive_reviews = [review for review in user_reviews if review.rating >= 4 and review.product_id]
    seed_reviews = positive_reviews or user_reviews

    category_scores = {}
    subcategory_scores = {}
    target_prices = []
    for review in seed_reviews:
        # Higher rating = higher weight, with minimum weight of 2
        weight = max(review.rating, 2)
        category_scores[review.product.category_id] = category_scores.get(review.product.category_id, 0) + weight
        subcategory_scores[review.product.subCategory_id] = subcategory_scores.get(review.product.subCategory_id, 0) + (weight * 1.5)
        target_prices.append(_effective_price(review.product))

    average_price = sum(target_prices) / len(target_prices) if target_prices else 0
    candidates = Product.objects.filter(available=True).exclude(id__in=reviewed_ids).annotate(
        avg_rating=Avg('review__rating'),
        review_count=Count('review'),
    )

    ranked = []
    for product in candidates:
        # Improved scoring algorithm
        score = 0.0
        
        # Category preference (most important for personalization)
        score += category_scores.get(product.category_id, 0) * 3.0
        score += subcategory_scores.get(product.subCategory_id, 0) * 4.0
        
        # Product quality metrics
        avg_rating = product.avg_rating or 0
        review_count = product.review_count or 0
        
        # Only consider products with at least some reviews
        if review_count > 0:
            # Weight rating more heavily if there are multiple reviews
            weighted_rating = avg_rating * (1 + min(review_count / 20, 1))
            score += weighted_rating * 2.5
            score += min(review_count, 50) * 0.3
        else:
            score += 1.0  # Small boost for new products

        # Price matching with tolerance
        if average_price > 0:
            price_gap = abs(_effective_price(product) - average_price)
            price_tolerance = average_price * 0.5  # ±50% tolerance
            if price_gap <= price_tolerance:
                score += max(0, 5 - (price_gap / price_tolerance) * 5)
            else:
                score -= 2.0  # Penalty for very different prices

        ranked.append((score, product))

    # Sort by score (descending) and then by creation date (newer first)
    ranked.sort(key=lambda item: (item[0], item[1].created), reverse=True)
    return [product for _, product in ranked[:limit]]


def _effective_price(product):
    return product.discount_price if product.discount_price is not None else product.price


def _extract_budget(query):
    """Extract budget constraint from query string."""
    # Enhanced pattern to catch more budget variations
    match = re.search(r'(?:under|below|less than|max|maximum|upto|up to|within|budget of)\s*\$?\s*(\d+(?:\.\d+)?)', query.lower())
    if match:
        return float(match.group(1))
    # Also check for patterns like "<$100" or "100 dollars"
    match = re.search(r'<\s*\$?\s*(\d+(?:\.\d+)?)', query.lower())
    if match:
        return float(match.group(1))
    return None


def _extract_search_keywords(query):
    """Extract search keywords from query, excluding price/budget terms."""
    # Remove budget-related terms from the query
    cleaned_query = re.sub(
        r'(?:under|below|less than|max|maximum|upto|up to|within|budget of|<)\s*\$?\s*\d+(?:\.\d+)?',
        '',
        query.lower()
    )
    # Extract meaningful keywords (min 2 chars to avoid noise)
    keywords = [term.strip() for term in re.split(r'\s+', cleaned_query) if len(term.strip()) > 1]
    return [k for k in keywords if k]  # Remove empty strings


def _filter_products_by_keywords(products, keywords):
    """Filter products that match one or more keywords."""
    if not keywords:
        return products
    
    filtered = []
    for product in products:
        # Check if any keyword matches product name, description, or category
        matches = False
        for keyword in keywords:
            if (keyword in product.name.lower() or
                keyword in (product.description or '').lower() or
                keyword in product.category.name.lower() or
                keyword in product.subCategory.name.lower()):
                matches = True
                break
        if matches:
            filtered.append(product)
    
    return filtered


def _assistant_product_payload(product):
    image_url = ''
    if product.image:
        try:
            image_url = product.image.url
        except ValueError:
            image_url = ''

    return {
        'id': product.id,
        'name': product.name,
        'price': _effective_price(product),
        'price_label': '${:,.2f}'.format(_effective_price(product)),
        'category': product.category.name if product.category_id else '',
        'subcategory': product.subCategory.name if product.subCategory_id else '',
        'rating': round(product.average_rating() or 0, 1),
        'reviews': product.review_set.count(),
        'description': (product.description or '')[:140],
        'url': reverse('shop:product_detail', args=[product.id]),
        'image': image_url,
    }


def _assistant_category_matches(query, queryset):
    """Match products to user query by category, keywords, and attributes."""
    lower_query = query.lower()
    category_names = list(Category.objects.values_list('name', flat=True))
    subcategory_names = list(SubCategory.objects.values_list('name', flat=True))
    matched_terms = []

    # Check for exact category matches
    for name in category_names + subcategory_names:
        lowered_name = name.lower()
        singular_name = lowered_name[:-1] if lowered_name.endswith('s') else lowered_name
        if lowered_name in lower_query or singular_name in lower_query:
            matched_terms.append(name)

    # Add keyword-based category suggestions
    keyword_mapping = {
        ('electronics', 'electronic', 'gadget', 'tech'): 'Electronics',
        ('appliances', 'appliance', 'kitchen', 'home appliance'): 'Appliances',
        ('cosmetics', 'skincare', 'face wash', 'beauty', 'makeup', 'personal care'): 'Cosmetics',
        ('clothing', 'clothes', 'apparel', 'fashion', 'wear', 'dress'): 'Clothing',
        ('book', 'books', 'novel', 'reading', 'literature'): 'Books',
        ('furniture', 'chair', 'table', 'sofa', 'bed'): 'Furniture',
    }
    
    for keywords, category in keyword_mapping.items():
        if any(kw in lower_query for kw in keywords):
            matched_terms.append(category)

    matched_terms = list(dict.fromkeys(matched_terms))
    if not matched_terms:
        return []

    category_filter = Q()
    for term in matched_terms:
        category_filter |= (
            Q(category__name__icontains=term) |
            Q(subCategory__name__icontains=term)
        )

    # Return products ordered by rating, review count, and recency
    return list(
        queryset.filter(category_filter)
        .annotate(review_count=Count('review'), avg_rating=Avg('review__rating'))
        .order_by('-avg_rating', '-review_count', '-created')
        .distinct()[:6]
    )


def shopping_assistant(request):
    """AI shopping assistant with improved accuracy and personalization."""
    query = (request.GET.get('q') or '').strip()
    lower_query = query.lower()
    quick_prompts = [
        'Show best reviewed items',
        'Find budget products under $100',
        'Show electronics',
        'Show the newest arrivals',
    ]

    if not query:
        products = _best_reviewed_products(limit=4)
        return JsonResponse({
            'message': 'Ask me for best-reviewed, budget-friendly, new, or category-based products and I will pull them from Titan Shop.',
            'products': [_assistant_product_payload(product) for product in products],
            'quick_prompts': quick_prompts,
        })

    available_products = Product.objects.filter(available=True)
    products = []
    message = ''

    # Personalized recommendations based on user's review history
    if request.user.is_authenticated and any(term in lower_query for term in ['recommend', 'suggest', 'for me', 'based on my']):
        user_recommendations = _recommended_for_user(request.user, limit=6)
        if user_recommendations:
            products = user_recommendations
            message = 'Based on your reviews, here are personalized picks just for you.'
        else:
            products = _best_reviewed_products(limit=6)
            message = 'Here are some great products you might like.'
    
    elif request.user.is_authenticated and any(term in lower_query for term in ['my reviews', 'my items', 'reviewed', 'review history']):
        reviewed_ids = list(
            Review.objects.filter(user_name=request.user.username)
            .order_by('-pub_date')
            .values_list('product_id', flat=True)
        )
        if reviewed_ids:
            unique_reviewed_ids = []
            for product_id in reviewed_ids:
                if product_id not in unique_reviewed_ids:
                    unique_reviewed_ids.append(product_id)
            reviewed_products = list(available_products.filter(id__in=unique_reviewed_ids))
            reviewed_products.sort(key=lambda product: unique_reviewed_ids.index(product.id))
            products = reviewed_products[:6]
            message = 'Here are the products you reviewed most recently.'
        else:
            message = 'You have not reviewed any products yet.'
            products = _best_reviewed_products(limit=6)
    
    elif any(term in lower_query for term in ['best', 'top rated', 'best reviewed', 'popular', 'trending', 'top', 'highest']):
        products = _best_reviewed_products(limit=6)
        message = 'These are the best-reviewed items in Titan Shop right now.'
    
    elif any(term in lower_query for term in ['new', 'newest', 'latest', 'recent', 'just']):
        products = list(available_products.order_by('-created')[:6])
        message = 'These are the newest arrivals in Titan Shop.'
    
    else:
        # Advanced search with budget and category matching
        category_products = _assistant_category_matches(query, available_products)
        budget = _extract_budget(query)
        search_keywords = _extract_search_keywords(query)
        
        if budget is not None:
            # Filter by budget
            budget_matches = [p for p in available_products if _effective_price(p) <= budget]
            
            # Apply keyword filtering if no category match
            if not category_products and search_keywords:
                budget_matches = _filter_products_by_keywords(budget_matches, search_keywords)
            elif category_products:
                category_ids = {p.id for p in category_products}
                budget_matches = [p for p in budget_matches if p.id in category_ids]
            
            # Sort by quality metrics within budget
            products = sorted(
                budget_matches,
                key=lambda p: (
                    -(p.average_rating() or 0),
                    -(p.review_set.count()),
                    _effective_price(p)
                )
            )[:6]
            
            # Build appropriate message
            if search_keywords:
                product_type = ' '.join(search_keywords).title()
                if category_products:
                    message = f'Here are highly-rated {product_type.lower()} in that category under ${budget:.0f}.'
                else:
                    message = f'Here are highly-rated {product_type.lower()} under ${budget:.0f}.'
            else:
                if category_products:
                    message = f'Here are highly-rated picks in that category under ${budget:.0f}.'
                else:
                    message = f'Here are highly-rated picks under ${budget:.0f}.'
        
        elif any(term in lower_query for term in ['cheap', 'budget', 'affordable', 'lowest', 'inexpensive']):
            # Budget-focused search
            budget_products = list(available_products)
            if search_keywords:
                budget_products = _filter_products_by_keywords(budget_products, search_keywords)
            
            products = sorted(
                budget_products,
                key=lambda p: (_effective_price(p), -(p.average_rating() or 0))
            )[:6]
            if search_keywords:
                message = f"Here are the most affordable {' '.join(search_keywords).lower()} in Titan Shop."
            elif category_products:
                message = 'Here are the most affordable items in that category.'
            else:
                message = 'Here are the most affordable products in Titan Shop.'
        
        elif search_keywords:
            # Keyword-based search with optional category filtering
            keyword_matches = _filter_products_by_keywords(list(available_products), search_keywords)
            
            # If we have category matches, use those; otherwise use generic keyword matches
            if category_products:
                products = category_products[:6]
                message = 'Here are the best-reviewed items from that category in Titan Shop.'
            elif keyword_matches:
                products = sorted(
                    keyword_matches,
                    key=lambda p: (-(p.average_rating() or 0), -(p.review_set.count()), -p.review_set.count())
                )[:6]
                product_type = ' '.join(search_keywords).title()
                message = f'Here are the best {product_type.lower()} we have in Titan Shop.'
            else:
                products = _best_reviewed_products(limit=4)
                message = 'I could not find that specific product, so here are some shop favorites.'
        
        elif category_products:
            # Category match found (no keywords)
            products = category_products[:6]
            message = 'Here are the best-reviewed items from that category in Titan Shop.'
        
        else:
            # Fallback to database search with multiple filters
            search_terms = [term for term in re.split(r'\s+', query) if len(term) > 2]
            if search_terms:
                search_filter = Q()
                for term in search_terms:
                    search_filter |= (
                        Q(name__icontains=term) |
                        Q(description__icontains=term) |
                        Q(category__name__icontains=term) |
                        Q(subCategory__name__icontains=term)
                    )
                
                products = list(
                    available_products.filter(search_filter)
                    .annotate(review_count=Count('review'), avg_rating=Avg('review__rating'))
                    .order_by('-avg_rating', '-review_count', 'name')
                    .distinct()[:6]
                )
                message = 'Here are the best-matching products I found.'

    if not products:
        products = _best_reviewed_products(limit=4)
        message = 'I could not find a match for that, so here are some shop favorites to explore.'

    return JsonResponse({
        'message': message,
        'products': [_assistant_product_payload(product) for product in products],
        'quick_prompts': quick_prompts,
    })


def signup(request):
    if request.method == "POST":
        # creating a user
        if request.POST['password'] == request.POST['repeatpassword']:
            try:
                user = User.objects.get(username=request.POST['username'])
                return render(request, 'shop/Register.html', {'error': "User already exist"})
            except User.DoesNotExist:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password'],
                                                email=request.POST['email'])

                return redirect(index)
        else:
            return render(request, 'shop/Register.html', {'error': "Password Don't match"})

    else:
        return render(request, 'shop/Register.html')


def user_login(request):
    if request.method == "POST":
        uname = request.POST['username']
        pwd = request.POST['password']
        user = auth.authenticate(username=uname, password=pwd)
        if user is not None:
            auth.login(request, user)
            return redirect('shop:shophome')

        else:
            return render(request, 'shop/login.html', {'error': "Invalid Login credential"})
    else:
        return render(request, 'shop/login.html')


def user_logout(request):
    logout(request)
    return redirect("shop:shophome")


def index(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    slider = Slider.objects.all()
    electronics = SubCategory.objects.filter(Q(category_id=1))
    products = Product.objects.filter(available=True).order_by('-created')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    return render(request, 'shop/index.html', {'category': category,
                                               'categories': categories,
                                               'slider': slider,
                                               'electronics': electronics,
                                               'product_list': paged_products,
                                               'products': paged_products})


def about(request, category_slug=None):
    category = None
    categories = Category.objects.filter(Q(name="sweate"))
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'about.html', {'category': category,
                                          'categories': categories,
                                          'products': products})


def product_list_category(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    product_list = Product.objects.order_by('-name')
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        print(category)
        products = products.filter(category=category)
    return render(request, 'shop/list.html', {'category': category,
                                              'categories': categories,
                                              'products': products,
                                              'product_list': product_list})


def search_suggestions(request):
    """Return live JSON suggestions for the search bar."""
    query = (request.GET.get('q') or '').strip()
    suggestions = []

    if query:
        products = Product.objects.filter(available=True, name__icontains=query).order_by('name')[:6]
        for product in products:
            suggestions.append({
                'name': product.name,
                'url': product.get_absolute_url(),
            })

        if len(suggestions) < 6:
            categories = Category.objects.filter(name__icontains=query)[:6-len(suggestions)]
            for category in categories:
                suggestions.append({
                    'name': 'Category: ' + category.name,
                    'url': reverse('shop:product_list_by_category', args=[category.slug]),
                })

    return JsonResponse({'suggestions': suggestions})


def search_list(request):
    """Smart hierarchical product search - progressively broader matches."""
    query = (request.GET.get('q') or '').strip()
    products = []
    
    if query:
        budget = _extract_budget(query)
        search_keywords = _extract_search_keywords(query)
        all_search_terms = [query] + search_keywords if search_keywords else [query]
        all_search_terms = [t for t in all_search_terms if t and len(t) > 1]
        
        available = Product.objects.filter(available=True)
        
        # Step 1: Search ONLY in product names (most specific)
        name_filter = Q()
        for term in all_search_terms:
            name_filter |= Q(name__icontains=term)
        products = list(available.filter(name_filter).distinct())
        
        # Step 2: If no name matches, search in category/subcategory (fallback)
        if not products:
            category_filter = Q()
            for term in all_search_terms:
                category_filter |= (
                    Q(subCategory__name__icontains=term) |
                    Q(category__name__icontains=term)
                )
            products = list(available.filter(category_filter).distinct())
        
        # Step 3: If still no results, search product descriptions (broadest)
        if not products:
            desc_filter = Q()
            for term in all_search_terms:
                desc_filter |= Q(description__icontains=term)
            products = list(available.filter(desc_filter).distinct())
        
        # Apply budget filter if specified
        if budget is not None:
            products = [p for p in products if _effective_price(p) <= budget]
        
        # Sort by rating and review count
        products = sorted(
            products,
            key=lambda p: (-(p.average_rating() or 0), -(p.review_set.count()), -p.created.timestamp())
        )
    
    return render(request, 'shop/searchview.html', {
        'products': products,
        'query': query,
    })


def product_list_subcategory(request, subcategory_slug=None):
    subcategories = SubCategory.objects.all()
    products = Product.objects.filter(available=True)
    if subcategory_slug:
        subcategory = get_object_or_404(SubCategory, slug=subcategory_slug)
        print(subcategory)
        products = products.filter(subCategory=subcategory)
    return render(request, 'shop/list.html', {'subcategory': subcategory,
                                              'subcategories': subcategories,
                                              'products': products})


# def product_detail(request, id, slug):
#     product = get_object_or_404(Product, id=id, slug=slug, available=True)
#     # cart_product_form = CartAddProductForm()
#     return render(request,
#                   'shop/show.html',
#                   {'product': product})


# for recommendation

def review_list(request):
    latest_review_list = Review.objects.order_by('-pub_date')[:9]
    context = {'latest_review_list': latest_review_list}
    return render(request, 'shop/review_list.html', context)


def review_detail(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    return render(request, 'shop/review_detail.html', {'review': review})


def product_list(request):
    product_list = Product.objects.order_by('-name')
    context = {'product_list': product_list}
    return render(request, 'shop/product_list.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_form = ShopCartForm()
    review_form = ReviewForm()
    return render(
        request,
        'shop/product_detail.html',
        {'product': product, 'cart_form': cart_form, 'review_form': review_form}
    )


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        rating = form.cleaned_data['rating']
        comment = form.cleaned_data['comment']
        user_name = request.user.username
        review = Review()
        review.product = product
        review.user_name = user_name
        review.rating = rating
        review.comment = comment
        review.pub_date = datetime.datetime.now()
        review.save()
        update_clusters(is_new_user=False)

        return HttpResponseRedirect(reverse('shop:product_detail', args=(product.id,)))

    return render(
        request,
        'shop/product_detail.html',
        {'product': product, 'review_form': form, 'cart_form': ShopCartForm()}
    )


def user_review_list(request, username=None):
    if not username:
        username = request.user.username
    latest_review_list = Review.objects.filter(user_name=username).order_by('-pub_date')
    context = {'latest_review_list': latest_review_list, 'username': username}
    return render(request, 'shop/user_review_list.html', context)


@login_required
def user_recommendation_list(request):
    user_reviews = Review.objects.filter(
        user_name=request.user.username
    ).select_related('product').order_by('-pub_date')
    reviewed_product_ids = []
    for review in user_reviews:
        if review.product_id not in reviewed_product_ids:
            reviewed_product_ids.append(review.product_id)

    reviewed_products = list(
        Product.objects.filter(id__in=reviewed_product_ids, available=True)
    )
    reviewed_products.sort(key=lambda product: reviewed_product_ids.index(product.id))

    recommended_products = _recommended_for_user(request.user, limit=12)
    best_reviewed_products = _best_reviewed_products(limit=12)
    if reviewed_product_ids:
        best_reviewed_products = [product for product in best_reviewed_products if product.id not in reviewed_product_ids]

    if recommended_products:
        message = 'These picks are based on the products, categories, and price ranges you rated most positively in Titan Shop.'
    elif reviewed_products:
        message = 'You have reviews, but there were not enough close matches yet, so we are showing strong shop-wide picks too.'
    else:
        message = 'Add a few reviews to build your recommendation profile. Until then, here are the best-reviewed items in Titan Shop.'

    context = {
        'username': request.user.username,
        'recommended_products': recommended_products,
        'reviewed_products': reviewed_products,
        'best_reviewed_products': best_reviewed_products,
        'recommendation_message': message,
    }
    return render(request, 'shop/user_recommendation_list.html', context)
