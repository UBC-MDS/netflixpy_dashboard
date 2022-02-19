Our role: Data Science consultancy firm 

Target audience: Over-the-top (OTT) media companies

## Motivation and Purpose 

With the advent of OTT platforms, there has been a gradual shift of audience from movie theaters to online viewing. Netflix is a popular online streaming service that wants to ensure that it provides the right selection of films and TV shows to its users. If we could understand which type of movies and series are being produced currently and how it has changed over the years, it would allow streaming services to produce a suitable content catalog, in line with viewers’ preferences. These factors include but are not limited to the duration of the content, the show directors, country of origin, and the release year of the film/series. 

To address this issue, we propose to build a data visualization dashboard that allows our target audience to visually and interactively explore a database of movies and TV shows to assess the popular content they need to provide to their viewers. Our dashboard will display the distribution and summarize the content duration, the directors, the country of origin, and the release year of the show which would aid the stakeholders in retargeting their production budgets on the most popular content out there.

## Data

We will be visualizing a [dataset](https://www.kaggle.com/shivamb/netflix-shows) of 8807 movie or TV shows available on Netflix from 2008 to 2021. Each Movie/ TV show has 10 associated variables that describe the following:

- `show_id`: Unique Id
- `type`: Movie or a Tv show
- `title`: Title of the Movie/ Tv show
- `director`: Director name(s)
- `cast`: Actors names who play a role
- `country`: Country where the production took place
- `date_added`: Date the Movie/ Tv show was added on Netflix
- `release_year`: Release year
- `rating`: TV rating
- `duration`: Total duration (in minutes or number of seasons)

## Research Questions and Usage Scenarios

Tanimose is a new intern at netflix and works in the business strategy division. He is appointed by the team lead to come up with a proposal
on how to drive the customer's consumption of netflix movies and TV shows based on ratings. The available data lead him to the following ask questions: 

- Over the years, what new ratings ( TV and movie ratings) were introduced to netflix and how have they increased or decreased?
- How has the average duration of the movies or series in each rating increased over the years?
- Are there trigger words in the titles of the movies or/and series that have been persistent in ratings?

Tanimose believes these questions would inform the executive boards on what movies or TV shows to include or remove based on ratings. 
