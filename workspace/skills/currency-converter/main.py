import argparse
import os
import sys
import httpx


def convert(amount: float, base: str, target: str) -> str:
    api_key = os.getenv("EXCHANGERATE_API_KEY")
    if not api_key:
        return "Error: EXCHANGERATE_API_KEY environment variable is not set."

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base.upper()}/{target.upper()}/{amount}"

    try:
        response = httpx.get(url, timeout=5)
        data = response.json()

        if data.get("result") != "success":
            error = data.get("error-type", "unknown error")
            return f"Error from API: {error}"

        converted = data["conversion_result"]
        rate = data["conversion_rate"]

        return (
            f"{amount} {base.upper()} = {converted:.2f} {target.upper()}\n"
            f"Exchange rate: 1 {base.upper()} = {rate} {target.upper()}"
        )

    except httpx.TimeoutException:
        return "Error: Request timed out."
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--amount", type=float, required=True, help="Amount to convert")
    parser.add_argument(
        "--from_currency", required=True, help="Base currency code e.g. USD"
    )
    parser.add_argument(
        "--to_currency", required=True, help="Target currency code e.g. INR"
    )
    args = parser.parse_args()

    print(convert(args.amount, args.from_currency, args.to_currency))
    sys.exit(0)
