import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# Function to calculate GHA and Declination (simplified version)
def calculate_gha_dec(body, time):
    if body.lower() == 'sun':
        gha = (280.46061837 + 360.98564736629 * time) % 360  # Simplified GHA calculation
        dec = 23.44 * np.sin(np.deg2rad(360/365.24 * (time - 81)))  # Simplified Dec calculation
        return gha, dec
    else:
        raise ValueError("Unknown celestial body")

# Function to calculate altitude and azimuth from assumed position
def calculate_alt_az(lat, lon, gha, dec):
    lat = np.deg2rad(lat)
    lon = np.deg2rad(lon)
    dec = np.deg2rad(dec)
    gha = np.deg2rad(gha)

    ha = gha + lon
    alt = np.arcsin(np.sin(lat) * np.sin(dec) + np.cos(lat) * np.cos(dec) * np.cos(ha))
    az = np.arccos((np.sin(dec) - np.sin(alt) * np.sin(lat)) / (np.cos(alt) * np.cos(lat)))

    alt = np.rad2deg(alt)
    az = np.rad2deg(az)

    if np.sin(ha) > 0:
        az = 360 - az

    return alt, az

# Function to perform position fix
def position_fix(observed_alt, lat, lon, time):
    gha, dec = calculate_gha_dec('sun', time)
    calc_alt, calc_az = calculate_alt_az(lat, lon, gha, dec)
    intercept = observed_alt - calc_alt

    lat_correction = intercept / 60.0 * np.cos(np.deg2rad(calc_az))
    lon_correction = intercept / 60.0 * np.sin(np.deg2rad(calc_az)) / np.cos(np.deg2rad(lat))

    corrected_lat = lat + lat_correction
    corrected_lon = lon + lon_correction

    return corrected_lat, corrected_lon

# Function to calculate new position based on speed and course
def calculate_new_position(lat, lon, speed, course, time_diff):
    distance = speed * time_diff
    course = np.deg2rad(course)

    delta_lat = distance * np.cos(course) / 60.0
    delta_lon = distance * np.sin(course) / (60.0 * np.cos(np.deg2rad(lat)))

    new_lat = lat + delta_lat
    new_lon = lon + delta_lon

    return new_lat, new_lon

# Function to plot on 3D globe
def plot_on_globe(lat, lon, assumed_positions, corrected_positions):
    fig = plt.figure(figsize=(15, 10))
    m = Basemap(projection='ortho', lon_0=lon, lat_0=lat, resolution='l')
    m.drawcoastlines()
    m.drawcountries()

    # Plot assumed positions
    for assumed_lat, assumed_lon in assumed_positions:
        x, y = m(assumed_lon, assumed_lat)
        m.plot(x, y, 'bo', markersize=8, label='Assumed Position')

    # Plot corrected positions
    for corrected_lat, corrected_lon in corrected_positions:
        x, y = m(corrected_lon, corrected_lat)
        m.plot(x, y, 'ro', markersize=8, label='Corrected Position')

    # Draw LOP lines
    for i in range(len(assumed_positions)):
        assumed_lat, assumed_lon = assumed_positions[i]
        corrected_lat, corrected_lon = corrected_positions[i]
        x_assumed, y_assumed = m(assumed_lon, assumed_lat)
        x_corrected, y_corrected = m(corrected_lon, corrected_lat)
        m.plot([x_assumed, x_corrected], [y_assumed, y_corrected], 'g--')

    plt.legend()
    plt.show()

def main():
    print("Celestial Navigation Software")

    # Input assumed position
    lat = float(input("Enter assumed latitude (degrees): "))
    lon = float(input("Enter assumed longitude (degrees): "))

    # Input vessel speed and course
    speed = float(input("Enter vessel speed (knots): "))
    course = float(input("Enter vessel course (degrees): "))

    assumed_positions = [(lat, lon)]
    corrected_positions = []

    # Input multiple observations
    while True:
        print("\nEnter observation data:")
        
        # Input observed altitude
        observed_alt = float(input("Enter observed altitude of the Sun (degrees): "))

        # Input observation time
        year = int(input("Enter observation year: "))
        month = int(input("Enter observation month: "))
        day = int(input("Enter observation day: "))
        hour = int(input("Enter observation hour (UTC): "))
        minute = int(input("Enter observation minute (UTC): "))
        second = int(input("Enter observation second (UTC): "))

        obs_time = datetime(year, month, day, hour, minute, second)
        time = (obs_time - datetime(obs_time.year, 1, 1)).total_seconds() / 86400.0

        # Perform position fix
        corrected_lat, corrected_lon = position_fix(observed_alt, lat, lon, time)
        corrected_positions.append((corrected_lat, corrected_lon))

        # Calculate new assumed position based on speed and course
        if len(corrected_positions) > 1:
            time_diff = (obs_time - prev_obs_time).total_seconds() / 3600.0  # Time difference in hours
            lat, lon = calculate_new_position(lat, lon, speed, course, time_diff)
            assumed_positions.append((lat, lon))

        prev_obs_time = obs_time

        more_obs = input("Do you want to add another observation? (yes/no): ").strip().lower()
        if more_obs != 'yes':
            break

    # Plot results on a 3D globe
    plot_on_globe(corrected_lat, corrected_lon, assumed_positions, corrected_positions)

if __name__ == "__main__":
    main()



