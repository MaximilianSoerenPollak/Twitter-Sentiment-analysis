<img src="https://bit.ly/2VnXWr2" alt="Ironhack Logo" width="100"/>

# Twitter Sentiment analysis with AWS
*Maximilian Sören Pollak*

*DA FT, RT MAY2021*

## Content
- [Project Description](#project-description)
- [Dataset](#dataset)
- [Workflow](#workflow)
- [Organization](#organization)
- [Links](#links)

## Important, if you use this.

If you want to use this code, make sure you make a python file in the same directory and call it "secrets_file".
Save all your api keys in there. You can also make the file be called something else but then make sure to change the import.
Also be aware of a 5 Mil. character Limit on AWS per month.

## Project Description
This project is searching the twitter API for a hashtag (that needs to be a stock ticker) in a certain timeframe (max 7days in the past).
It will then analyze the sentiment of all of the tweets and give an overall sentiment value.
It also will give additional information about the Stock you have choosen, as well as a graph of the open/closing value it was at in the searched timeframe.


## Dataset
The Data is obtained through the API of Twitter via the wrapper tweepy, as well as through Amazon's API through the wrapper of Boto3.
All Data is obtained once then stored internally in a dataframe. It is not stored for permanent storage somewhere else.


## Workflow
- Decide on a Project
- Research abot ways to achieve that goal
- Research about how to obtain the data
- Mentor meeting
- Plan Code structure
- Data Wrangling
- Perform Analysis
- Build the website
- Test everything
- Write medium article
- Prepare presentation

## Organization
I used my blackboard that I have in my study room, to draw out the overall structure of the project.
Then used VS-Code to make a mock-code version of my script.
I used a Notepad to keep track of all functions and how they internally work togheter and the order in which they need to be called.
You can read more about how it all works in my medium article (link below)

## Links
[Repository](https://github.com/MaximilianSoeren/Project-Week-2-Barcelona)  
[Medium](https://medium.com/@pollakmaximilian/a-simple-sentiment-analysis-of-tweets-containing-with-the-help-of-aws-tweepy-7bc2e17a0c6f?source=friends_link&sk=null)


