Milestone 4 Reflection
================

We extended the dashboard that visualizes some trends of movies and TV
shows in Netflix to contain the following plot and widget:

1. Word Cloud plot : The wordcloud plot represents the most used word in movies and TV shows titles.
2. Rating Widget: A drop dwon to filter selected movie anf TV shows. It is interactive
across all the plot

We modified the duration plot by making it a boxplot. This represents the information better
than the histogram plot.

### Plot Interactivity

All of the plots contain interactivity. The world map has a tooltip that
shows the country name, content release year and count of occurences per
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

### Limitations and Future Additions

In this milestone, we have spent a lot of time on exploring and
wrangling the data, and therefore there a lot of future additions that
we would like to add to our dashboard.

Although the current implemented dashboard performs well in terms of the
plot interactivity and widgets described above, there are some
limitations that we would like to address by future additions as
described below:

-   Adding the selection between movie and TV shows for the world map
    and director plots.

-   Adding a couple of the most popular movie/ TV show images.

-  Selective interaction between plots without the use of a widget.
