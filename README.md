# Gujarat Transportation Web Application

## Project Description

Gujarat Transportation is a comprehensive web application built with Flask that provides transportation services across Gujarat, India. The platform offers luxury bus travel (including sleeper coaches and A/C options) and heavy-duty truck transportation for cargo and logistics. The application features user authentication, booking systems, an admin panel, and a responsive design to cater to both individual travelers and businesses.

The website connects major business corridors in Gujarat, including Ahmedabad, Surat, Vadodara, Rajkot, and industrial zones in Kutch, while also supporting nationwide transportation services.

## Features

### Core Services
- **Luxury Sleeper Coaches**: Comfortable overnight travel with spacious berths
- **A/C Sleeper Coaches**: Premium air-conditioned buses with luxury interiors
- **Non-A/C Coaches**: Budget-friendly travel options
- **Heavy Truck Transport**: Reliable heavy-duty transport for cargo and logistics
- **Container Services**: Secure container shipping for industrial transportation
- **Express Delivery**: Fast and efficient delivery services
- **Tanker Services**: Liquid cargo transportation
- **Flatbed Trailers**: Heavy machinery and large equipment transport
- **Dumpers & Excavators**: Construction material transportation

### User Features
- User registration and login system
- Secure booking for bus journeys and truck shipments
- Profile management and booking history
- Responsive design for mobile and desktop
- 24/7 customer support integration (WhatsApp)
- Real-time distance calculation using Google Maps API

### Admin Features
- Admin panel for managing users and bookings
- User management system (add, edit, delete, toggle status)
- Dashboard with analytics and statistics
- Total users, bus bookings, and truck shipment tracking
- Revenue calculation for both bus and truck services
- Recent bookings overview (last 5 transactions)

### Additional Features
- Video background hero section
- Gallery showcasing fleet and services
- Contact forms and location integration
- Social media links
- GPS-tracked vehicles for safety
- 98% on-time delivery guarantee
- Interactive seat layout for bus bookings

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Database**: MySQL with mysql-connector-python + MongoDB with PyMongo
- **Frontend**: HTML5, CSS3, JavaScript
- **Icons**: Lucide icons
- **Video**: MP4 videos for hero sections
- **Authentication**: Session-based authentication
- **Real-time**: SocketIO for live seat updates and admin dashboard
- **HTTP Client**: Requests for Google Maps API
- **Deployment**: Gunicorn for production server

## Database Configuration

The application uses both MySQL and MongoDB databases:

### MySQL Configuration
- **Host**: localhost
- **User**: root
- **Password**: karan@05
- **Database**: gujarat_transport

### MongoDB Configuration
- **Host**: localhost
- **Port**: 27017
- **Database**: gujarat_transport

#### MongoDB Collections
- **users**: User accounts with roles (admin/user)
- **bus_bookings**: Bus booking records
- **truck_bookings**: Truck shipment records
- **queries**: Contact form queries

### MySQL Database Tables
- **users**: User accounts with roles (admin/user)
- **buses**: Bus information (operator, type, routes, pricing)
- **bus_bookings**: Bus booking records
- **truck_bookings**: Truck shipment records

## Installation

### Prerequisites
- Python 3.x or higher
- MySQL database server
- pip or pipenv for dependency management

### Setup Instructions

1. **Navigate to the project directory**:
   
```
   cd d:/gujarat_transportation
   
```

2. **Install dependencies**:
   
```
   pip install -r requirement.txt
   
```

   Or using Pipfile:
   
```
   pipenv install
   
```

3. **Set up the database**:
   - Ensure MySQL is running
   - Create the database: `CREATE DATABASE gujarat_transport;`
   - The application will automatically create required tables on first run

4. **Configure Google Maps API** (optional):
   - Edit `app.py` and set your Google Maps API key:
   
```
python
   GOOGLE_MAPS_KEY = "your-api-key-here"
   
```

5. **Run the application**:
   
```
   pipenv run python app.py
   
```

   Or directly:
   
```
   python app.py
   
```

6. **Access the application**:
   - Open your browser and go to `http://localhost:5000`

## Default Admin Credentials

- **Username**: admin
- **Password**: karan@2004

## Usage

