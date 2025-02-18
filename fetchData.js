const fs = require("fs");
const fetch = require("node-fetch");

const DISCOGS_TOKEN = "YOUR_DISCOGS_API_TOKEN"; // Optional API Token
const ARTIST_IDS = [...Array(10).keys()].map(i => i + 1); // [1,2,3,4,5,6,7,8,9,10]

// Fetch artist releases from Discogs API
async function fetchArtistData(artistId) {
    const url = `https://api.discogs.com/artists/${artistId}/releases?per_page=5&page=1${DISCOGS_TOKEN ? `&token=${DISCOGS_TOKEN}` : ''}`;

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP Error! Status: ${response.status}`);
        const data = await response.json();
        return data.releases || [];
    } catch (error) {
        console.error(`Error fetching artist ${artistId}:`, error);
        return [];
    }
}

// Create graph structure
async function createGraphData() {
    let nodes = [];
    let links = [];

    for (const artistId of ARTIST_IDS) {
        const artistUrl = `https://api.discogs.com/artists/${artistId}`;
        try {
            const artistResponse = await fetch(artistUrl);
            if (!artistResponse.ok) throw new Error(`Error fetching artist ${artistId}`);
            const artistData = await artistResponse.json();
            const artistName = artistData.name || `Artist ${artistId}`;

            // Add artist node if not already in the list
            if (!nodes.some(n => n.id === artistName)) {
                nodes.push({ id: artistName, type: "artist" });
            }

            // Fetch releases
            const releases = await fetchArtistData(artistId);
            releases.forEach(release => {
                if (!nodes.some(n => n.id === release.title)) {
                    nodes.push({ id: release.title, type: "release" });
                }
                links.push({ source: artistName, target: release.title });
            });

        } catch (error) {
            console.error(`Skipping artist ${artistId} due to error.`);
        }
    }

    return { nodes, links };
}

// Main function to fetch and save data
async function generateDataJson() {
    const graphData = await createGraphData();
    fs.writeFileSync("data.json", JSON.stringify(graphData, null, 2));
    console.log("✅ Data saved to data.json!");
}

// Run the script
generateDataJson();
