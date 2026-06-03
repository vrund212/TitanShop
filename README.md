# TitanShop

TitanShop is a smart e-commerce web application built using Django. The platform provides a complete online shopping experience with product browsing, user authentication, shopping cart management, order tracking, admin-side management, reviews, personalized product recommendations, and an AI shopping assistant interface.

The project combines full-stack web development with recommendation system concepts such as TF-IDF and Matrix Factorization. It demonstrates how web technologies, database management, intelligent recommendation techniques, and AI-assisted product discovery can work together in a practical e-commerce platform.

---

## Project Overview

TitanShop allows users to browse products, view product details, add products to a cart, place orders, track order status, and receive personalized recommendations. The system also includes an admin dashboard where administrators can manage users, products, categories, orders, carts, reviews, and other application data.

A major focus of this project is personalization. Instead of showing only static product listings, TitanShop recommends products based on product content, user ratings, product categories, price ranges, and user interaction patterns. The AI shopping assistant further improves the user experience by helping users discover products through guided prompts and shopping-related queries.

The project follows Django’s Model-View-Template architecture, which separates the system into models, views, and templates. This makes the application easier to maintain, debug, and extend.

---

## Key Features

- User registration, login, and logout
- User profile management
- Product catalog with categories
- Product detail pages with images, pricing, descriptions, ratings, and stock details
- Shopping cart functionality
- Checkout and order placement workflow
- Order tracking system
- Admin dashboard for backend management
- Product reviews and ratings
- Personalized product recommendation system
- TF-IDF-based content recommendation
- Matrix Factorization-based collaborative recommendation
- AI shopping assistant interface for guided product discovery
- Responsive frontend using HTML, CSS, Bootstrap, and JavaScript

---

## Highlighted Feature: Recommendation System

TitanShop includes a recommendation system designed to make the shopping experience more personalized and useful. In a normal e-commerce website, users usually browse products manually or depend only on category filters. TitanShop improves this experience by suggesting products that are more relevant to the user.

The recommendation system uses two main approaches:

### 1. TF-IDF Based Content Recommendation

TF-IDF stands for Term Frequency-Inverse Document Frequency. In TitanShop, TF-IDF is used to analyze product-related text such as product names, descriptions, categories, and tags.

This helps the system find products that are textually similar to the products a user has viewed, rated, or interacted with.

For example, if a user shows interest in watches, the TF-IDF-based recommendation system can identify other products with similar product descriptions, category terms, or related keywords.

TF-IDF helps TitanShop recommend products based on:

- Product descriptions
- Product names
- Product categories
- Product tags
- Similar textual features

This approach is especially useful when the system has limited user behavior data because it can still recommend products based on product content.

### 2. Matrix Factorization Based Collaborative Recommendation

Matrix Factorization is a collaborative filtering technique. It is used to understand hidden patterns between users and products based on user-product interactions such as ratings, reviews, or preferences.

Instead of only comparing product descriptions, Matrix Factorization focuses on behavior patterns. It attempts to learn what types of products a user may prefer by analyzing how users interact with products.

For example, if users who liked one product also liked other similar products, the system can use that pattern to recommend those products to another user with similar interests.

Matrix Factorization helps TitanShop recommend products based on:

- User ratings
- Product reviews
- User-product interaction patterns
- Similar user behavior
- Hidden preference relationships

By combining TF-IDF and Matrix Factorization, TitanShop supports both content-based and collaborative recommendation logic. This makes the recommendation system more flexible and more intelligent than a simple category-based product listing.

---

## Highlighted Feature: AI Shopping Assistant

TitanShop also includes an AI shopping assistant interface that helps users discover products more easily. The assistant is designed as a conversational shopping support feature that appears on the user interface and guides users toward relevant product choices.

The AI shopping assistant improves the shopping experience by allowing users to ask product-related questions in a natural way. Instead of manually searching through many product cards, users can ask for recommendations such as budget products, best-reviewed items, new arrivals, or products from a specific category.

Example shopping queries include:

- Best reviewed items
- Budget picks
- Electronics under a price range
- New arrivals
- Category-based suggestions
- Product recommendations based on user interest

The assistant interface supports a more interactive shopping experience. It acts as a product discovery layer between the user and the catalog, helping users quickly find products that match their needs.

The AI shopping assistant is useful because it:

- Reduces manual searching
- Improves product discovery
- Makes shopping more interactive
- Helps users explore products by category, price, rating, or popularity
- Complements the recommendation system
- Makes the platform feel more intelligent and user-friendly

Together, the recommendation system and AI shopping assistant make TitanShop more than a basic e-commerce website. They add personalization, guidance, and intelligent product discovery to the platform.

---

