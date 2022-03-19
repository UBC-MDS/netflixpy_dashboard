Milestone 4 Reflection
================

We have utilized our peer feedback to improve our DashPy implemention of the app which visualizes some trends of movies and TV shows in Netflix to contain the following plot and widget:

1. Word Cloud plot: The wordcloud plot represents the most used word in movies and TV shows titles.

2. Rating Widget: A drop down to filter selected movies and TV shows based on content rating. It is interactive across all the plots.

3. We modified the duration plot by making modifying the histogram into a boxplot. 

4. We extended the world map to contain the genre and rating widgets.

5. We Modified the layout and design of the app to resemble the red, black and white theme of the Netflix.

6. Modified the year slider for a better fit in the layout.

7. Added an information button providing the user with some descriptions of the app.

### Layout 

We implemented a unified color theme and layout that is visually appealing and constinent with the Netflix theme, in order to ensures better user engagement and interaction with the dashboard.

### Plot Interactivity

All of the plots contain interactivity. The world map has a tooltip that
shows the country name, content release year and count of occurrences per
country. The director bar plot also contain a tool tip and opacity
interactivity. Furthermore, the duration plot shows the maximum, minimum duration
of movies or TV shows.

### Widgets

First, we have implemented a drop-down menu containing different genres and rating
of the content for the director and the duration plots. Second, we have
implemented a year slidebar to show the differences in production of
content, content directors and duration of content over the years.
Moreover, since the content has different duration type depending on
whether it is a movie or a TV show, we have implemented separated tabs
showing the differences in duration type.

### Differences between DashR and DashPy

There are several differences between the DashR and DashPy implementation that we are hoping to address in the future additions. First, there is no word cloud of the content titles in the DashR, and second the theme is slightly different than DashPy.

### Limitations and Future Additions

Although the current implemented dashboard is easy to use and performs well in terms of the plot interactivity and widgets described above, there are some limitations that we would like to address by future additions as described below:

- Currently, the wordcloud causes the app to crash on Mac M1. We will be looking for a solution to address this issue.

- The word cloud slows down the performance of the app slightly. We will be looking for a solution to address this issue.

- When selecting or unselecting the dropdown widgets too fast, the wordcloud throws an error. We will be looking for a solution to address this issue. 

- We will address the differences between DashR and DashPy.

- Adding the selection between movie and TV shows for the world map and director plots.

- Adding a couple of the most popular movie/ TV show images.

- Selective interaction between plots without the use of a widget.

- Improving the layout and design further.
