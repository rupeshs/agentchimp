import argparse
import urllib.request
import json
import sys


def get_weather(city: str) -> str:
    url = f"https://wttr.in/{city.replace(' ', '+')}?format=j1"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read())

        current = data["current_condition"][0]
        temp_c = current["temp_C"]
        feels_like = current["FeelsLikeC"]
        description = current["weatherDesc"][0]["value"]
        humidity = current["humidity"]
        print(f"Weather in {city}: {description}")

        return (
            f"Weather in {city}: {description}\n"
            f"Temperature: {temp_c}°C (feels like {feels_like}°C)\n"
            f"Humidity: {humidity}%"
        )

    except Exception as e:
        return f"Error fetching weather for {city}: {e}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", required=True, help="City name")
    args = parser.parse_args()
    print(get_weather(args.city))
    sys.exit(0)
