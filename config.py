# MySQL Database Configuration
DB_CONFIG = {
    'host': 'sql12.freesqldatabase.com', 
    'port': 3306,
    'database': 'sql12809689',
    'user': 'sql12809689',  
    'password': '1HHLVLnslr',  
    'charset': 'utf8mb4',
    'autocommit': True
}

# Connection pool settings for better performance
POOL_CONFIG = {
    'pool_name': 'smartcafe_pool',
    'pool_size': 5,
    'pool_reset_session': True
}

# Cafe Theme Colors
CAFE_THEME = {
    'primary_button_bg': '#8B4513',      # Saddle Brown
    'primary_button_fg': '#FFFFFF',      # White
    'secondary_button_bg': '#D2691E',    # Chocolate
    'secondary_button_fg': '#FFFFFF',    # White
    'accent_button_bg': '#A0522D',       # Sienna
    'accent_button_fg': '#FFFFFF',       # White
    'background': '#F0EDE4',             # Light beige
    'text_primary': '#4A4A4A',           # Dark gray
    'text_secondary': '#6B4423'          # Dark brown
}
