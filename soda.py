import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from pulp import LpMinimize, LpProblem, LpVariable, lpSum
from math import radians, cos, sin, sqrt, atan2

# Haversine formula to calculate the distance between two points on the Earth
def haversine(lat1, lon1, lat2, lon2):
    # The Earth's radius in miles
    R = 3958.8  # This is a constant value representing the average radius of the Earth

    # Convert latitude and longitude from degrees to radians
    # Latitude and longitude are usually given in degrees, but for accurate calculations, we need to convert them to radians
    d_lat = radians(lat2 - lat1)  # Difference in latitude between the two points
    d_lon = radians(lon2 - lon1)  # Difference in longitude between the two points
    r_lat1 = radians(lat1)  # Convert the latitude of the first point to radians
    r_lat2 = radians(lat2)  # Convert the latitude of the second point to radians

    # Haversine formula to calculate the shortest distance over the Earth's surface
    # This formula is great for calculating distances between two points on a sphere, like our planet
    a = sin(d_lat / 2) ** 2 + cos(r_lat1) * cos(r_lat2) * sin(d_lon / 2) ** 2
    # 'a' is the square of half the chord length between the points.
    # It uses the differences in latitude and longitude to determine this.

    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    # 'c' is the angular distance in radians, which is the central angle between the two points

    # Finally, multiply 'c' by the Earth's radius to get the distance in miles
    return R * c

# From a customer's perspective:
# - Imagine you want to know how far two places are from each other.
# - For instance, you want to know the distance from your home to the nearest grocery store.
# - The Haversine formula helps calculate this distance accurately by considering the Earth's curvature.

# Here’s a step-by-step breakdown:
# 1. Convert the latitude and longitude of both locations from degrees to radians.
#    - Why? Because mathematical functions like sine and cosine work with radians, not degrees.
# 2. Calculate the difference in latitude and longitude between the two points.
# 3. Use the Haversine formula to find 'a', which gives you an idea of the relative distance between the points.
# 4. Calculate 'c', the central angle, which tells you how far apart the two points are on the Earth's surface.
# 5. Multiply 'c' by the Earth's radius to convert this angle into a distance in miles.

# This means, with just the coordinates of two places, you can find out how far apart they are, helping you make decisions about travel or logistics.


# GPS coordinates for your home and stores
coordinates = {
    'Home': (33.721880, -117.139720),  # Your home
    'Cardenas': (33.721880, -117.139720),  # Cardenas
    'Vons': (33.713120, -117.193024),  # Vons
    'StaterBros': (33.683840, -117.152600),  # Stater Bros.
    'Ralphs': (33.684230, -117.168590),  # Ralphs
    'Vending': (33.720240, -117.149050),  # Vending machine
    '7-Eleven': (33.721880, -117.139720)  # 7-Eleven
}

# From a customer's perspective:
# - These coordinates are like addresses that help us pinpoint exact locations on a map.
# - We use latitude and longitude to specify where each place is.
# - Each pair of numbers represents a specific spot on Earth.

# Here's what each entry means:
# - 'Home': This is where you live. We use the coordinates to figure out distances from your home to various stores.
# - 'Cardenas': This is a grocery store near you. Its coordinates help us calculate the distance from your home to this store.
# - 'Vons': Another grocery store. By knowing its coordinates, we can determine how far it is from you.
# - 'StaterBros': Yet another grocery store. Coordinates help in figuring out if it's the closest or the best option for shopping.
# - 'Ralphs': A popular supermarket. The coordinates help us include this store in the distance and cost calculations.
# - 'Vending': A local vending machine. It's included to see if buying a soda from here is the most convenient option.
# - '7-Eleven': A convenience store. We include this in the calculation to compare with other stores.

# Why are these coordinates important?
# - They allow us to calculate the distance between your home and each store accurately.
# - This helps in optimizing your shopping trip by finding the closest store or the best combination of stores to visit.
# - Essentially, it makes your shopping more efficient, saving you time and potentially money.


