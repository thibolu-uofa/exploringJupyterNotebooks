"""This script gets the raw location data for a given location string using geocoding.
After the raw location is encoutnered, it gets the country name from latitude and longitude 
coordinates using reverse geocoding. This codes gets the country/location of
contributors for Notebook and Python dataset splits (for Software Engineering
and educational purposes).

You can run this script with the command:

python -m research_questions.src.contributors.get_contributors_info

from inside the main  directory of this project."""

import pandas as pd
from research_questions.configs.configs import Configs
from pathlib import Path
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderServiceError, GeocoderInsufficientPrivileges
import requests_cache


def get_raw_location(location_str, geocode):

    try:
        location = geocode(location_str)
        if location:
            raw_location = location.raw

            return raw_location
        else:
            print(f"Coordinates not found")
            return None

    except (GeocoderTimedOut, GeocoderServiceError,
            GeocoderInsufficientPrivileges, Exception) as e:

        print(f"Geocoding error: {e}")
        time.sleep(1)
        return None


def get_country_from_coordinates(lat, lon, reverse):
    try:
        location = reverse((lat, lon), language='en')
        if location:
            address = location.raw['address']
            country = address.get('country')

            return country
        else:
            print(f"Country not found")
            return None

    except (GeocoderTimedOut, GeocoderServiceError,
            GeocoderInsufficientPrivileges, Exception) as e:

        print(f"Geocoding error: {e}")
        return None


def process_country(location_str: str, email) -> str:

    if not location_str:
        return 'unknown'

    requests_cache.install_cache('geocoding_cache', expire_after=86400)
    geolocator = Nominatim(user_agent=config.email)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=5)
    reverse = RateLimiter(geolocator.reverse, min_delay_seconds=5)

    try:
        raw_location = get_raw_location(location_str, geocode)

        if raw_location:

            latitude = raw_location['lat']
            longitude = raw_location['lon']

            country = get_country_from_coordinates(
                latitude, longitude, reverse)

            if country:
                return country
            else:
                return 'geopy could not find'
        else:
            return 'geopy could not find'
    except Exception as e:

        print(f"Geocoder exception: {e}")
        return f'geocoder error'


def load_dataset(split):

    contributors_path = Path(Path.cwd(), "research_questions", "src",
                             "contributors")

    if split == 'SE':
        # contributors for SE purpose repos with notebooks:
        contributors_file = contributors_path / "contributors_data_SE.csv"

    if split == 'non_SE':
        contributors_file = contributors_path / "contributors_data_non_SE.csv"

    if split == 'SE_py':
        contributors_file = contributors_path / "contributors_data_SE_py.csv"

    if split == 'non_SE_py':
        contributors_file = contributors_path / "contributors_data_non_SE_py.csv"

    df = pd.read_csv(contributors_file)

    return df


def get_country_from_df(df, email):

    countries = []
    for index, row in df.iterrows():

        if pd.isna(row['location']):
            country = 'absent location in GitHub'
        else:
            country = process_country(row['location'], email)

        countries.append(country)
        print(f"number of contributors parsed: {index+1} out of {len(df)}")

    df['country'] = countries

    return df


def save_results_in_csv(df, split):

    results_path = Path(Path.cwd(), "research_questions",
                        "src", "contributors")

    csv_filename = 'country_contributors_' + split + '.csv'
    csv_filepath = results_path / csv_filename

    df.to_csv(csv_filepath, index=False, encoding='utf-8')

    print(
        f"Contributors country information has been written to {csv_filename}")


if __name__ == '__main__':

    config = Configs()
    # Uncomment the desired split to get data from it:
    # split = "non_SE_py"
    # split = "SE_py"
    # split = "non_SE"
    split = "SE"
    df = load_dataset(split)
    df = get_country_from_df(df, email=config.email)

    save_results_in_csv(df, split)
