import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from better_profanity import profanity

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database
db = SQL("sqlite:////home/xanmankey/mysite/finance/finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Liquidate/sell all
    if request.method == "POST":
        stockSymboltmp = db.execute('SELECT DISTINCT symbol FROM purchases WHERE id = ?', session['user_id'])
        if len(stockSymboltmp) == 0:
            return apology("no stocks to sell")
        stockSymbol = [None] * len(stockSymboltmp)
        portfolioTotal = 0
        totalPrice = [None] * len(stockSymboltmp)
        i = 0
        for stock in stockSymbol:
            stock = lookup(stockSymboltmp[i]['symbol'])
            numSharestmp = db.execute("SELECT SUM(shares) FROM purchases WHERE symbol = ? AND id = ?", stockSymboltmp[i]['symbol'], session['user_id'])
            numShares = int(numSharestmp[0]['SUM(shares)'])
            totalPrice[i] = float(stock['price']) * numShares
            portfolioTotal += totalPrice[i]
            db.execute('INSERT INTO purchases (id, symbol, shares, transactions, price, time) VALUES (?, ?, ?, ?, ?, ?)', session['user_id'], stockSymboltmp[i]['symbol'], -numShares, "sold", -totalPrice[i], str(datetime.datetime.now()))
            i += 1
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])
        db.execute("UPDATE users SET cash = ? WHERE id = ?", float(cash[0]['cash']) + portfolioTotal, session['user_id'])
        return redirect('/')


    # Displays the stocks (stock symbol, then actual company) the user owns, the num of shares, the current price of each share, and the total value (shares * price)
    else:
        # Use global error to return messages regarding banana harvesting
        if 'error' in globals():
            global error
            global m
            if error == 1 and m == 1:
                flash("Thanks for all you're hard work and volunteering! Unfortunately, we only pay indentured servants...", category='error')

            elif error == 2 and m == 1:
                flash("I don't know how you managed to break the bank, but your credit score is something", category='error')
            m += 1


        achievements = db.execute("SELECT * FROM achievements WHERE achieved = ? AND user_id = ?", "ACHIEVED!!!", session['user_id'])
        # Unlocks small rewards if you get all the achievements (namely a star in front of your name and mario brothers music on your portfolio screen)
        if len(achievements) == 10:
            achieved = 0
        else:
            achieved = 1
        stockSymbol = db.execute('SELECT DISTINCT symbol FROM purchases WHERE id = ?', session['user_id'])
        bananas = db.execute('SELECT bananas FROM users WHERE id = ?', session['user_id'])
        bananas = bananas[0]['bananas']
        if bananas:
            bananaTime = db.execute('SELECT bananaTime FROM users WHERE id = ?', session['user_id'])
            bananaTime = int(bananaTime[0]['bananaTime'])
            interest = datetime.datetime.now().timetuple().tm_yday - bananaTime
            # Base case: First day of the year (Late Christmas gift)!
            if datetime.datetime.now().timetuple().tm_yday == 1:
                db.execute('UPDATE users SET bananaTime = ? WHERE id = ?', 1, session['user_id'])
                bananaTime = db.execute('SELECT bananaTime FROM users WHERE id = ?', session['user_id'])
                interest = datetime.datetime.now().timetuple().tm_yday - bananaTime
            # Update interest based on the number of days since last login
            if bananas != 0 and interest != 0:
                for i in range(interest):
                    bananas = bananas * 1.02
                db.execute('UPDATE users SET bananas = ? WHERE id = ?', bananas, session['user_id'])
                bananaTime += 1
                db.execute('UPDATE users SET bananaTime = ? WHERE id = ?', bananaTime, session['user_id'])
        # Initialize and fill arrays w/ important data regarding the portfolio, including:
        # Name, shares, price, and totalPrice
        stockName = [None] * len(stockSymbol)
        stockSharesTmp = [None] * len(stockSymbol)
        stockShares = [None] * len(stockSymbol)
        stockPrice = [None] * len(stockSymbol)
        totalPrice = [None] * len(stockSymbol)
        stockSymbolStore = [None] * len(stockSymbol)
        transactionstmp = [None] * len(stockSymbol)
        transactions = [None] * len(stockSymbol)
        i = 0
        j = 0
        portfolioTotal = 0
        cash = db.execute('SELECT cash FROM users WHERE id = ?', session['user_id'])
        for stock in stockSymbol:
            tmp = db.execute("SELECT SUM(shares) FROM purchases WHERE symbol = ? AND id = ?", stockSymbol[i]['symbol'], session['user_id'])
            if tmp[0]['SUM(shares)'] == 0:
                i += 1
                j += 1
            else:
                stock = lookup(stockSymbol[i]['symbol'])
                stockSymbolStore[i] = stockSymbol[i]['symbol']
                stockName[i] = stock['name']
                stockSharesTmp[i] = db.execute("SELECT SUM(shares) FROM purchases WHERE symbol = ? AND id = ?", stockSymbol[i]['symbol'], session['user_id'])
                stockShares[i] = stockSharesTmp[i][0]['SUM(shares)']
                stockPrice[i] = stock['price']
                transactionstmp[i] = db.execute("SELECT DISTINCT price FROM purchases WHERE symbol = ? AND id = ? ORDER BY time DESC", stockSymbol[i]['symbol'], session['user_id'])
                transactions[i] = float(transactionstmp[i][0]['price'])
                totalPrice[i] = round(float(stockPrice[i]) * float(stockSharesTmp[i][0]['SUM(shares)']), 2)
                portfolioTotal += totalPrice[i]
                stockPrice[i] = float(stockPrice[i])
                totalPrice[i] = usd(totalPrice[i])
                i += 1
        if bananas:
            portfolioTotal = round(portfolioTotal - bananas)
        else:
            portfolioTotal = round(portfolioTotal)
        db.execute('UPDATE users SET totalValue = ? WHERE id = ?', portfolioTotal + cash[0]['cash'], session['user_id'])

        # Achievement 2
        achieve = db.execute("SELECT achieved FROM achievements WHERE user_id = ? AND id = 2", session['user_id'])
        cash = db.execute('SELECT cash FROM users WHERE id = ?', session['user_id'])
        if len(stockSymbol) >= 20 and achieve[0]['achieved'] != 'ACHIEVED!!!':
            registered = db.execute("SELECT achievement FROM achievements WHERE user_id = ? AND id = 2", session['user_id'])
            flash(registered[0]['achievement'])
            db.execute("UPDATE achievements SET achieved = ? WHERE id = 2 AND user_id = ?", "ACHIEVED!!!", session['user_id'])
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash[0]['cash'] + 500, session['user_id'])

        # Achievement 8
        achieve = db.execute("SELECT achieved FROM achievements WHERE user_id = ? AND id = 8", session['user_id'])

        if portfolioTotal + cash[0]['cash'] >= 50000 and achieve[0]['achieved'] != 'ACHIEVED!!!':
            registered = db.execute("SELECT achievement FROM achievements WHERE user_id = ? AND id = 2", session['user_id'])
            flash(registered[0]['achievement'])
            db.execute("UPDATE achievements SET achieved = ? WHERE id = 8 AND user_id = ?", "ACHIEVED!!!", session['user_id'])
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash[0]['cash'] + 500, session['user_id'])

        # Functionality for displaying your current rank on the website if you aren't in the top or bottom ten
        totalUsers = db.execute("SELECT username FROM users")
        userPlacement = db.execute("SELECT username FROM users WHERE totalValue >= ?", portfolioTotal + cash[0]['cash'])


        # NOTE: I rounded the money amounts, for any money application that is inexcusable, but this is casual enough that it doesn't matter
        return render_template("index.html", j=j, i=i, numUsers=len(totalUsers), placement=len(userPlacement), achieved=achieved, stocks=stockSymbol, symbol=stockSymbolStore, name=stockName, shares=stockShares, price=stockPrice, totalPrice=totalPrice, portfolioTotal=portfolioTotal, cash=round(cash[0]['cash']), transactions=transactions)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # Buy any number of any stock
        stockSymbol = request.form.get('symbol')
        if not lookup(stockSymbol) or lookup(stockSymbol) == 'None':
            return apology("Sorry that stock does not exist")
        stockShares = request.form.get('shares')
        try:
            int(stockShares)
        except ValueError:
            return apology("Not an integer")
        # Prevent integer overflow
        if int(stockShares) <= 0:
            return apology("Insufficient number of shares")
        stock = lookup(stockSymbol)
        price = stock['price'] * int(stockShares)
        userId = session['user_id']
        cash = db.execute('SELECT cash FROM users WHERE id = ?', userId)
        if price > cash[0]['cash']:
            return apology("Insufficient funds")
        newFunds = cash[0]['cash'] - price

        db.execute("INSERT INTO purchases (id, symbol, shares, transactions, price, time) VALUES (?, ?, ?, ?, ?, ?)", userId, stockSymbol.upper(), stockShares, "bought", price, str(datetime.datetime.now()))
        db.execute("UPDATE users SET cash = ? WHERE id = ?", newFunds, session['user_id'])

        return redirect('/')


    else:
        return render_template('buy.html')


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Show history of transactions"""
    if request.method == 'POST':

        # Achievement 9
        # Called if the linked ED is clicked
        registered = db.execute("SELECT achievement FROM achievements WHERE user_id = ? AND id = 9", session['user_id'])
        flash(registered[0]['achievement'])
        db.execute("UPDATE achievements SET achieved = ? WHERE id = 9 AND user_id = ?", "ACHIEVED!!!", session['user_id'])
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash[0]['cash'] + 1000, session['user_id'])
        return redirect('/')
    else:

        # Return whether a stock was bought or sold, symbol, sale price, number of shares bought or sold, and date and time
        stockSymboltmp = db.execute("SELECT symbol FROM purchases WHERE id = ? ORDER BY time DESC", session['user_id'])
        symbol = [None] * len(stockSymboltmp)
        stockName = [None] * len(stockSymboltmp)
        stockSharesTmp = [None] * len(stockSymboltmp)
        stockShares = [None] * len(stockSymboltmp)
        totalPrice = [None] * len(stockSymboltmp)
        timestmp = db.execute("SELECT time FROM purchases WHERE id = ? ORDER BY time DESC", session['user_id'])
        times = [None] * len(stockSymboltmp)
        transactionstmp = db.execute("SELECT transactions FROM purchases WHERE id = ? ORDER BY time DESC", session['user_id'])
        purchases = [None] * len(stockSymboltmp)
        transactions = [None] * len(stockSymboltmp)
        for i in range(len(stockSymboltmp)):
            symbol[i] = stockSymboltmp[i]['symbol']
            # Achievement 9 check 1
            if str(symbol[i]) == 'ED':
                achieve = db.execute("SELECT achieved FROM achievements WHERE user_id = ? AND id = 9", session['user_id'])
                achieved = True
                achieveNum = i
            else:
                try: int(achieved)

                except UnboundLocalError:
                    achieve = db.execute("SELECT achieved FROM achievements WHERE user_id = ? AND id = 9", session['user_id'])
                    achieved = False
            stock = lookup(symbol[i])
            stockName[i] = stock['name']
            purchase = db.execute("SELECT price FROM purchases WHERE id = ? AND symbol = ? ORDER BY time DESC", session['user_id'], symbol[i])
            purchases[i] = abs(float(purchase[0]['price']))
            stockSharesTmp[i] = db.execute("SELECT shares FROM purchases WHERE symbol = ? ORDER BY time DESC", symbol[i])
            stockShares[i] = abs(stockSharesTmp[i][0]['shares'])
            # abs(stockSharesTmp[i][0]['shares'])
            totalPrice[i] = round(purchases[i] * float(stockShares[i]), 2)
            time = timestmp[i]['time']
            size = len(time)
            times[i] = time[:size - 7]
            transactions[i] = transactionstmp[i]['transactions']

        # Achievement 9
        if achieved == True and achieve[0]['achieved'] != 'ACHIEVED!!!':
            print("This calls...")
            # Make the ED symbol glow
            return render_template('history.html', stocks=len(symbol), name=stockName, LIGHT=achieveNum, symbol=symbol, shares=stockShares, transactions=transactions, price=purchases, totalPrice=totalPrice, time=times)

        return render_template('history.html', stocks=len(symbol), name=stockName, symbol=symbol, shares=stockShares, transactions=transactions, price=purchases, totalPrice=totalPrice, time=times)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        deletedtmp = db.execute("SELECT username FROM deleted")
        deleted = [None] * len(deletedtmp)
        for i in range(len(deletedtmp)):
            deleted[i] = deletedtmp[i]['username']

        # Ensure username was submitted
        if request.form.get("username") in deleted:
            return render_template("deleted.html")

        elif not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Initializing achievements for those who already have accounts (I added achievements later on) or a failsafe just in case exploits cause further glitches
        anyachievers = db.execute("SELECT * FROM achievements WHERE user_id = ?", session['user_id'])
        if anyachievers == []:
            achievements = ['some new FUNds', 'Diversify', 'Make a deal with the devil', 'An explosive commodity', 'The house always wins', '🍌 $', 'Time to be a [[ big shot ]]', 'Achieve a total value of 50000', 'An elder that lights up the way', '☝︎✌︎☼︎👌︎✌︎☝︎☜︎ ☠︎⚐︎✋︎💧︎☜']
            for i in range(len(achievements)):
                db.execute("INSERT INTO achievements VALUES (?, ?, ?, ?)", i + 1, session['user_id'], achievements[i], "not achieved...")
            db.execute("UPDATE achievements SET achieved = ? WHERE user_id = ?", "ACHIEVED!!!", session['user_id'])

        return redirect("/")


    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        # Use the provided lookup function to cross-check the stock symbol with the IEX database and return values, including:
        # Name, price, and symbol
        stockSymbol = request.form.get('symbol')
        stocks = lookup(stockSymbol)
        if not stocks:
            return apology("invalid stock symbol")

        # Achievement 4
        achieve = db.execute("SELECT achieved FROM achievements WHERE user_id = ? AND id = 4", session['user_id'])
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])

        if str(stockSymbol) == 'BOOM' and achieve[0]['achieved'] != 'ACHIEVED!!!':
            registered = db.execute("SELECT achievement FROM achievements WHERE user_id = ? AND id = 4", session['user_id'])
            flash(registered[0]['achievement'])
            db.execute("UPDATE achievements SET achieved = ? WHERE id = 4 AND user_id = ?", "ACHIEVED!!!", session['user_id'])
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash[0]['cash'] + 500, session['user_id'])
            return render_template("quoted.html", stocks=stocks, price=usd(stocks['price']))

        # Achievement 10
        achieve = db.execute("SELECT achieved FROM achievements WHERE user_id = ? AND id = 10", session['user_id'])

        if str(stockSymbol) == 'WM' and achieve[0]['achieved'] != 'ACHIEVED!!!':
            registered = db.execute("SELECT achievement FROM achievements WHERE user_id = ? AND id = 10", session['user_id'])
            flash(registered[0]['achievement'])
            db.execute("UPDATE achievements SET achieved = ? WHERE id = 10 AND user_id = ?", "ACHIEVED!!!", session['user_id'])
            cash = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])
            cash = cash[0]['cash']
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash[0]['cash'] + 500, session['user_id'])
            return render_template("quoted.html", stocks=stocks, price=usd(stocks['price']))

        return render_template("quoted.html", stocks=stocks, price=usd(stocks['price']))


    else:
        return render_template("quote.html")


# Normally, in any monetarty app this is sensitive information, but I figured I would implement it for fun
@app.route("/topten", methods=["GET"])
@login_required
def topTen():
    # The Forbes 10
    db.execute("UPDATE users SET bananas = 0 WHERE bananas is NULL")
    topTentmp = db.execute("SELECT username, totalValue, bananas FROM users GROUP BY username ORDER BY totalValue DESC LIMIT 10")
    topTenUser = [None] * len(topTentmp)
    topTenValue = [None] * len(topTentmp)
    bananas = [None] * len(topTentmp)
    achieved = [None] * len(topTentmp)
    for i in range(len(topTentmp)):
        topTenUser[i] = topTentmp[i]['username']
        userId = db.execute("SELECT id FROM users WHERE username = ?", topTenUser[i])
        bananas[i] = topTentmp[i]['bananas']
        topTenValue[i] = float(topTentmp[i]['totalValue'])
        achievements = db.execute("SELECT * FROM achievements WHERE achieved = ? AND user_id = ?", "ACHIEVED!!!", userId[0]['id'])
        if len(achievements) == 10:
            achieved[i] = 0
        else:
            achieved[i] = 1
    return render_template("topten.html", achieved=achieved, length=topTentmp, username=topTenUser, portfolioValue=topTenValue, bananas=bananas)


@app.route("/bottomten", methods=["GET"])
@login_required
def bottomTen():
    # Included to benefit people who found exploits, as well as punish those who cause integer overflow trying to take advantage of said exploits
    db.execute("UPDATE users SET bananas = 0 WHERE bananas is NULL")
    # Initialization if not yet initialized
    db.execute("UPDATE users SET totalValue = 10000 WHERE totalValue is NULL")
    topTentmp = db.execute("SELECT username, totalValue, bananas FROM users GROUP BY username ORDER BY totalValue ASC LIMIT 10")
    topTenUser = [None] * len(topTentmp)
    topTenValue = [None] * len(topTentmp)
    bananas = [None] * len(topTentmp)
    for i in range(len(topTentmp)):
        topTenUser[i] = topTentmp[i]['username']
        bananas[i] = topTentmp[i]['bananas']
        topTenValue[i] = float(topTentmp[i]['totalValue'])# - float(bananas[i])
    return render_template("bottomten.html", length=topTentmp, username=topTenUser, portfolioValue=topTenValue, bananas=bananas)


# Option to delete the user
@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "POST":
        # Add the user to the deleted table; cross-checked when users login
        username = request.form.get('username')
        userIdtmp = db.execute("SELECT id FROM users WHERE username = ?", username)
        userId = userIdtmp[0]['id']
        if session['user_id'] == userId:
            db.execute("INSERT INTO deleted (id, username) VALUES (?, ?)", session['user_id'], username)
            db.execute('DELETE FROM users WHERE username = ?', username)
            db.execute('DELETE  FROM purchases WHERE id = ?', session['user_id'])
            return(render_template("deleted.html"))
        else:
            return apology("Cannot delete that user")


    else:
        return render_template("delete.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    # Get the username and password from the form if the user is posting information
    if request.method == "POST":
        usernametmp = db.execute("SELECT username FROM users")
        usernames = [None] * len(usernametmp)

        for i in range(len(usernametmp)):
            usernames[i] = usernametmp[i]['username']

        if not request.form.get('username'):
            return apology("Invalid username")
        # Routine checks for passwords
        elif not request.form.get('password'):
            return apology("Invalid password")
        elif request.form.get('password') != request.form.get('confirmation'):
            return apology("Passwords do not match")
        elif request.form.get("username") in usernames:
            return apology("Sorry, that username is already taken")
        elif "🌟" in request.form.get("username"):
            return apology("Sorry, you don't qualify as a star just yet")
        elif len(request.form.get('username')) > 20:
            return apology("Sorry, usernames must be less than 20 characters long!")
        # Passwords are then hashed to an id and stored for safety reasons
        profanity.load_censor_words()
        user = request.form.get('username')
        user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", profanity.censor(user),
        generate_password_hash(request.form.get('password')))

        # Check if a user with that id already exists
        if not user:
            return apology('Someone already has this user id')

        # Assign the user_id to user and get the id
        rows = db.execute("SELECT id FROM users WHERE username = ?", request.form.get('username'))
        session["user_id"] = rows[0]["id"]
        # After database has been updated redirect to home
        achievements = ['some new FUNds', 'Diversify', 'Make a deal with the devil', 'An explosive commodity', 'The house always wins', '🍌 $', 'Time to be a [[ big shot ]]', 'Achieve a total value of 50000', 'An elder that lights up the way', '☝︎✌︎☼︎👌︎✌︎☝︎☜︎ ☠︎⚐︎✋︎💧︎☜']
        for i in range(len(achievements)):
            db.execute("INSERT INTO achievements VALUES (?, ?, ?, ?)", i + 1, session['user_id'], achievements[i], "not achieved...")

        registered = db.execute("SELECT achievement FROM achievements WHERE user_id = ? AND id = 1", session['user_id'])

        # Achievement 1
        db.execute("UPDATE achievements SET achieved = ? WHERE id = 1 AND user_id = ?", "ACHIEVED!!!", session['user_id'])
        flash(registered[0]['achievement'])
        return redirect('/')


    elif request.method == "GET":
        # Allow the user to register a new account, and update users database and sessions accordingly
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # Get the share and current price, and update user cash, portfolio, and tracked purchases accordingly
        stockSymbol = request.form.get('symbol')
        numOfSharestmp = db.execute("SELECT SUM(shares) FROM purchases WHERE symbol = ?", stockSymbol)
        numOfShares = numOfSharestmp[0]['SUM(shares)']
        shareSell = request.form.get('shares')
        try:
            int(shareSell)
        except ValueError:
            return apology("Not an integer")
        if int(shareSell) > numOfShares:
            return apology("Not enough shares")
        tmp = lookup(stockSymbol)
        cash = tmp['price']
        fundstmp = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])
        funds = fundstmp[0]['cash']
        totalPrice = cash * numOfShares
        sellShares = cash * int(shareSell)
        newFunds = funds + float(sellShares)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", newFunds, session['user_id'])
        db.execute('INSERT INTO purchases (id, symbol, shares, transactions, price, time) VALUES (?, ?, ?, ?, ?, ?)', session['user_id'], stockSymbol, -int(shareSell), "sold", -totalPrice, str(datetime.datetime.now()))
        return redirect('/')


    else:
        # Give the user the option to sell shares of any of their stocks
        symbolstmp = db.execute('SELECT DISTINCT symbol FROM purchases WHERE id = ?', session['user_id'])
        symbols = [None] * len(symbolstmp)
        for i in range(len(symbolstmp)):
            symbols[i] = symbolstmp[i]['symbol']
        return render_template("sell.html", symbols=symbols)

@app.route("/getloan", methods=["GET", "POST"])
@login_required
def loan():
    if request.method == "POST":
        # Check loan amount, prior loans, and prior cash
        loanAmount = request.form.get('loanAmount')
        if int(float(loanAmount)) <= 0:
            return apology("Invalid loan amount")
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])
        cash = cash[0]['cash']
        db.execute("UPDATE users SET bananas = 0 WHERE bananas is NULL")
        bananas = db.execute("SELECT bananas FROM users WHERE id = ?", session['user_id'])
        bananas = bananas[0]['bananas']

        # 1000000 loan cap is fair
        if bananas >= 1000000 or float(loanAmount) >= 1000000:
            return apology("Sorry, your credit score isn't good enough, too many bananas")
        db.execute("UPDATE users SET cash = ? WHERE id = ?", float(cash) + float(loanAmount), session['user_id'])
        db.execute("UPDATE users SET bananas = ? WHERE id = ?", float(loanAmount) + float(bananas), session['user_id'])

        # Achievement 3
        achieve = db.execute("SELECT achieved FROM achievements WHERE user_id = ? AND id = 3", session['user_id'])
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])
        if float(loanAmount) == 666.0 and achieve[0]['achieved'] != 'ACHIEVED!!!':
            registered = db.execute("SELECT achievement FROM achievements WHERE user_id = ? AND id = 3", session['user_id'])
            flash(registered[0]['achievement'])
            db.execute("UPDATE achievements SET achieved = ? WHERE id = 3 AND user_id = ?", "ACHIEVED!!!", session['user_id'])
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash[0]['cash'] + 500, session['user_id'])
            return redirect('/')

        # Achievement 6
        achieve = db.execute("SELECT achieved FROM achievements WHERE user_id = ? AND id = 6", session['user_id'])

        if float(loanAmount) == 19.0 and achieve[0]['achieved'] != 'ACHIEVED!!!':
            registered = db.execute("SELECT achievement FROM achievements WHERE user_id = ? AND id = 6", session['user_id'])
            flash(registered[0]['achievement'])
            db.execute("UPDATE achievements SET achieved = ? WHERE id = 6 AND user_id = ?", "ACHIEVED!!!", session['user_id'])
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash[0]['cash'] + 500, session['user_id'])
            return redirect('/')

        # Achievement 7
        achieve = db.execute("SELECT achieved FROM achievements WHERE user_id = ? AND id = 7", session['user_id'])

        if float(loanAmount) == 1997.0 and achieve[0]['achieved'] != 'ACHIEVED!!!':
            registered = db.execute("SELECT achievement FROM achievements WHERE user_id = ? AND id = 7", session['user_id'])
            flash(registered[0]['achievement'])
            db.execute("UPDATE achievements SET achieved = ? WHERE id = 7 AND user_id = ?", "ACHIEVED!!!", session['user_id'])
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash[0]['cash'] + 500, session['user_id'])
            return redirect('/')

        return redirect('/')


    else:
        db.execute("UPDATE users SET bananas = 0 WHERE bananas is NULL")
        db.execute("UPDATE users SET bananaTime = ? WHERE bananaTime is NULL", datetime.datetime.now().timetuple().tm_yday)
        return render_template("getloan.html")

@app.route("/payloan", methods=["GET", "POST"])
@login_required
def payloan():
    if request.method == "POST":
        # Pay off the loan using available funds
        amountPaid = request.form.get('amountPaid')
        try:
            float(amountPaid)
        except ValueError:
            return apology("NOT A VALID 🍌 AMOUNT")
        loanTotal = db.execute('SELECT bananas FROM users WHERE id = ?', session['user_id'])
        if float(amountPaid) > float(loanTotal[0]['bananas']):
            return apology("TOO MUCH 🍌")
        cash = db.execute('SELECT cash FROM users WHERE id = ?', session['user_id'])
        cash = cash[0]['cash']
        if float(amountPaid) > float(cash):
            return apology("NOT ENOUGH FUNDS")
        loanTotal = float(loanTotal[0]['bananas']) - float(amountPaid)
        db.execute('UPDATE users SET bananas = ? WHERE id = ?', loanTotal, session['user_id'])
        db.execute('UPDATE users SET cash = ? WHERE id  = ?', float(cash) - float(amountPaid), session['user_id'])

        # Achievement 5
        achieve = db.execute("SELECT achieved FROM achievements WHERE user_id = ? AND id = 5", session['user_id'])
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])

        if float(amountPaid) == 777.0 and achieve[0]['achieved'] != 'ACHIEVED!!!':
            registered = db.execute("SELECT achievement FROM achievements WHERE user_id = ? AND id = 5", session['user_id'])
            flash(registered[0]['achievement'])
            db.execute("UPDATE achievements SET achieved = ? WHERE id = 5 AND user_id = ?", "ACHIEVED!!!", session['user_id'])
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash[0]['cash'] + 500, session['user_id'])
            return redirect('/')

        return redirect('/')


    else:
        loanTotal = db.execute('SELECT bananas FROM users WHERE id = ?', session['user_id'])
        if loanTotal[0]['bananas'] > 0:
            return render_template('payloan.html')
        else:
            return redirect('/')

@app.route("/achievements")
@login_required
def achievements():
    # Check the user's achievements and their status
    achievements = db.execute("SELECT achievement FROM achievements WHERE user_id = ?", session['user_id'])
    achieved = db.execute("SELECT achieved FROM achievements WHERE user_id = ?", session['user_id'])
    achieve = [None] * len(achievements)
    theAchieved = [None] * len(achievements)
    for i in range(len(achievements)):
        achieve[i] = achievements[i]['achievement']
        theAchieved[i] = achieved[i]['achieved']
    return render_template('achievements.html', achievements=achieve, achieved=theAchieved)

@app.route("/bananaHarvest", methods=['GET', 'POST'])
@login_required
def bananaHarvest():
    # Counter keeping track of harvested bananas, your loan gets reduced once you have finished the job
    totalBananas = 0
    if request.method == 'POST':
        global m
        m = 0

        # Passing a js value using an ajax call
        bananas = request.json['item']
        totalBananas += bananas
        loans = db.execute("SELECT bananas FROM users WHERE id = ?", session['user_id'])
        loans = loans[0]['bananas']

        # Global variable used to trigger certian flask FLASH messages (popups)
        global error
        error = 0
        if loans == 0:
            totalBananas -= bananas
            error = 1
            return redirect('/')
        elif loans < 0:
            totalBananas -= bananas
            error = 2
            return redirect('/')

        # Half-measure to discourage autoclicking and key macros (not a full measure because there are other exploits, this helps balance them a little and rewards creativity)
        if totalBananas > 500:
            totalBananas -= bananas
            bananas = 500 - totalBananas
            loans -= bananas / 100
            if loans <= 0:
                loans = 0
            db.execute("UPDATE users SET bananas = ? WHERE id = ?", loans, session['user_id'])
        else:
            loans -= bananas / 100
            if loans <= 0:
                loans = 0
            db.execute("UPDATE users SET bananas = ? WHERE id = ?", loans, session['user_id'])

        return redirect('/')


    else:
        return render_template('harvest.html')

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == '__main__':
    app.run()
