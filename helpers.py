import os
# requests is a simple python library that allows you to send HTTP requests easily
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


# REMEMBER: the @ sign is basically just a decarator used to pass arguments to the function or method mentioned in the @ sign
# REMEMBER # 2: self (common usage: self.) represents the instance of the class, so if you create a new instance, it refers to that new instance (I believe)
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    # requests.RequestException means there was an ambiguous exception that occured while handling your request; if this passes, there is likely a different error in your code
    except requests.RequestException:
        return None # This is the error call that is being returned
        # I don't quite understand why; I think my API is correct; maybe reddit sources will help

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        print(2)
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
