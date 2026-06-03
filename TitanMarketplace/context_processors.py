SUPPORTED_LANGUAGES = (
    ('en', 'English'),
    ('es', 'Espanol'),
    ('hi', 'Hindi'),
)


UI_TRANSLATIONS = {
    'en': {
        'welcome_store': 'For the Titans,',
        'daily_deals': 'By Titans',
        'change_language': 'Change Language',
        'location': 'Fullerton, CA',
        'track_order': 'Track My Order',
        'sign_in': 'Sign in',
        'sign_up': 'Sign up',
        'log_out': 'Log out',
        'search_placeholder': 'Search',
        'search_button': 'Search',
        'all_categories': 'All Categories',
        'recommendation': 'Recommendation',
        'trending': 'Trending',
        'new_arrivals': 'New Arrivals',
        'contact_us': 'Contact Us',
        'electronics_appliances': 'Electronics & appliances',
        'appliances': 'Appliances',
        'electronics': 'Electronics',
        'tv_appliances_electronics': 'TV, Appliances, Electronics',
        'no_items': 'No items',
    },
    'es': {
        'welcome_store': 'For the Titans,',
        'daily_deals': 'By Titans',
        'change_language': 'Cambiar idioma',
        'location': 'Fullerton, CA',
        'track_order': 'Rastrear pedido',
        'sign_in': 'Iniciar sesion',
        'sign_up': 'Registrarse',
        'log_out': 'Cerrar sesion',
        'search_placeholder': 'Buscar',
        'search_button': 'Buscar',
        'all_categories': 'Todas las categorias',
        'recommendation': 'Recomendaciones',
        'trending': 'Tendencias',
        'new_arrivals': 'Nuevos productos',
        'contact_us': 'Contactanos',
        'electronics_appliances': 'Electronica y electrodomesticos',
        'appliances': 'Electrodomesticos',
        'electronics': 'Electronica',
        'tv_appliances_electronics': 'TV, electrodomesticos y electronica',
        'no_items': 'Sin articulos',
    },
    'hi': {
        'welcome_store': 'For the Titans,',
        'daily_deals': 'By Titans',
        'change_language': 'Bhasha badlein',
        'location': 'Fullerton, CA',
        'track_order': 'Mera order track karein',
        'sign_in': 'Sign in',
        'sign_up': 'Sign up',
        'log_out': 'Log out',
        'search_placeholder': 'Search',
        'search_button': 'Search',
        'all_categories': 'Sabhi categories',
        'recommendation': 'Recommendation',
        'trending': 'Trending',
        'new_arrivals': 'New Arrivals',
        'contact_us': 'Contact Us',
        'electronics_appliances': 'Electronics aur appliances',
        'appliances': 'Appliances',
        'electronics': 'Electronics',
        'tv_appliances_electronics': 'TV, Appliances, Electronics',
        'no_items': 'Koi item nahi',
    },
}


def language_ui(request):
    current_language = request.session.get('site_language', 'en')
    if current_language not in UI_TRANSLATIONS:
        current_language = 'en'
    return {
        'current_language': current_language,
        'language_choices': SUPPORTED_LANGUAGES,
        'ui_text': UI_TRANSLATIONS[current_language],
    }
