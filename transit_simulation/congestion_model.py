import numpy as np

def voc(tod):
    '''A helper function for defining the volume-capacity
    ratio of theroad network'''
    assert np.all((0 <= tod)&(tod <= 24)), "Time for defining congestion status should be given in hours since midnight"
    
    tod = np.asarray(tod)
    voc = np.empty(tod.shape)
    
    voc[tod <= 24] = (tod[tod <= 24]-24) * -0.02
    voc[tod < 19] = (tod[tod < 19]-19) * -0.08 + 0.1
    voc[tod < 16] = (tod[tod < 16]-14) * 0.12 + 0.1
    voc[tod < 14] = 0.1
    voc[tod < 10] = (tod[tod < 10]-10) * -0.085 + 0.1
    voc[tod < 8] = (tod[tod < 8]-5) * 0.09
    voc[tod < 5] = 0

    return voc

def intersection_status(n_intersections):
    '''Args:
    n_intersections: The number of digiroad elements nearby the location

    Returns:
    status: a scaler of speed in range [1, 0.1]'''
    power = 3
    high_limit = 20
    n_intersections = np.asarray(n_intersections)
    
    status = np.zeros(n_intersections.shape)
    status[n_intersections<high_limit] = (0.9*n_intersections**(power)/high_limit**power)[n_intersections<high_limit]
    status[n_intersections>=high_limit] = 0.9

    return 1-status

def congestion_status(tod, n_intersections):
    '''Args:
    tod: Time of day, hours since midnight
    n_intersections: The number of digiroad elements nearby the location

    Returns:
    speed limited by congestion situation [km/h]
    '''
    status = 1
    status *= (1 - voc(tod)**1.5) * intersection_status(n_intersections)

    return status


def congested_speed(speed_limit, tod, n_intersections):
    '''Args:
    speed_limit: The speed limit of a road [km/h]
    tod: Time of day, hours since midnight
    n_intersections: The number of digiroad elements nearby the location

    Returns:
    speed limited by congestion situation [km/h]
    '''
    return speed_limit*congestion_status(tod, n_intersections)

if __name__ == "__main__":
    speed_limit = 40
    tod = 8
    n_intersections = 30
    print(congestion_status(tod, n_intersections))
    print(congested_speed(speed_limit, tod, n_intersections))