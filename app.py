   from flask import Flask, request, jsonify
import json
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

def calculate_distance(coord1, coord2):
    # Radius of the Earth in km
    R = 6371.0

    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def recommend_services(user_location, services_data, max_distance=10.0, min_rating=0.0, prix_per_kelo_max=float('inf'), num_recommendations=10):
    # Calculate distance for each service and sort by distance
    for service in services_data:
        if 'title' not in service:
            continue
        title = service['title']
        latitude = service.get('latitude', 0.0)
        longitude = service.get('longitude', 0.0)
        review_rating = service.get('review_rating', 0.0)
        service['distance'] = calculate_distance(user_location, (latitude, longitude))
        service['title'] = title
        service['latitude'] = latitude
        service['longitude'] = longitude
        service['review_rating'] = review_rating
        service['price_per_kilometre'] = 0.1  # Adding price_per_kilometre field
        service['contact'] = "0776464646"  # Adding contact field
    
    sorted_services = sorted(services_data, key=lambda x: x.get('distance', float('inf')))

    # Filter services by rating, distance, and price_per_kilometre
    filtered_services = [service for service in sorted_services 
                         if service.get('review_rating', 0.0) >= min_rating 
                         and service.get('distance', float('inf')) <= max_distance
                         and service.get('price_per_kilometre', float('inf')) <= prix_per_kelo_max]
    
    # Recommend the top services based on distance, rating, and price_per_kilometre
    recommended_services = filtered_services[:num_recommendations]

    return recommended_services

@app.route('/recommend-services', methods=['POST'])
def get_recommendations():
    # Get latitude, longitude, max distance, and max price per kilometer from request JSON
    request_data = request.get_json()
    latitude = request_data.get('latitude')
    longitude = request_data.get('longitude')
    max_distance = request_data.get('max_distance', 10.0)  # Default max distance is 10.0 km
    prix_per_kelo_max = request_data.get('prix_per_kelo_max', float('inf'))  # Default max price per kilometer is infinity

    if latitude is None or longitude is None:
        return jsonify({'error': 'Latitude and longitude are required.'}), 400

    user_location = (float(latitude), float(longitude))

    # Read data from JSON file
    with open('./auto_services_data.json', 'r', encoding='utf-8') as json_file:
        services_data = json.load(json_file)

    # Get recommended services
    recommended_services = recommend_services(user_location, services_data, 
                                              max_distance=float(max_distance), 
                                              prix_per_kelo_max=float(prix_per_kelo_max))

    return jsonify(recommended_services)

if __name__ == '__main__':
    app.run(debug=True)
