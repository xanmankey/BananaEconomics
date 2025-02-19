# BananaEconomics
**ⓘ: The website is currently not hosted, but I still wanted to archive the code for comparison and organization.**
## Important Links
#### Video Demo:  https://youtu.be/HUKrki-4cYw
#### Website URL: https://xanmankey.pythonanywhere.com/
## BananaEconomics: A History
  One day as I was working on PSET9 finance, some friends asked what I was doing, and then we began to have a conversation about the website, the stock market, and how it would be a fun competitive thing to do. After a few emails, lots of debugging and error testing, a little frustration and googling, I ended up with BananaEconomic$, my personalized take on the CS50 Finance website!
## BananaEconomics: A Breakdown
  This code is mainly for educational purposes; if you want to test it, you will need an api key for iexcloud.io, you can see steps for obtaining an api key at https://cs50.harvard.edu/x/2021/psets/9/finance/ underneath "Configuring" (thank you CS50)! Also, the server side files will update over time, and I may do occassional maintinence based on requests, but the files uploaded are the version as of December 1st, 2021.
  #### CS50 PSET9 Functionality
  The CS50 team was kind enough to provide me with a starting point, giving me a css file which I used, a layout file which I made some slight edits to, a database to store users and other information which I expanded upon, and an application file and some HTML templates, where I did most of my programming.
##### Register
  The Register function adds an entry to the users table in finance.db with significant information and initializes a session_id to validate to the program that the user is the current user is the owner of the created account. Once registered, a user is provided with $10,000.
##### Log in/Log out
  The log in and log out functions manipulate and validate session, as well as check against the datatable using session['user_id'] as an indicator to check if the user is logged in or not. I also added basic censorship for certain names using the better-profanity python module.
##### Quote
  The Quote function uses the IEX stock index and the predefined function (thanks again, CS50) lookup in helpers.py to return stock name, price , and symbol when a stock symbol is inputted.
##### Buy
  The Buy function uses the lookup function defined above to purchase stocks based on the simulation. Your portfolio is updated upon the purchasing of a stock. Purchases are tracked in the purchases table in finance.db.
##### Sell
  The Sell function accesses the stocks in your portfolio and allows you to sell your shares of a particular stock if you so choose. Sales are tracked in the purchases table in finance.db.
##### History
  The History function returns the purchases table for the user to view their previous transactions. The time column in the table is in UTC (Coordinated Universal Time).
##### Portfolio
  The Portfolio function returns the users current stock index, total cash, total loans (which will be discussed below) on GET, and notifies you whether a stock has gone up or down from your original purchasing point based on color scheme (red = loss, green = profit). I also added a liquidate button, for those who want to cash in their earnings.
##### Apology
  Returns an apology providing information regarding the error or a message of some sort
##### Lookup
  Access and get data from the IEX database by inputting a stock symbol
  
#### New Functionality
##### Delete User
  The Delete User function adds an entry to the deleted table in finance.db, and returns a Deltarune reference if you try to login using that user again (I didn't want to delete the data, just so I had a way to back it up just in case someone deleted their account; I also added a warning in deleted.html just to notify users what would happen if they inputted their username into the form).
##### Top Ten
  The ranking system (my main drive behind my ideas for the website) is in the form of the Top Ten and Bottom Ten functions. I combine the users portfolio value, cash, and loans into a total value, and rank the users using that value. It also provides the users with a notification of how many 🍌 they owe, primarily because the more you see your loans, the more inclined you will be to get them paid off in one way or another. I added the Bottom Ten function because I was recently alerted to an exploit regarding integer overflow, and I am curious how far the website can be broken in that regard (right now it's essentially a testing page for myself and others).
##### Servitude
  Another reason I included the amount owed in the Top Ten and Bottom Ten pages was because I had gotten many tips that the interest rate (2% per day) was a high rate in regards to the amount of profit, and discouraged the use of the loan system. The Servitude function exists as a counterbalance, where it is essentially a clicker that pays off one cent of your loan each click (up to a max of $5 per work session, and NEED TO ADD AUTOCLICKER CHECK to prevent autoclicking and macros).
##### Achievements
  Achievements are bonuses or rewards for solving my riddles or accomplishing certain feats on the website. They give the user cash bonuses (relative to the difficulty of the achievement in certain cases) and incentivize exploring and using the website. Solutions can be found in the code if you get tired of searching, but otherwise I wish you luck on your achievement hunt!
##### Get a Loan
  Getting a loan allows you to increase the return of your portfolio, but it also creates a balance by increasing risk (in the form of interest) as well. I store and update the loan amount (using real time) on user logins, I also decided to add (more like disguise as in this case though) a Christmas bonus for those that hadn't logged in for a while, if they log in on January 1st, I wipe all their accrued interest away. This was the first page I added music to, and, after a group poll (because I couldn't decide whether music that autoplays was annoying or not) I opted that it's better to add it for people that want it, and people that don't can mute the tab or their computer audio.
##### Pay Loan
  The Pay Loan function allows you to pay off your loans and get rid of that pesky debt. 
  
## Ideas
  I still have ideas for this website, although I haven't decided whether I want to implement them or move on yet. I took up almost the entirety of the navbar however, and that, along with people having fun and being competitive and strategic on the website, has given me some closure for this project. I may add new functionality (achievements, pages, and more) in the future though, I will update the readMe if I ever decide to do so! If you have any ideas, feel free to reach out and let me know!

## Credits
- A special thanks to the CS50 team for getting me started on my coding journey! I'd never be where I was without you.
- Thanks to IEX for a quick and easy way to access a simulated stock index!
- Thanks to Toby Fox, for making Deltarune chapter 1 and 2, which I referenced and used media from throughout (Seen in the static folder).
- Thanks to my friends, for helping me test and debug my website, catching many errors that I would've overlooked otherwise.
