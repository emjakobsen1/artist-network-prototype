
Fetches an artist and their top tracks from the spotify API, and constructs a graph by performing BFS on the featured artists of these.
Nodes: artists. Edge: Collaboration between artists, If they are featured on the same track. Edge color, light grey to black, is spotify's popularity score for the track. 

```sh
   python fetchSpotifyData.py
```


Fetches info from artists and whom they have collaborated with. More details, but no graphs or visualizations. 

```sh
   python fetchSpotifyData2.py
```

Simple javascript/D3.js example. 2 node classes: Artists and releases, edge if an artist appears on a release. Data from discogs API. 

Preview index.html