# Calculate distances between all pairs of locations
def calculate_distance_matrix(locations):
    n = len(locations)  # Number of locations
    distance_matrix = np.zeros((n, n))  # Create an n x n matrix filled with zeros to store distances
    location_keys = list(locations.keys())  # List of location names

    # Loop through each pair of locations to calculate the distance between them
    for i in range(n):
        for j in range(i + 1, n):
            # Calculate the distance between location i and location j using the Haversine formula
            distance = haversine(locations[location_keys[i]][0], locations[location_keys[i]][1], locations[location_keys[j]][0], locations[location_keys[j]][1])
            distance_matrix[i, j] = distance  # Store the distance in the matrix
            distance_matrix[j, i] = distance  # Since distance from i to j is the same as from j to i, store it symmetrically

    return distance_matrix  # Return the matrix containing distances between all pairs of locations

# From a customer's perspective:
# - This function helps us figure out how far apart each pair of locations is.
# - It's like creating a table that tells us the distance from every place to every other place.
# - For example, if you want to know how far your home is from each store, this function calculates that for you.

# Here's a step-by-step breakdown:
# 1. **Number of Locations**: We count how many places we're dealing with.
# 2. **Distance Matrix**: We create a table (matrix) to store distances between every pair of locations.
# 3. **Location Names**: We list all the location names (like Home, Cardenas, Vons, etc.).
# 4. **Calculate Distances**: We loop through each pair of locations and calculate the distance using the Haversine formula.
#    - This part does the heavy lifting, calculating how far each place is from every other place.
# 5. **Symmetry**: We store each distance in the matrix in both directions (from i to j and from j to i) because the distance is the same either way.
# 6. **Return the Matrix**: Finally, we return the table with all the distances.

# Why is this important?
# - It helps in planning your shopping trip by knowing exactly how far each store is.
# - By having all distances, you can decide the best route to take to minimize travel time and cost.
# - Essentially, it makes your shopping more efficient and convenient.


# Define data for the optimization
prices = {
    'Cardenas': {'7.5oz_can_10pack': 9.29, '16.9oz_bottle_6pack': 7.99},
    'Vons': {'7.5oz_can_6pack': 3.47, '12oz_glass_24pack': 32.99},
    'StaterBros': {'12oz_can_12pack': 4.99},
    'Ralphs': {'2L': 1.49, '12oz_can_12pack': 3.99},
    'Vending': {'12oz_can': 1.35},
    '7-Eleven': {'20oz_bottle': 3.74, '30oz_BigGulp': 2.29},
}

# From a customer's perspective:
# - These are the prices of different soda packages at various stores.
# - You got these prices from newspapers delivered to your garage driveway.

# Here's a breakdown of what each entry means:
# - 'Cardenas':
#     - '7.5oz_can_10pack': A 10-pack of 7.5oz cans costs $9.29.
#     - '16.9oz_bottle_6pack': A 6-pack of 16.9oz bottles costs $7.99.
# - 'Vons':
#     - '7.5oz_can_6pack': A 6-pack of 7.5oz cans costs $3.47.
#     - '12oz_glass_24pack': A 24-pack of 12oz glass bottles costs $32.99.
# - 'StaterBros':
#     - '12oz_can_12pack': A 12-pack of 12oz cans costs $4.99.
# - 'Ralphs':
#     - '2L': A 2-liter bottle costs $1.49.
#     - '12oz_can_12pack': A 12-pack of 12oz cans costs $3.99.
# - 'Vending':
#     - '12oz_can': A single 12oz can costs $1.35 from a vending machine.
# - '7-Eleven':
#     - '20oz_bottle': A 20oz bottle costs $3.74.
#     - '30oz_BigGulp': A 30oz Big Gulp costs $2.29.

# Why is this important?
# - These prices are used to determine the most cost-effective way to buy sodas.
# - By comparing prices from different stores, you can find the best deals and save money.
# - This data is crucial for the optimization algorithm to decide where you should shop to get the best prices for the sodas you want to buy.

# Imagine you want to buy soda for a party.
# - You could go to one store and buy everything, but you might not get the best prices.
# - By using this price data, the program can figure out if it's cheaper to buy some sodas at one store and others at another store.
# - This way, you get the most sodas for the least amount of money.


# Define the total fluid ounces for each package of soda
fluid_ounces = {
    'Cardenas': {'7.5oz_can_10pack': 75, '16.9oz_bottle_6pack': 101.4},
    'Vons': {'7.5oz_can_6pack': 45, '12oz_glass_24pack': 288},
    'StaterBros': {'12oz_can_12pack': 144},
    'Ralphs': {'2L': 67.6, '12oz_can_12pack': 144},
    'Vending': {'12oz_can': 12},
    '7-Eleven': {'20oz_bottle': 20, '30oz_BigGulp': 30},
}

