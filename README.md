# soccer_betting
This project will pull stats for the 5 major European soccer leagues and predict the best results to bet on based on expected goals (xG).
The xG stat is used to predict how many goals each team will score in a given match.
That number is then fed into a Poisson distribution and 10,000 matches are simulated based on the output.
The probability of each result (Home Win, Away Win, Draw) is then used in conjunction with betting odds to make a bet that should give the highest rate of return.

The second part of the project involves using a machine learning algorithm (such as Support Vector Classification or Known Nearest Neighbors) to make predictions based solely on the betting odds offered.
