# TitanShop

TitanShop is a Django-based e-commerce web application with product browsing, user authentication, shopping cart management, order tracking, product reviews, personalized recommendations, and an AI shopping assistant interface.

The project focuses on building a complete shopping workflow while also adding recommendation features using TF-IDF and Matrix Factorization concepts.

## Project Overview

TitanShop allows users to browse products, view product details, add items to a cart, place orders, track order status, and receive product recommendations. It also includes an admin dashboard where administrators can manage users, products, categories, orders, carts, reviews, and other application data.

The recommendation system helps users discover products based on product content, ratings, categories, price ranges, and user interaction patterns. The AI shopping assistant adds a guided product discovery experience by helping users find products through shopping-related prompts and queries.

The project follows Django’s Model-View-Template architecture and keeps the application organized across separate modules for products, orders, profiles, reviews, recommendations, and admin management.

## Key Features

* User registration, login, and logout
* User profile management
* Product catalog with categories
* Product detail pages with images, pricing, descriptions, ratings, and stock details
* Shopping cart functionality
* Checkout and order placement workflow
* Order tracking
* Admin dashboard for backend management
* Product reviews and ratings
* Personalized product recommendations
* TF-IDF-based content recommendations
* Matrix Factorization-based collaborative recommendations
* AI shopping assistant interface for product discovery
* Responsive frontend using HTML, CSS, Bootstrap, and JavaScript

## Tech Stack

| Category         | Technologies Used                          |
| ---------------- | ------------------------------------------ |
| Backend          | Python, Django                             |
| Frontend         | HTML, CSS, Bootstrap, JavaScript           |
| Database         | SQLite                                     |
| Architecture     | Django MVT Pattern                         |
| Recommendations  | TF-IDF, Matrix Factorization               |
| AI Assistant     | Conversational product discovery interface |
| Admin Management | Django Admin Panel                         |
| Version Control  | Git, GitHub                                |

## Recommendation System

TitanShop includes a recommendation system that combines content-based and collaborative recommendation logic.

### TF-IDF Content Recommendations

The TF-IDF module compares product text such as names, descriptions, categories, and tags. This helps the system recommend products that are similar to items a user has viewed, rated, reviewed, or interacted with.

This approach is useful when there is limited user interaction data because recommendations can still be generated from product information.

### Matrix Factorization Recommendations

The Matrix Factorization module uses user-product interaction patterns such as ratings, reviews, and preferences. It helps identify hidden relationships between users and products so the system can recommend items based on similar behavior patterns.

By combining TF-IDF and Matrix Factorization, TitanShop supports both product-content similarity and user-behavior-based recommendations.

## AI Shopping Assistant

TitanShop includes an AI shopping assistant interface for guided product discovery. Users can enter shopping-related queries or choose suggested prompts to find relevant products from the catalog.

Example queries include:

* Best reviewed items
* Budget products
* Electronics within a price range
* New arrivals
* Category-based suggestions
* Product recommendations based on user interest

The assistant helps users explore products by category, price, rating, and popularity without manually browsing through the full catalog.

## Main Modules

### User and Profile Module

Handles user authentication and profile management. Users can create an account, log in, manage profile information, and interact with the shopping system.

### Product Module

Manages product listings, product details, categories, pricing, images, stock information, and availability.

### Cart Module

Allows users to add products to a cart, view selected items, update quantities, and continue to checkout.

### Order Module

Handles order creation, order details, delivery information, order status, and order tracking.

### Review Module

Allows users to rate and review products. Reviews help improve product credibility and support recommendation logic.

### Recommendation Module

Generates personalized product suggestions using TF-IDF and Matrix Factorization. Recommendations are based on product content, user ratings, product categories, price ranges, and interaction patterns.

### AI Shopping Assistant Module

Provides a conversational-style interface for product discovery. It helps users find products based on budget, category, ratings, popularity, and new arrivals.

### Admin Module

Uses Django’s built-in admin panel to manage products, categories, users, orders, carts, reviews, and other application data.

## System Workflow

A typical user workflow in TitanShop looks like this:

1. User registers or logs in.
2. User browses the product catalog.
3. User views product details and reviews.
4. User adds products to the cart.
5. User places an order through the checkout workflow.
6. User tracks the order status.
7. User receives product recommendations based on product content and interaction patterns.
8. User can use the AI shopping assistant to discover additional products.

## Recommendation Workflow

The recommendation system follows this general flow:

1. User interacts with products by viewing, rating, reviewing, or browsing them.
2. Product information such as names, descriptions, categories, and tags is used for content comparison.
3. TF-IDF identifies products with similar text-based features.
4. Matrix Factorization analyzes user-product interaction patterns.
5. Recommended products are shown to the user on the recommendation page.

## AI Shopping Assistant Workflow

The AI shopping assistant follows this general flow:

1. User opens the shopping assistant interface.
2. User enters a shopping-related query or selects a suggested prompt.
3. The assistant matches the query with catalog filters such as category, price, rating, or popularity.
4. Relevant products are retrieved from the product catalog.
5. Product suggestions are shown in a conversational format.
6. User can continue exploring products or navigate to product detail pages.

## Admin Panel

TitanShop uses Django’s built-in admin panel for backend management.

Administrators can:

* Add, update, and delete products
* Manage product categories
* View and manage users
* Track orders
* Manage carts and order details
* Review ratings and feedback
* Monitor recommendation-related data
* Manage application records from one centralized interface

## Project Structure

```text
TitanShop/
|
|-- TitanMarketplace/              # Main Django project settings and configuration
|-- blog/                          # Blog or informational module
|-- matrixfactorization/           # Matrix Factorization recommendation module
|-- order/                         # Order and cart-related functionality
|-- products/                      # Product-related logic
|-- profiles/                      # User profile module
|-- reviews/                       # Product reviews and ratings module
|-- shop/                          # Main shopping module
|-- static/                        # CSS, JavaScript, and image files
|-- templates/                     # HTML templates
|-- tfidf/                         # TF-IDF recommendation module
|-- screenshots/                   # Project screenshots and diagrams
|-- manage.py                      # Django project management file
|-- requirements.txt               # Python dependencies
|-- .gitignore                     # Ignored files and folders
`-- README.md                      # Project documentation
```

## Setup Instructions

Clone the repository and move into the project folder:

```bash
cd TitanShop
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run database migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create a superuser for the admin panel:

```bash
python manage.py createsuperuser
```

Run the development server:

```bash
python manage.py runserver
```

Open the local development URL shown in the terminal.


## Data and Privacy Note

This project is intended for demo and portfolio use. Do not commit real customer data, payment information, passwords, API keys, access tokens, private emails, or personal user information.

Recommended files and folders to keep out of GitHub:

```gitignore
.env
*.sqlite3
db.sqlite3
__pycache__/
.venv/
media/
```

## Future Improvements

* Add payment gateway integration in test mode
* Improve the shopping assistant with more advanced natural language handling
* Add product search with filtering and sorting
* Add wishlist functionality
* Add email notifications for order updates
* Add deployment configuration for a cloud platform
* Add more test coverage for cart, order, and recommendation workflows

## Conclusion

TitanShop demonstrates a full-stack e-commerce workflow using Django, SQLite, Bootstrap, and recommendation system concepts. It combines standard shopping features with personalized recommendations and a guided shopping assistant to make product discovery easier for users.
