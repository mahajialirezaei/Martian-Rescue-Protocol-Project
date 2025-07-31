def get_input():
    ship = int(input('Number of accessible Starships :'))
    B = int(input('Number of Space Stations on Earth :'))
    C = int(input('Number of Residential Area on Mars :'))
    Passengers_Groups = list(map(int, input('Number of Passengers Groups :').split(' ')))
    Capacity_Residential_Area = list(map(int, input('Number of Capacity Residential Area :')))
    Time_Texas_Space_Stations = list(map(int, input('Number of Time Texas Space Stations :')))
    Time_of_Traveling = list()
    for i in range(B):
        matrix_Time = list(map(int, input('Matrix Time :').split(' ')))
        Time_of_Traveling.append(matrix_Time)
    return ship, B, C, Passengers_Groups, Capacity_Residential_Area, Time_Texas_Space_Stations, Time_of_Traveling