## Tech Stack

| Category | Technologies Used |
|---|---|
| Backend | Python, Django |
| Frontend | HTML, CSS, Bootstrap, JavaScript |
| Database | SQLite |
| Architecture | Django MVT Pattern |
| Recommendation System | TF-IDF, Matrix Factorization |
| AI Assistant | Conversational product discovery interface |
| Admin Management | Django Admin Panel |
| Version Control | Git, GitHub |

---

## System Architecture

TitanShop follows Django’s MVT architecture.

### Model

The model layer defines the structure of the database and represents the main entities of the system. These include users, profiles, products, categories, carts, orders, order details, reviews, and recommendation-related data. Django ORM is used to interact with the database using Python classes instead of writing raw SQL queries.

### View

The view layer handles the business logic of the application. It receives user requests, communicates with models, processes the required data, applies recommendation logic where needed, and sends that data to templates for rendering.

### Template

The template layer is responsible for the user interface. It displays dynamic HTML pages such as product listings, product details, cart pages, order tracking screens, recommendation pages, profile pages, and the AI shopping assistant interface.

---

## Main Modules

### User and Profile Module

The user and profile module handles authentication and user-related information. Users can log in, manage their profile, and interact with the shopping system using their account.

### Product Module

The product module manages product listings, product details, categories, pricing, images, stock information, and availability.

### Cart Module

The cart module allows users to add products to their cart, view selected items, update quantities, and proceed toward checkout.

### Order Module

The order module manages order creation, order details, customer delivery information, order status, and order tracking.

### Review Module

The review module allows users to rate and review products. These reviews help improve product credibility and also support recommendation logic by providing user preference data.

### Recommendation Module

TitanShop includes recommendation functionality using TF-IDF and Matrix Factorization concepts.

- TF-IDF is used for content-based recommendations by comparing product names, descriptions, categories, and other textual information.
- Matrix Factorization supports collaborative filtering by learning patterns from user-product interactions.
- The recommendation page displays personalized suggestions based on products, categories, ratings, and price ranges that the user has interacted with positively.

### AI Shopping Assistant Module

The AI shopping assistant module provides a conversational interface for product discovery. It helps users ask shopping-related questions and receive relevant product suggestions. It supports queries related to budget products, best-reviewed items, category-based products, and new arrivals.

### Admin Module

The Django admin panel allows administrators to manage the system from a centralized backend interface. Admin users can add products, manage categories, monitor users, inspect orders, and manage reviews.

---

## Recommendation System Workflow

The recommendation system follows this general workflow:

1. User interacts with products by viewing, rating, reviewing, or browsing them.
2. Product information such as descriptions, categories, names, and tags is collected.
3. TF-IDF analyzes product text to find content similarity.
4. Matrix Factorization analyzes user-product interaction behavior.
5. The system generates recommended products based on content similarity and user preference patterns.
6. Recommended products are displayed to the user on the recommendation page.

This workflow allows TitanShop to provide more personalized shopping suggestions instead of only displaying static product lists.

---

## AI Shopping Assistant Workflow

The AI shopping assistant follows this general workflow:

1. User opens the AI shopping assistant interface.
2. User enters a shopping-related query or selects a suggested prompt.
3. The assistant interprets the shopping intent, such as budget, category, rating, or new arrivals.
4. Relevant products are retrieved from the available product catalog.
5. The assistant displays product suggestions in a user-friendly conversational format.
6. The user can continue exploring products or navigate to product pages.

This makes product discovery faster, easier, and more interactive.

---

## Admin Panel

TitanShop uses Django’s built-in admin panel for backend data management. The admin panel is directly connected to the model layer, which makes it easy to create, update, view, and delete records.

Administrators can:

- Add, update, and delete products
- Manage product categories
- View and manage users
- Track orders
- Manage carts and order details
- Review ratings and feedback
- Monitor recommendation-related data
- Monitor application data from one centralized interface

---

## Project Structure

```text
TitanShop/
│
├── TitanMarketplace/              # Main Django project settings and configuration
├── blog/                          # Blog or informational module
├── matrixfactorization/           # Matrix Factorization recommendation module
├── order/                         # Order and cart-related functionality
├── products/                      # Product-related logic
├── profiles/                      # User profile module
├── reviews/                       # Product reviews and ratings module
├── shop/                          # Main shopping module
├── static/                        # Static files such as CSS, JavaScript, and images
├── templates/                     # HTML templates
├── tfidf/                         # TF-IDF recommendation module
├── screenshots/                   # Project screenshots and diagrams
├── manage.py                      # Django project management file
├── requirements.txt               # Python dependencies
├── .gitignore                     # Ignored files and folders
└── README.md                      # Project documentation