# From a customer's perspective:
# - This dictionary tells us how much soda (in fluid ounces) is in each package from different stores.
# - Knowing the total fluid ounces helps us understand how much soda we're getting for the price we pay.

# Here's a breakdown of what each entry means:
# - 'Cardenas':
#     - '7.5oz_can_10pack': The total fluid ounces in a 10-pack of 7.5oz cans is 75 oz (7.5 oz x 10).
#     - '16.9oz_bottle_6pack': The total fluid ounces in a 6-pack of 16.9oz bottles is 101.4 oz (16.9 oz x 6).
# - 'Vons':
#     - '7.5oz_can_6pack': The total fluid ounces in a 6-pack of 7.5oz cans is 45 oz (7.5 oz x 6).
#     - '12oz_glass_24pack': The total fluid ounces in a 24-pack of 12oz glass bottles is 288 oz (12 oz x 24).
# - 'StaterBros':
#     - '12oz_can_12pack': The total fluid ounces in a 12-pack of 12oz cans is 144 oz (12 oz x 12).
# - 'Ralphs':
#     - '2L': A 2-liter bottle contains 67.6 oz (1 liter = 33.8 oz, so 2 liters = 67.6 oz).
#     - '12oz_can_12pack': The total fluid ounces in a 12-pack of 12oz cans is 144 oz (12 oz x 12).
# - 'Vending':
#     - '12oz_can': A single 12oz can contains 12 oz of soda.
# - '7-Eleven':
#     - '20oz_bottle': A 20oz bottle contains 20 oz of soda.
#     - '30oz_BigGulp': A 30oz Big Gulp contains 30 oz of soda.

# Why is this important?
# - It helps you compare not just the prices but also the quantity of soda you get for that price.
# - By knowing the total fluid ounces, you can determine the best value for your money.
# - This data is crucial for the optimization algorithm to decide which package offers the best deal per ounce.

# Imagine you're planning a party and need a lot of soda:
# - You want to make sure you get the most soda for the least amount of money.
# - By comparing the total fluid ounces, you can see which package gives you the most soda.
# - This helps you make an informed decision, ensuring you get the best value.


# Define the number of sodas in each package
sodas_per_package = {
    'Cardenas': {'7.5oz_can_10pack': 10, '16.9oz_bottle_6pack': 6},
    'Vons': {'7.5oz_can_6pack': 6, '12oz_glass_24pack': 24},
    'StaterBros': {'12oz_can_12pack': 12},
    'Ralphs': {'2L': 1, '12oz_can_12pack': 12},
    'Vending': {'12oz_can': 1},
    '7-Eleven': {'20oz_bottle': 1, '30oz_BigGulp': 1},
}

# From a customer's perspective:
# - This dictionary tells us how many individual sodas are in each package from different stores.
# - Knowing the number of sodas per package helps us understand how many units we're getting when we buy a package.

# Here's a breakdown of what each entry means:
# - 'Cardenas':
#     - '7.5oz_can_10pack': This package contains 10 cans, each 7.5oz.
#     - '16.9oz_bottle_6pack': This package contains 6 bottles, each 16.9oz.
# - 'Vons':
#     - '7.5oz_can_6pack': This package contains 6 cans, each 7.5oz.
#     - '12oz_glass_24pack': This package contains 24 glass bottles, each 12oz.
# - 'StaterBros':
#     - '12oz_can_12pack': This package contains 12 cans, each 12oz.
# - 'Ralphs':
#     - '2L': This package contains 1 bottle, which is 2 liters (approximately 67.6oz).
#     - '12oz_can_12pack': This package contains 12 cans, each 12oz.
# - 'Vending':
#     - '12oz_can': This is a single 12oz can.
# - '7-Eleven':
#     - '20oz_bottle': This is a single 20oz bottle.
#     - '30oz_BigGulp': This is a single 30oz Big Gulp.

# Why is this important?
# - It helps you understand the quantity of sodas in each package, which is crucial for making purchasing decisions.
# - By knowing how many sodas you get in each package, you can better compare prices and quantities across different stores.
# - This data is essential for the optimization algorithm to determine the best value for the number of sodas you want to buy.

# Imagine you need to buy sodas for a party:
# - You want to know how many cans or bottles are in each package to decide how much to buy.
# - For example, if you need 24 sodas, you can choose between two 12-packs from StaterBros or one 24-pack from Vons.
# - This information helps you plan your purchase more effectively, ensuring you get the right amount of soda for your needs.


