// Set up width and height (bigger canvas)
const width = 1000, height = 700;

// Create an SVG element inside the body
const svg = d3.select("body")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

// Load the JSON data
d3.json("data.json").then(data => {
    const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).id(d => d.id).distance(150)) // Increase distance to spread nodes apart
        .force("charge", d3.forceManyBody().strength(-150)) // Stronger repulsion to spread nodes apart
        .force("center", d3.forceCenter(width / 2, height / 2)) // Center the graph
        .force("x", d3.forceX(width / 2).strength(0.05)) // Push nodes towards the center horizontally
        .force("y", d3.forceY(height / 2).strength(0.05)) // Push nodes towards the center vertically
        .force("collide", d3.forceCollide().radius(20)) // Add collision force to prevent overlap between nodes

    // Draw links (edges)
    const link = svg.selectAll(".link")
        .data(data.links)
        .enter()
        .append("line")
        .attr("class", "link")
        .attr("stroke", "gray")
        .attr("stroke-width", 2);

    // Draw nodes (circles) with different colors for artists and releases
    const node = svg.selectAll(".node")
        .data(data.nodes)
        .enter()
        .append("circle")
        .attr("class", "node")
        .attr("r", 10) // Node size
        .attr("fill", d => d.type === "artist" ? "red" : "blue") // Artist = red, Release = blue
        .call(d3.drag()
            .on("start", dragStart)
            .on("drag", dragging)
            .on("end", dragEnd));

    // Add labels (text)
    const labels = svg.selectAll(".label")
        .data(data.nodes)
        .enter()
        .append("text")
        .attr("class", "label")
        .attr("text-anchor", "middle")
        .attr("dy", -15) // Position above nodes
        .attr("font-size", "12px")
        .attr("fill", "black")
        .text(d => d.id);

    // Simulation update
    simulation.on("tick", () => {
        link.attr("x1", d => Math.max(10, Math.min(width - 10, d.source.x)))
            .attr("y1", d => Math.max(10, Math.min(height - 10, d.source.y)))
            .attr("x2", d => Math.max(10, Math.min(width - 10, d.target.x)))
            .attr("y2", d => Math.max(10, Math.min(height - 10, d.target.y)));

        node.attr("cx", d => Math.max(10, Math.min(width - 10, d.x)))
            .attr("cy", d => Math.max(10, Math.min(height - 10, d.y)));

        labels.attr("x", d => Math.max(10, Math.min(width - 10, d.x)))
              .attr("y", d => Math.max(10, Math.min(height - 10, d.y)));
    });

    // Drag functions
    function dragStart(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragging(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragEnd(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
});