### For Users
1. **Register/Login**: Create an account or log in to access booking features
2. **Browse Services**: Navigate through Home, Services, Gallery, and About pages
3. **Book Bus**: Use the Booking page to reserve bus seats with seat layout selection
4. **Book Truck**: Use Cargo Transport page for truck shipments
5. **View Bookings**: Check My Bookings page for booking history
6. **Contact Support**: Use the Contact page or WhatsApp integration for inquiries

### For Admins
1. **Admin Login**: Use the dedicated admin credentials to access the admin panel
2. **Dashboard**: View statistics on total users, bookings, and revenue
3. **Manage Users**: View, edit, delete, or toggle user status
4. **Monitor Bookings**: Track and manage bus and truck booking requests
5. **View Shipments**: Access truck shipment details and management

## API Endpoints

### Pages
- `/` - Home page
- `/about` - About page
- `/contact` - Contact page
- `/service` - Services page
- `/booking` - Bus booking page
- `/cargotransport` - Truck/cargo booking page
- `/gallery` - Gallery page
- `/profile` - User profile
- `/mybookings` - User's bookings
- `/adminpanel` - Admin dashboard
- `/manage-users` - User management
- `/queries` - Contact queries

### Authentication
- `/register` - User registration (POST)
- `/login` - User login (POST)
- `/logout` - User logout

### API
- `/api/distance` - Calculate distance using Google Maps API
- `/api/admin-stats` - Get admin statistics
- `/api/truck-admin` - Get truck shipment data
- `/api/bus-admin` - Get bus booking data
- `/get-users` - Get all users (admin)
- `/save-bus-booking` - Save bus booking
- `/save-truck-shipment` - Save truck shipment

## Project Structure

```
gujarat_transportation/
├── app.py                 # Main Flask application
├── config.py              # Application configuration
├── extensions.py          # Flask extensions
├── requirement.txt        # Python dependencies
├── Pipfile               # Pipenv dependency management
├── Pipfile.lock           # Pipenv lock file
├── transport.txt          # Project notes
├── queries.json           # Contact form queries
├── shipments.json         # Truck shipment data
├── bus_bookings.json      # Bus booking data
├── README.md             # This file
├── database/             # Database utilities
│   ├── db.py            # Database helper functions
│   └── init_db.py       # Database setup script
├── static/               # Static assets
│   ├── adminpanel.css    # Admin panel styles
│   ├── form.css          # Form styles
│   ├── login-modal.css   # Login modal styles
│   ├── main.css          # Main stylesheet
│   ├── profile.css       # Profile page styles
│   ├── img/              # Images and logos
│   ├── js/               # JavaScript files
│   │   ├── data.js       # Data handling scripts
│   │   ├── modal.js      # Modal functionality
│   │   ├── reel.js       # Reel/gallery scripts
│   │   ├── script.js     # Main scripts
│   │   └── service.js   # Service page scripts
│   └── video/            # Videos for hero sections
├── templates/            # HTML templates
│   ├── about.html        # About page
│   ├── adminpanel.html   # Admin panel
│   ├── booking.html      # Bus booking page
│   ├── bus-booking.html  # Admin bus booking management
│   ├── cargotransport.html # Truck/cargo booking
│   ├── contact.html      # Contact page
│   ├── gallery.html      # Gallery page
│   ├── index.html        # Home page
│   ├── login-modal.html  # Login modal
│   ├── manage-users.html # User management
│   ├── mybookings.html   # User bookings
│   ├── profile.html      # User profile
│   ├── queries.html      # Contact queries
│   ├── seat_layout.html  # Interactive seat layout
│   ├── service.html      # Services page
│   └── trucks-shipment.html # Admin truck shipments
└── webapp/               # Additional web app files
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is proprietary software for Gujarat Transportation. All rights reserved.

## Contact

For inquiries or support:
- **Phone**: +91 897-664-5502
- **Email**: official.karanparmar@gmail.com
- **Address**: 05 Transport Hub, Highway Road, Ahmedabad, Gujarat 700007
- **WhatsApp**: [Click to chat](https://wa.me/918976645502?text=Hi%20I%20want%20a%20booking%20service)

## Acknowledgments

- Built with a focus on safety, reliability, and customer satisfaction
- Serving Gujarat's transportation needs for over 15 years
- Committed to environmental responsibility and modern fleet management
- Special thanks to all partners and customers for their continued support
