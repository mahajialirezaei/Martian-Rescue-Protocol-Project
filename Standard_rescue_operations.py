def get_input():
    ship = int(input('Number of accessible Starships :'))
    B = int(input('Number of Space Stations on Earth :'))
    C = int(input('Number of Residential Area on Mars :'))
    source = list(map(int, input('Number of Passengers Groups :').split(' ')))
    dest = list(map(int, input('Number of Capacity Residential Area :').split(' ')))
    init_time = list(map(int, input('Number of Time Texas Space Stations :').split(' ')))
    travel_time = list()
    for i in range(B):
        matrix_Time = list(map(int, input('Matrix Time :').split(' ')))
        travel_time.append(matrix_Time)
    return ship, B, C, source, dest, init_time, travel_time


ship, B, C, source, dest, init_time, travel_time = get_input()
