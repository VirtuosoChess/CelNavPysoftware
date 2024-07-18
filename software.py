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

# Function to plot on 3D globe
def plot_on_globe(lat, lon, lines_of_position):
    fig = plt.figure(figsize=(10, 7))
    m = Basemap(projection='ortho', lon_0=lon, lat_0=lat)
    m.drawcoastlines()
    m.drawcountries()

    x, y = m(lon, lat)
    m.plot(x, y, 'bo', markersize=10)

    for lop in lines_of_position:
        lop_lat, lop_lon = lop
        x, y = m(lop_lon, lop_lat)
        m.plot(x, y, 'r.', markersize=5)
    
    plt.show()

def main():
    print("Celestial Navigation Software")

    # Input assumed position
    lat = float(input("Enter assumed latitude (degrees): "))
    lon = float(input("Enter assumed longitude (degrees): "))

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

    # Assume LOPs for demonstration
    lines_of_position = [(corrected_lat, corrected_lon)]

    # Plot results on a 3D globe
    plot_on_globe(corrected_lat, corrected_lon, lines_of_position)

if __name__ == "__main__":
    main()

