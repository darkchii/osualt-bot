import math
import os
import aiohttp

def calculateHeatIndex(temperature_c, humidity):
    tempF = convertCelsiusToFahrenheit(temperature_c)

    heatIndex = 0.5 + (tempF + 61.0 + ((tempF - 68.0) * 1.2) + (humidity * 0.094))

    if heatIndex >= 80:
        heatIndex = -42.379 + 2.04901523 * tempF + 10.14333127 * humidity - 0.22475541 * tempF * humidity - 6.83783e-3 * tempF * tempF - 5.481717e-2 * humidity * humidity + 1.22874e-3 * tempF * tempF * humidity + 8.5282e-4 * tempF * humidity * humidity - 1.99e-6 * tempF * tempF * humidity * humidity

    return convertFahrenheitToCelsius(heatIndex)

def calculateWindChill(temperature_c, wind_speed_kmh):
    if (temperature_c > 10 or wind_speed_kmh < 4.8):
        return temperature_c
    
    windSpeedMs = wind_speed_kmh / 3.6  # Convert km/h to m/s
    return 13.12 + 0.6215 * temperature_c - 11.37 * (windSpeedMs ** 0.16) + 0.3965 * temperature_c * (windSpeedMs ** 0.16)

def calculateRealFeel(temperature_c, humidity, wind_speed_kmh):
    feelsLike = temperature_c

    if(temperature_c > 20):
        feelsLike = calculateHeatIndex(temperature_c, humidity)
    elif(temperature_c < 10):
        feelsLike = calculateWindChill(temperature_c, wind_speed_kmh)

    # TODO: Solar radiation

    return feelsLike

def convertCelsiusToFahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9/5) + 32

def convertFahrenheitToCelsius(fahrenheit):
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5/9

def convertKmhToMps(kmh):
    """Convert kilometers per hour to meters per second."""
    return kmh / 3.6

def calculateDewPoint(temperature_c, humidity):
    """Calculate the dew point in Celsius."""
    if humidity is None or temperature_c is None:
        return None
    a = 17.27
    b = 237.7
    alpha = ((a * temperature_c) / (b + temperature_c)) + (math.log(humidity / 100.0))
    dew_point_c = (b * alpha) / (a - alpha)
    return dew_point_c

def getWindDirectionLabel(degrees):
    """Get the wind direction label based on degrees."""
    if degrees is None:
        return "Unknown"
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    index = round(degrees / 22.5) % 16
    return directions[index]

def getAirQualityLabel(aqi):
    """Get the air quality label based on AQI."""
    if aqi is None:
        return "Unknown"
    if aqi == 1:
        return "Good"
    elif aqi == 2:
        return "Fair"
    elif aqi == 3:
        return "Moderate"
    elif aqi == 4:
        return "Poor"
    elif aqi == 5:
        return "Very Poor"
    else:
        return "Unknown"
    
def getBadAirQualityComponents(components):
    """Only returns the components that are currently responsible for the bad air quality."""
    _list = []

    ## SO2, NO2, PM10, PM2_5, O3, CO
    if components.get("so2", 0) > 250:
        _list.append("SO2")
    if components.get("no2", 0) > 150:
        _list.append("NO2")
    if components.get("pm10", 0) > 100:
        _list.append("PM10")
    if components.get("pm2_5", 0) > 50:
        _list.append("PM2.5")
    if components.get("o3", 0) > 140:
        _list.append("O3")
    if components.get("co", 0) > 9400:
        _list.append("CO")
    return _list

def getAirQualityComponentLabel(component):
    """Get the label for a specific air quality component."""
    labels = {
        "so2": "Sulfur Dioxide (SO2)",
        "no2": "Nitrogen Dioxide (NO2)",
        "pm10": "Particulate Matter 10 (PM10)",
        "pm2_5": "Particulate Matter 2.5 (PM2.5)",
        "o3": "Ozone (O3)",
        "co": "Carbon Monoxide (CO)"
    }
    return labels.get(component, component.upper())

def convertToBetterWeatherObject(name, weather, air_quality):
    """Convert raw weather data to a more usable format."""
    temp_c = weather.get("main", {}).get("temp")
    wind_speed_kmh = weather.get("wind", {}).get("speed") * 3.6  # Convert m/s to km/h
    wind_speed_mph = weather.get("wind", {}).get("speed") * 2.23694  # Convert m/s to mph
    real_feel_c = calculateRealFeel(temp_c, weather.get("main", {}).get("humidity"), wind_speed_kmh) if temp_c is not None else None
    return {
        "location": name,
        "temperature_c": temp_c,
        "temperature_f": convertCelsiusToFahrenheit(temp_c) if temp_c is not None else None,
        "humidity": weather.get("main", {}).get("humidity"),
        "pressure": weather.get("main", {}).get("pressure"),
        "wind_speed": weather.get("wind", {}).get("speed"),
        "description": weather.get("weather", [{}])[0].get("description"),
        "icon": weather.get("weather", [{}])[0].get("icon"),
        "timezone": weather.get("timezone"),
        "dt": weather.get("dt"),
        "country_code": weather.get("sys", {}).get("country", "Unknown"),
        "country_emoji": f":flag_{weather.get('sys', {}).get('country', 'unknown').lower()}:",
        "air_pressure": weather.get("main", {}).get("pressure"),
        "heat_index_c": real_feel_c,
        "heat_index_f": convertCelsiusToFahrenheit(real_feel_c) if real_feel_c is not None else None,
        # "heat_index_f": convertCelsiusToFahrenheit(heat_index_c) if heat_index_c is not None else None,
        "wind_speed_kmh": wind_speed_kmh,
        "wind_speed_mph": wind_speed_mph,
        "wind_direction": getWindDirectionLabel(weather.get("wind", {}).get("deg")),
        "air_quality": air_quality.get("list", [{}])[0].get("main", {}).get("aqi"),
        "air_quality_label": getAirQualityLabel(air_quality.get("list", [{}])[0].get("main", {}).get("aqi")),
        "bad_air_quality_components": getBadAirQualityComponents(air_quality.get("list", [{}])[0].get("components", {})),
        "air_quality_components": {getAirQualityComponentLabel(k): v for k, v in air_quality.get("list", [{}])[0].get("components", {}).items() if v is not None and v > 0}
    }

async def getApiResponse(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error fetching data from {url}: {response.status}")
                return None
            
async def getLatLong(location):
    key = os.getenv("OPENWEATHERMAP_API_KEY")
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={key}"
    data = await getApiResponse(url)
    if data and len(data) > 0:
        lat = data[0]['lat']
        lon = data[0]['lon']
        name = data[0]['name']
        return lat, lon, name
    else:
        print(f"Could not find location: {location}")
        return None, None, None

async def getWeatherData(location):
    key = os.getenv("OPENWEATHERMAP_API_KEY")
    lat, lon, name = await getLatLong(location)
    url_weather = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric"
    url_air_quality = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={key}"
    data_weather = await getApiResponse(url_weather)
    data_air_quality = await getApiResponse(url_air_quality)
    if data_weather:
        return convertToBetterWeatherObject(name, data_weather, data_air_quality)
    else:
        print(f"Could not retrieve weather data for {location}")
        return None