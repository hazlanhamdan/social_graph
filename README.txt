social_graph - First project of The Data Incubator

The problem was to retrieve photo captions from http://www.newyorksocialdiary.com/ and to analyze the social graph implied by which people appear together in photos (see problem statement below).  

The script `graph_scrape` compiles a list of unicode strings containing all the photo captions from the website (some 125000 captions) and save the result to a pickle file.  

The script `graph_analyze` uses a number of heuristics to extract names from the captions.  It then uses python's `network-x` module to construct and analyze the graph.  

PROBLEM STATEMENT
-----------------

[New York Social Diary](http://www.newyorksocialdiary.com/) provides a fascinating lens onto New York's socially well-to-do.  The data forms a natural social graph for New York's social elite.  Take a look at this page of a recent run-of-the-mill holiday party:

`http://www.newyorksocialdiary.com/party-pictures/2014/holiday-dinners-and-doers`

Besides the brand-name celebrities, you will notice the photos have carefully annotated captions labeling those that appear in the photos.  We can think of this as implicitly implying a social graph: there is a connection between two individuals if they appear in a picture together.

For the analysis, we think of the problem in terms of a [network](http://en.wikipedia.org/wiki/Computer_network) or a [graph](http://en.wikipedia.org/wiki/Graph_%28mathematics%29).  Any time a pair of people appear in a photo together, that is considered a link.  What we have described is more appropriately called an (undirected) [multigraph](http://en.wikipedia.org/wiki/Multigraph) with no self-loops but this has an obvious analog in terms of an undirected [weighted graph](http://en.wikipedia.org/wiki/Graph_%28mathematics%29#Weighted_graph).  In this problem, we will analyze the social graph of the new york social elite.

QUESTION 1

  The simplest question you might want to ask is 'who is the most popular'?  The easiest way to answer this question is to look at how many connections everyone has.  Return the top 100 people and their degree.  Remember that if an edge of the graph has weight 2, it counts for 2 in the degree.
  
QUESTION 2

  A similar way to determine popularity is to look at their [pagerank](http://en.wikipedia.org/wiki/PageRank).  Pagerank is used for web ranking and was originally [patented](http://patft.uspto.gov/netacgi/nph-Parser?patentnumber=6285999) by Google and is essentially the [stationary distribution](http://en.wikipedia.org/wiki/Markov_chain#Stationary_distribution_relation_to_eigenvectors_and_simplices) of a [markov chain](http://en.wikipedia.org/wiki/Markov_chain) implied by the social graph.

  Use 0.85 as the damping parameter so that there is a 15% chance of jumping to another vertex.
  
QUESTION 3

  Another interesting question is who tend to co-occur with each other.  Give us the 100 edges with the highest weights

  Google these people and see what their connection is.  Can we use this to detect instances of infidelity?