# Define shipping costs for online or delivery orders
shipping_costs = {
    'Cardenas': 0,       # Cardenas offers free shipping
    '7-Eleven': 9.55,    # 7-Eleven charges $9.55 for shipping
}

# From a customer's perspective:
# - This dictionary tells us the additional cost for having sodas delivered from certain stores.
# - Knowing the shipping costs helps us understand the total cost of our purchase if we choose delivery.

# Here's a breakdown of what each entry means:
# - 'Cardenas':
#     - Shipping cost is $0, meaning Cardenas offers free shipping.
# - '7-Eleven':
#     - Shipping cost is $9.55, meaning you'll pay an extra $9.55 to have your sodas delivered from 7-Eleven.

# Why is this important?
# - It helps you consider the full cost of purchasing sodas if you opt for delivery rather than picking them up in-store.
# - By including shipping costs, you can make a more informed decision about whether it's cheaper to buy from a store with free shipping or to buy locally and pick up yourself.

# Imagine you want to buy sodas but prefer delivery:
# - You need to know how much extra you'll pay for shipping.
# - For example, if Cardenas offers free shipping, it might be a better deal than 7-Eleven, which charges $9.55 for shipping.
# - This information helps you compare not just the price of the sodas but also the total cost including delivery, ensuring you get the best overall deal.


# Define container preferences with a numerical value indicating preference level
container_preferences = {
    'can': 1,       # Cans are preferred daily and durable containers
    'glass': 2,     # Glass is fancy and preferred for special occasions
    'plastic': 1.5  # Plastic bottles are resealable, important for saving soda for later
}

# From a customer's perspective:
# - This dictionary represents your preference for different types of containers.
# - The numerical values indicate how much you prefer each type, with lower values being more preferred.

# Here's a breakdown of what each entry means:
# - 'can':
#     - Preference value is 1.
#     - Cans are great for daily use because they are durable and convenient.
# - 'glass':
#     - Preference value is 2.
#     - Glass bottles are fancy and you prefer them for special occasions.
# - 'plastic':
#     - Preference value is 1.5.
#     - Plastic bottles are resealable, which is very important for saving soda for later.

# Why is this important?
# - It helps the program consider your container preferences when optimizing your shopping plan.
# - By including container preferences, the program can suggest options that align better with your personal taste and practical needs.

# Imagine you are choosing between different soda packages:
# - If you want a fancy option for a party, you might prefer glass bottles despite their higher preference value.
# - For everyday use, cans might be more practical due to their durability and convenience.
# - If you want to save some soda for later, plastic bottles are a great option because they can be resealed.

# How does this affect the optimization?
# - The program uses these preferences to weigh the options, potentially suggesting different stores or packages based on the container type.
# - This way, you get a shopping plan that not only saves you money but also fits your personal preferences.


# Define the type of container for each soda package
container_types = {
    '7.5oz_can_10pack': 'can',         # 10-pack of 7.5oz cans
    '16.9oz_bottle_6pack': 'plastic',  # 6-pack of 16.9oz plastic bottles
    '7.5oz_can_6pack': 'can',          # 6-pack of 7.5oz cans
    '12oz_glass_24pack': 'glass',      # 24-pack of 12oz glass bottles
    '12oz_can_12pack': 'can',          # 12-pack of 12oz cans
    '2L': 'plastic',                   # 2-liter plastic bottle
    '12oz_can': 'can',                 # Single 12oz can
    '20oz_bottle': 'plastic',          # Single 20oz plastic bottle
    '30oz_BigGulp': 'plastic'          # Single 30oz Big Gulp plastic cup
}

# From a customer's perspective:
# - This dictionary tells us the type of container for each soda package.
# - Knowing the container type helps us apply our preferences when selecting soda packages.

