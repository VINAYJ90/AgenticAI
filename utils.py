import requests
import time
import math

from dotenv import load_dotenv
import os


load_dotenv()


query_dict = {'Rental Availability': "Hotels near me", \
              'Safety': "police stations near me", \
              'Connectivity': ["bus stop near me", "metro station near me", "train station near me", 'airport near me'],\
              'Health': "hospitals near me",\
              'Entertainment': ["cafes near me", "restaurants near me", "gyms near me", \
                                                "movie theaters near me", "clubs near me"],\
              'Education': ["schools near me", "colleges near me", "universities near me"],\
              'Environment': ["parks near me", "walking trails near me"],\
              'Community and Culture': ["religious place near me", \
                                        "cultural centers near me", "museum near me", "Art gallery near me"],\
              'Digital & Civic Infrastructure': ["electricity board/grid near me", "internet service provider near me", \
                                                 "toll plaza near me"],\
              'Employment Opportunities': ["coworking spaces near me", "tech parks near me", \
                                           "offices near me", "factories near me"]
              }

def search_places(query, lat, lng, radius, api_key, max_pages=2):
    """
    Search places using Google Places Text Search API.

    Parameters:
        query (str): Search query (e.g., "hospital").
        lat (float): Latitude.
        lng (float): Longitude.
        radius (int): Search radius in meters.
        api_key (str): Your Google Maps API key.
        max_pages (int): Max number of paginated result pages to fetch (default is 3).

    Returns:
        List[dict]: List of places with name, address, location, and rating info.
    """

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    all_results = []
    page_token = None

    for _ in range(max_pages):
        params = {
            "query": query,
            "location": f"{lat},{lng}",
            "rankby": "distance",
            "key": api_key
        }
        if page_token:
            params["pagetoken"] = page_token
            time.sleep(5)  # Required delay before next_page_token becomes active

        response = requests.get(url, params=params)
        response_json = response.json()

        results = response_json.get("results", [])
        for place in results:
            all_results.append({
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "lat": place.get("geometry", {}).get("location", {}).get("lat"),
                "lng": place.get("geometry", {}).get("location", {}).get("lng"),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("user_ratings_total")
            })

        page_token = response_json.get("next_page_token")
        if not page_token:
            break

    return all_results, response_json


def run_search(q_latitude, q_longitude, query_key):

    API_KEY = os.getenv('google_place_api_key')
    radius = 1
    query_output_dict = {}

    # for query_key in query_dict.keys():
    # for query_key in [query_key]:
    # query_values = query_dict.get(query_key, [])
    print('query_key: ', query_key)
    
    if type(query_key) == str:
        query_values = [query_key]
    else:
        query_values = query_key

    for query_str in query_values:
        print('query_str: ', query_str)
        places, response_json= search_places(query_str, q_latitude, q_longitude, radius, API_KEY)
        query_output_dict[query_str] = [places, response_json]

    return query_output_dict