# Here's a breakdown of what each entry means:
# - '7.5oz_can_10pack':
#     - Container type is 'can'.
#     - This package contains 10 cans, each 7.5oz.
# - '16.9oz_bottle_6pack':
#     - Container type is 'plastic'.
#     - This package contains 6 plastic bottles, each 16.9oz.
# - '7.5oz_can_6pack':
#     - Container type is 'can'.
#     - This package contains 6 cans, each 7.5oz.
# - '12oz_glass_24pack':
#     - Container type is 'glass'.
#     - This package contains 24 glass bottles, each 12oz.
# - '12oz_can_12pack':
#     - Container type is 'can'.
#     - This package contains 12 cans, each 12oz.
# - '2L':
#     - Container type is 'plastic'.
#     - This is a single 2-liter plastic bottle.
# - '12oz_can':
#     - Container type is 'can'.
#     - This is a single 12oz can.
# - '20oz_bottle':
#     - Container type is 'plastic'.
#     - This is a single 20oz plastic bottle.
# - '30oz_BigGulp':
#     - Container type is 'plastic'.
#     - This is a single 30oz Big Gulp plastic cup.

# Why is this important?
# - It helps you know what kind of container you'll get for each soda package, which is important based on your preferences.
# - By knowing the container types, the program can consider your preferences and suggest packages that best suit your needs.

# Imagine you are choosing soda packages based on container preferences:
# - If you prefer cans for their durability and daily use, you'll know which packages contain cans.
# - If you prefer glass bottles for special occasions, you'll see which packages offer glass containers.
# - If you value the resealability of plastic bottles, you'll know which packages contain plastic bottles.

# How does this affect the optimization?
# - The program uses the container type information along with your preferences to suggest the best packages to buy.
# - This way, you get not only the best deals but also the container types that match your preferences.


# Function to determine the optimal shopping plan for buying sodas
def get_optimal_shopping_plan():
    # Ask the user for the number of sodas they want to buy
    num_sodas = int(input("Enter the number of sodas you want: "))

    # Dictionary to store the cost per soda for each store and item
    cost_per_soda = {}
    for store in prices:
        cost_per_soda[store] = {}
        for item in prices[store]:
            # Get the container type for the current item
            container = container_types[item]
            # Calculate the travel cost from home to the store
            travel_cost = haversine(coordinates['Home'][0], coordinates['Home'][1], coordinates[store][0], coordinates[store][1]) * 0.5 if store in coordinates else 0
            # Initialize shipping cost to 0
            shipping_cost = 0
            # Determine the total cost considering shipping if applicable
            if store == 'Cardenas':
                total_cost = prices[store][item]
                if total_cost < 80:
                    shipping_cost = 10  # Free shipping for orders over $80
            elif store == '7-Eleven':
                shipping_cost = shipping_costs[store]
            total_cost = prices[store][item] + travel_cost + shipping_cost
            # Calculate the cost per soda considering container preferences
            cost_per_soda[store][item] = (total_cost / sodas_per_package[store][item]) * container_preferences[container]

    # Create an optimization problem to minimize cost
    prob = LpProblem("Minimize_Cost", LpMinimize)
    # Create variables to represent the amount to buy from each store and item
    x = LpVariable.dicts("amounts_to_buy", [(store, item) for store in cost_per_soda for item in cost_per_soda[store]], 0, None, cat='Integer')
    # Objective function: Minimize the total cost
    prob += lpSum([cost_per_soda[store][item] * x[(store, item)] for store in cost_per_soda for item in cost_per_soda[store]])
    # Constraint: The total number of sodas bought should equal the requested number
    prob += lpSum([sodas_per_package[store][item] * x[(store, item)] for store in cost_per_soda for item in cost_per_soda[store]]) == num_sodas
    # Solve the optimization problem
    prob.solve()

    # Calculate the total cost for Cardenas including shipping if applicable
    total_cost_cardenas = 0
    # Dictionary to store the amounts to buy from each store and item
    amounts_to_buy = {k: v.varValue for k, v in x.items()}
    # Set to store the stores to visit
    stores_to_visit = set()

    for (store, item), amount in amounts_to_buy.items():
        if store == 'Cardenas':
            total_cost_cardenas += amount * prices[store][item]
        if amount > 0:
            stores_to_visit.add(store)

    # Apply shipping cost for Cardenas if the total is less than $80
    if total_cost_cardenas < 80 and total_cost_cardenas > 0:
        total_cost_cardenas += 10

    # Print the optimal amounts to buy from each store
    print("Amounts to buy (in number of sodas):")
    for (store, item), amount in amounts_to_buy.items():
        if amount > 0:
            container_type = container_types[item]
            travel_distance = haversine(coordinates['Home'][0], coordinates['Home'][1], coordinates[store][0], coordinates[store][1]) if store in coordinates else 'N/A'
            total_cost = amount * prices[store][item]
            fluid_ounce_per_soda = fluid_ounces[store][item] / sodas_per_package[store][item]
            print(f"{store} - {item}: {amount * sodas_per_package[store][item]:.0f} sodas, {container_type} container, Total Cost: ${total_cost:.2f}, Travel Distance: {travel_distance} miles, Fluid Ounces per Soda: {fluid_ounce_per_soda:.2f} oz")

    # Print the total cost for Cardenas if any sodas are bought from there
    if total_cost_cardenas > 0:
        print(f"Total cost for Cardenas including shipping: ${total_cost_cardenas:.2f}")

    # If multiple stores are involved, calculate the optimized route for visiting them
    if len(stores_to_visit) > 1:
        print("\nOptimized route for visiting multiple stores:")
        stores_to_visit = list(stores_to_visit)
        filtered_coordinates = {k: coordinates[k] for k in ['Home'] + stores_to_visit}
        distance_matrix = calculate_distance_matrix(filtered_coordinates)
        tsp_data = {
            'distance_matrix': distance_matrix,
            'num_locations': len(distance_matrix),
            'depot': 0  # Assuming 'Home' is the first in filtered_coordinates
        }
        manager = pywrapcp.RoutingIndexManager(len(tsp_data['distance_matrix']), 1, tsp_data['depot'])
        routing = pywrapcp.RoutingModel(manager)
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(tsp_data['distance_matrix'][from_node][to_node])
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        solution = routing.SolveWithParameters(search_parameters)
        if solution:
            print('Route:')
            index = routing.Start(0)
            plan_output = 'Route for vehicle 0:\n'
            route_distance = 0
            while not routing.IsEnd(index):
                plan_output += ' {} ->'.format(list(filtered_coordinates.keys())[manager.IndexToNode(index)])
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
            plan_output += ' {}\n'.format(list(filtered_coordinates.keys())[manager.IndexToNode(index)])
            plan_output += 'Distance of the route: {} miles\n'.format(route_distance)
            print(plan_output)

# From a customer's perspective:
# - This function helps you figure out the best way to buy the number of sodas you want, considering both cost and container preferences.

# Here's a step-by-step breakdown:
# 1. **User Input**: You enter the number of sodas you want to buy.
# 2. **Cost Calculation**: The program calculates the cost per soda for each store, including travel and shipping costs.
# 3. **Optimization Problem**: It sets up an optimization problem to minimize the total cost.
# 4. **Solving the Problem**: The program solves the optimization problem to find the best amounts to buy from each store.
# 5. **Total Cost Calculation**: If buying from Cardenas, it considers shipping if the total is less than $80.
# 6. **Print Results**: It prints the optimal amounts to buy from each store, along with the total cost and travel distance.
# 7. **Optimized Route**: If multiple stores are involved, it calculates and prints the best route to visit all the stores.

# Why is this important?
# - It helps you get the best value for your money by considering prices, container preferences, travel costs, and shipping costs.
# - By optimizing the shopping plan, you can save both time and money, ensuring you get the sodas you want in the most efficient way possible.


# Call the function to determine and print the optimal shopping plan
get_optimal_shopping_plan()

# From a customer's perspective:
# - This line is where you actually run the function to get your optimized shopping plan.
# - It triggers the whole process of calculating the best way to buy the number of sodas you want.

# Here's what happens when you run this function:
# 1. **Prompt for Input**: The program will ask you to enter the number of sodas you want.
# 2. **Cost Analysis**: It calculates the cost per soda at different stores, considering your preferences, travel costs, and shipping costs.
# 3. **Optimization**: The program finds the most cost-effective way to purchase the sodas, making sure you get the best deal.
# 4. **Results**: It prints out the amounts to buy from each store, total costs, and travel distances.
# 5. **Route Optimization**: If necessary, it also calculates the most efficient route to visit multiple stores.

# Why is this important?
# - Running this function provides you with a detailed and optimized shopping plan.
# - You can see exactly where to buy your sodas to get the best price and the most efficient route to pick them up.
# - It saves you both time and money, ensuring you get the sodas you need in the most convenient way possible.

# Imagine you need to stock up on sodas for a party:
# - Instead of manually comparing prices and figuring out the best stores to visit, you just run this function.
# - It does all the heavy lifting for you, providing a clear and optimized plan.
# - You get the best deals without the hassle, and you know exactly where to go to get your sodas.