def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two lat/lon in kilometers using Haversine formula.
    """
    R = 6371  # Earth radius in km

    abs_diff = abs(lat1 - lat2)
    if abs_diff> 10:
        x = lat1
        lat1 = lat2
        lat2 = x

        x = lon1
        lon1 = lon2
        lon2 = x 

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance




def get_rental_availability(q_latitude, q_longitude):

    query_str = query_dict.get('Rental Availability', [])
    print('query_str:', query_str)
    query_output_dict = run_search(q_latitude, q_longitude, query_str)
    print('query_output_dict:', str(query_output_dict)[:100])

    results =query_output_dict[query_str][0]

    stars = -1
    distance_sum = -1
    distance_counter = -1
    top_rating = -99
    top_place = ''


    for place in results:
        # print(place)
        lat= place.get("lat")
        lng= place.get("lng")
        dist = haversine_distance(q_latitude, q_longitude, lat, lng)
        # print(lat, lng)
        
        # print(f"Distance: {dist:.2f} km")
        # print('\n')

        if (distance_sum == -1) & (dist> 0):
            distance_sum = dist
            distance_counter = 1

        if (distance_sum > 0) & (dist> 0):
            distance_sum = distance_sum + dist
            distance_counter = distance_counter+ 1

        ratings = place.get("rating", -99)
        if (ratings is not None): 
            if (ratings > top_rating):
                top_rating = ratings
                top_place = place.get('name')

        if distance_counter >= 10:
            break


    wt_distance = distance_sum/distance_counter
    # print(distance_sum, distance_counter, wt_distance)

    if distance_counter >= 10:
        if wt_distance <= 1.5:
            return [5, top_place, top_rating]
        if wt_distance <= 3:
            return [4, top_place, top_rating]
        if wt_distance <= 5:
            return [3, top_place, top_rating]
        if wt_distance <= 10:
            return [2, top_place, top_rating]
        if wt_distance <= 20:
            return [1, top_place, top_rating]
    else :
        return [2, top_place, top_rating]
    

def get_safety(q_latitude, q_longitude):

    # print(q_latitude, q_longitude)
    query_str = 'police stations near me'
    query_output_dict = run_search(q_latitude, q_longitude, query_str)


    results =query_output_dict[query_str][0]

    stars = -1
    distance_sum = -1
    distance_counter = -1
    top_rating = -99
    top_place = ''


    for place in results:
        # print(place)
        lat= place.get("lat")
        lng= place.get("lng")
        dist = haversine_distance(q_latitude, q_longitude, lat, lng)
        # print(lat, lng)
        
        # print(f"Distance: {dist:.2f} km")
        # print('\n')

        if (distance_sum == -1) & (dist> 0):
            distance_sum = dist
            distance_counter = 1

        if (distance_sum > 0) & (dist> 0):
            distance_sum = distance_sum + dist
            distance_counter = distance_counter+ 1


        ratings = place.get("rating", -99)
        if (ratings is not None):
            if (ratings > top_rating):
                top_rating = ratings
                top_place = place.get('name')


        if distance_counter >= 4:
                break


    wt_distance = distance_sum/distance_counter
    print(distance_sum, distance_counter, wt_distance)

    if (distance_counter >= 3) & (wt_distance <= 5):
        return [5, top_place, top_rating]
    if (distance_counter >= 1) & (wt_distance <= 5):
        return [4, top_place, top_rating]
    if (wt_distance <= 10):
        return [3, top_place, top_rating]
    if (wt_distance <= 20):
        return [2, top_place, top_rating]
    if (wt_distance <= 50):
        return [1, top_place, top_rating]
    if (distance_counter == -1):
        return [0, top_place, top_rating]
    


def get_connectivity(q_latitude, q_longitude):

    # print(q_latitude, q_longitude)

    distance_sum = -1
    place_counter = -1
    top_rating = -99
    top_place = ''

    query_str = 'Connectivity'
    query_list = query_dict.get(query_str, [])
    query_output_dict = run_search(q_latitude, q_longitude, query_list)



    for query_str in query_list:
        try:
            results =query_output_dict[query_str][0]
        except:
            results = []

        for place in results:
            # print(place)
            lat= place.get("lat")
            lng= place.get("lng")
            dist = haversine_distance(q_latitude, q_longitude, lat, lng)
            # print(lat, lng)
            
            # print(f"Distance: {dist:.2f} km")
            # print('\n')

            if (distance_sum == -1) & (dist> 0):
                distance_sum = dist
                place_counter = 1

            if (distance_sum > 0) & (dist> 0):
                distance_sum = distance_sum + dist
                place_counter = place_counter+ 1

            ratings = place.get("rating", -99)
            if (ratings is not None):
                if (ratings > top_rating):
                    top_rating = ratings
                    top_place = place.get('name')


            if place_counter >= 10:
                break


    wt_distance = distance_sum/place_counter
    # print(distance_sum, place_counter, wt_distance)

    if (place_counter >= 10) & (wt_distance <= 2):
        return [5, top_place, top_rating]
    if (place_counter >= 10) & (wt_distance <= 5):
        return [4, top_place, top_rating]
    if (place_counter >= 5) & (wt_distance <= 10):
        return [3, top_place, top_rating]
    if (place_counter >= 2) & (wt_distance <= 10):
        return [2, top_place, top_rating]
    if (place_counter >= 1) & (wt_distance <= 10):
        return [1, top_place, top_rating]
    if (place_counter == -1):
        return [0, top_place, top_rating]
    else:
        return [0, top_place, top_rating]
    
def get_entertainment(q_latitude, q_longitude):

    # print(q_latitude, q_longitude)

    distance_sum = -1
    place_counter = -1
    top_rating = -99
    top_place = ''

    query_str = 'Entertainment'
    query_list = query_dict.get(query_str, [])
    query_output_dict = run_search(q_latitude, q_longitude, query_list)

    for query_str in query_list:
        try:
            results =query_output_dict[query_str][0]
        except:
            results = []

        for place in results:
            # print(place)
            lat= place.get("lat")
            lng= place.get("lng")
            dist = haversine_distance(q_latitude, q_longitude, lat, lng)
            # print(lat, lng)
            
            # print(f"Distance: {dist:.2f} km")
            # print('\n')

            if (distance_sum == -1) & (dist> 0):
                distance_sum = dist
                place_counter = 1

            if (distance_sum > 0) & (dist> 0):
                distance_sum = distance_sum + dist
                place_counter = place_counter+ 1

            ratings = place.get("rating", -99)
            if (ratings is not None):
                if (ratings > top_rating):
                    top_rating = ratings
                    top_place = place.get('name')


            print('query_str:')
            print(distance_sum, place_counter)  

            if place_counter >= 10:
                break


    wt_distance = distance_sum/place_counter
    print('Final:')
    print(distance_sum, place_counter, wt_distance)

    if (place_counter >= 10) & (wt_distance <= 2):
        return [5, top_place, top_rating]
    if (place_counter >= 10) & (wt_distance <= 5):
        return [4, top_place, top_rating]
    if (place_counter >= 5) & (wt_distance <= 10):
        return [3, top_place, top_rating]
    if (place_counter >= 2) & (wt_distance <= 10):
        return [2, top_place, top_rating]
    if (place_counter >= 1) & (wt_distance <= 10):
        return [1, top_place, top_rating]
    if (place_counter == -1):
        return [0, top_place, top_rating]
    else:
        return [0, top_place, top_rating]
    

def get_education(q_latitude, q_longitude):

    # print(q_latitude, q_longitude)

    distance_sum = -1
    place_counter = -1
    top_rating = -99
    top_place = ''
    
    query_str = 'Education'
    query_list = query_dict.get(query_str, [])
    query_output_dict = run_search(q_latitude, q_longitude, query_list)

    print('Inside Education:')
    print(query_output_dict)
    print('\n\n')
    

    for query_str in query_list:
        try:
            print('Inside Education:')
            print(query_output_dict[query_str])
            print('\n\n')

            print('Inside Education:')
            print(query_output_dict[query_str][0])
            print('\n\n')

            results =query_output_dict[query_str][0]
        except:
            results = []

        for place in results:
            print(place.get('name'))
            lat= place.get("lat")
            lng= place.get("lng")

            dist = haversine_distance(q_latitude, q_longitude, lat, lng)
            print('Indise place in results loop:', lat, lng)
            
            # print(f"Distance: {dist:.2f} km")
            # print('\n')

            if (distance_sum == -1) & (dist> 0):
                distance_sum = dist
                place_counter = 1

            if (distance_sum > 0) & (dist> 0):
                distance_sum = distance_sum + dist
                place_counter = place_counter+ 1

            ratings = place.get("rating", -99)
            if (ratings is not None):
                if (ratings > top_rating):
                    top_rating = ratings
                    top_place = place.get('name')


            if place_counter >= 10:
                break

            print(distance_sum, place_counter)


    wt_distance = distance_sum/place_counter
    print(distance_sum, place_counter, wt_distance)

    if (place_counter >= 10) & (wt_distance <= 10):
        return [5, top_place, top_rating]
    if (place_counter >= 7) & (wt_distance <= 20):
        return [4, top_place, top_rating]
    if (place_counter >= 5) & (wt_distance <= 20):
        return [3, top_place, top_rating]
    if (place_counter >= 2) & (wt_distance <= 20):
        return [2, top_place, top_rating]
    if (place_counter >= 1) & (wt_distance <= 20):
        return [1, top_place, top_rating]
    if (place_counter == -1):
        return [0, top_place, top_rating]
    else:
        return [0, top_place, top_rating]
    


def get_environment(q_latitude, q_longitude):

    # print(q_latitude, q_longitude)

    distance_sum = -1
    place_counter = -1
    top_rating = -99
    top_place = ''

    query_str = 'Environment'
    query_list = query_dict.get(query_str, [])
    query_output_dict = run_search(q_latitude, q_longitude, query_list)


    for query_str in query_list:
        try:
            results =query_output_dict[query_str][0]
        except:
            results = []

        for place in results:
            # print(place.get('name'))
            lat= place.get("lat")
            lng= place.get("lng")
            dist = haversine_distance(q_latitude, q_longitude,  lat, lng)
            # print(lat, lng)
            
            # print(f"Distance: {dist:.2f} km")
            # print('\n')

            if (distance_sum == -1) & (dist> 0):
                distance_sum = dist
                place_counter = 1

            if (distance_sum > 0) & (dist> 0):
                distance_sum = distance_sum + dist
                place_counter = place_counter+ 1

            ratings = place.get("rating", -99)
            if (ratings is not None):
                if (ratings > top_rating):
                    top_rating = ratings
                    top_place = place.get('name')


            if place_counter>= 10:
                break


    wt_distance = distance_sum/place_counter
    # print(distance_sum, place_counter, wt_distance)

    if (place_counter >= 10) & (wt_distance <= 10):
        return [5, top_place, top_rating]
    if (place_counter >= 7) & (wt_distance <= 20):
        return [4, top_place, top_rating]
    if (place_counter >= 5) & (wt_distance <= 20):
        return [3, top_place, top_rating]
    if (place_counter >= 2) & (wt_distance <= 20):
        return [2, top_place, top_rating]
    if (place_counter >= 1) & (wt_distance <= 20):
        return [1, top_place, top_rating]
    if (place_counter == -1):
        return [0, top_place, top_rating]
    else:
        return [0, top_place, top_rating]
    


def get_community(q_latitude, q_longitude):

    print(q_latitude, q_longitude)

    distance_sum = -1
    place_counter = -1
    top_rating = -99
    top_place = ''

    query_str = 'Community and Culture'
    query_list = query_dict.get(query_str, [])
    query_output_dict = run_search(q_latitude, q_longitude, query_list)


    for query_str in query_list:
        try:
            results =query_output_dict[query_str][0]
        except:
            results = []

        for place in results:
            # print(place.get('name'))
            lat= place.get("lat")
            lng= place.get("lng")
            dist = haversine_distance(q_latitude, q_longitude, lat, lng)
            # print(lat, lng)
            
            # print(f"Distance: {dist:.2f} km")
            # print('\n')

            if (distance_sum == -1) & (dist> 0):
                distance_sum = dist
                place_counter = 1

            if (distance_sum > 0) & (dist> 0):
                distance_sum = distance_sum + dist
                place_counter = place_counter+ 1

            ratings = place.get("rating", -99)
            if (ratings is not None):
                if (ratings > top_rating):
                    top_rating = ratings
                    top_place = place.get('name')

            # print(distance_sum, place_counter)


    wt_distance = distance_sum/place_counter
    # print(distance_sum, place_counter, wt_distance)

    if (place_counter >= 10) & (wt_distance <= 3):
        return [5, top_place, top_rating]
    if (place_counter >= 7) & (wt_distance <= 5):
        return [4, top_place, top_rating]
    if (place_counter >= 5) & (wt_distance <= 10):
        return [3, top_place, top_rating]
    if (place_counter >= 2) & (wt_distance <= 20):
        return [2, top_place, top_rating]
    if (place_counter >= 1) & (wt_distance <= 20):
        return [1, top_place, top_rating]
    if (place_counter == -1):
        return [0, top_place, top_rating]
    else:
        return [0, top_place, top_rating]
    


def get_d_c_infra(q_latitude, q_longitude):

    # print(q_latitude, q_longitude)

    distance_sum = -1
    place_counter = -1
    top_rating = -99
    top_place = ''
    
    
    query_str = 'Digital & Civic Infrastructure'
    query_list = query_dict.get(query_str, [])
    query_output_dict = run_search(q_latitude, q_longitude, query_list)


    for query_str in query_list:
        try:
            results =query_output_dict[query_str][0]
        except:
            results = []

        for place in results:
            # print(place.get('name'))
            lat= place.get("lat")
            lng= place.get("lng")
            dist = haversine_distance(q_latitude, q_longitude,  lat, lng)
            # print(lat, lng)
            
            # print(f"Distance: {dist:.2f} km")
            # print('\n')

            if (distance_sum == -1) & (dist> 0):
                distance_sum = dist
                place_counter = 1

            if (distance_sum > 0) & (dist> 0):
                distance_sum = distance_sum + dist
                place_counter = place_counter+ 1

            ratings = place.get("rating", -99)
            if (ratings is not None):
                if (ratings > top_rating):
                    top_rating = ratings
                    top_place = place.get('name')


    wt_distance = distance_sum/place_counter
    # print(distance_sum, place_counter, wt_distance)

    if (place_counter >= 3) & (wt_distance <= 10):
        return [5, top_place, top_rating]
    if (place_counter >= 3) & (wt_distance <= 20):
        return [4, top_place, top_rating]
    if (place_counter >= 3) & (wt_distance <= 30):
        return [3, top_place, top_rating]
    if (place_counter >= 2) & (wt_distance <= 30):
        return [2, top_place, top_rating]
    if (place_counter >= 1) & (wt_distance <= 30):
        return [1, top_place, top_rating]
    if (place_counter == -1):
        return [0, top_place, top_rating]
    else:
        return [0, top_place, top_rating]
    

def get_employment(q_latitude, q_longitude):

    # print(q_latitude, q_longitude)

    distance_sum = -1
    place_counter = -1
    top_rating = -99
    top_place = ''

    query_str = 'Employment Opportunities'
    query_list = query_dict.get(query_str, [])
    query_output_dict = run_search(q_latitude, q_longitude, query_list)

    print('\n')    
    print(query_output_dict)
    print('\n')


    

    for query_str in query_list:
        try:
            print('just str \n')    
            print(query_output_dict[query_str])
            print('\n')
            
            
            print(' str + 1 \n')    
            print(query_output_dict[query_str][0])
            print('\n')

            print(' final \n')    
            print(query_output_dict[query_str][0])
            print('\n')

            results =query_output_dict[query_str][0]
        except:
            results = []

        for place in results:
            # print(place.get('name'))
            lat= place.get("lat")
            lng= place.get("lng")
            dist = haversine_distance(q_latitude, q_longitude,  lat, lng)
            # print(lat, lng)
            
            # print(f"Distance: {dist:.2f} km")
            # print('\n')

            if (distance_sum == -1) & (dist> 0):
                distance_sum = dist
                place_counter = 1

            if (distance_sum > 0) & (dist> 0):
                distance_sum = distance_sum + dist
                place_counter = place_counter+ 1

            ratings = place.get("rating", -99)
            if (ratings is not None):
                if (ratings > top_rating):
                    top_rating = ratings
                    top_place = place.get('name')


    wt_distance = distance_sum/place_counter
    # print(distance_sum, place_counter, wt_distance)

    if (place_counter >= 10) & (wt_distance <= 30):
        return [5, top_place, top_rating]
    if (place_counter >= 5) & (wt_distance <= 30):
        return [4, top_place, top_rating]
    if (place_counter >= 5) & (wt_distance <= 50):
        return [3, top_place, top_rating]
    if (place_counter >= 2) & (wt_distance <= 50):
        return [2, top_place, top_rating]
    if (place_counter >= 1) & (wt_distance <= 50):
        return [1, top_place, top_rating]
    if (place_counter == -1):
        return [0, top_place, top_rating]
    else:
        return [0, top_place, top_rating]
    


def get_all_scores(q_latitude, q_longitude):
    print('Enetered All ')

    """
    Get all scores based on the queries and the location.
    """
    scores = {}
    new_scores = {}
    top_places = {}
    top_ratings = {}
    
    scores['Rental Availability'] = get_rental_availability(q_latitude, q_longitude)
    scores['Safety'] = get_safety(q_latitude, q_longitude)
    scores['Connectivity'] = get_connectivity( q_latitude, q_longitude)
    # scores['Health'] = 5  # Assuming health is always good
    scores['Entertainment'] = get_entertainment( q_latitude, q_longitude)
    scores['Education'] = get_education( q_latitude, q_longitude)
    # scores['Environment'] = get_environment( q_latitude, q_longitude)
    # scores['Community and Culture'] = get_community( q_latitude, q_longitude)
    # scores['Digital & Civic Infrastructure'] = get_d_c_infra( q_latitude, q_longitude)
    # scores['Employment Opportunities'] = get_employment(q_latitude, q_longitude)



    for key in scores.keys():
        values = scores.get(key)

        new_scores[key] = values[0]
        top_places[key] = values[1]
        top_ratings[key] = values[2]


    print('new_scores:', new_scores)
    print('top_places:', top_places)
    print('top_ratings:', top_ratings)
    print('Exiting All ')

    return new_scores, top_places, top_ratings


def ask_google_maps_or_not(client, message):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="If the message needs information of something, respond with Yes, else start with No. \n Response should stictly start with Yes or No. " \
            + "If response starts with no, give explanation and try to help. Keep the response concise. " \
            + "Be supportive and generally answer with a Yes. \n Message: " + message 
    )

    return response.text


def rephrase_ques_for_maps(client, message):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Rephrase the message to be asked to google maps."\
            + " give only one keyword. " \
            + "dont use any special character. \n Message: " + message 
    )

    return response.text


def respond_to_maps_output(client, message, context):

    # print('chat_history:')
    # print(str(chat_history)[:100])

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="You are a helpful guide in Bengaluru."\
               + " Use the context to answer the Question."\
               + " Keep the response concise."\
               + " Provide 2 options if possible."\
               + " Context: "+ context \
            #    + " chat history: " + str(chat_history['chat_history']) \
               + " Question: "+ message 
    )

    return response.text



def formalize_context(places):

    context = ''
    iter = 1

    for place in places:
        context = context + 'Name: ' +str(iter) +' '+ place.get('name', '') \
                          + 'Type: ' + str(place.get('type', '')) \
                          + 'Price Level: ' + str(place.get('price_level', '')) \
                          + 'Over all rating: ' + str(place.get('rating', '')) \
                          + '# of ratings: ' + str(place.get('user_ratings_total', '')) \
                          + 'Address: ' + str(place.get('address', ''))+ '. \n'
        
        iter = iter + 1

        if iter >= 5:
            break

    return context