document.addEventListener('DOMContentLoaded', function() {
    var scrollBox = document.getElementById('scrollBox');

    // Fetch data from Flask backend to set up buttons at the start
    fetchInitialData();

    function fetchInitialData() {
        fetch('/initial_data', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data === "Wait") {
                    console.log("Server is still processing. Please wait for initial data.");
                } else {
                    console.log('Initial data:', data);
    
                    // Variable to track if it's the first key
                    let isFirstKey = true;
    
                    // Iterate over each key in the data object
                    Object.keys(data).forEach(key => {
                        createButton(key);
                        
                        // If it's the first key, call createGraph with its data
                        if (isFirstKey) {
                            createGraph(data[key]);
                            isFirstKey = false; // Ensure this block runs only once
                        }
    
                        // Optionally, log details of items within each key if needed
                        data[key].forEach(item => {
                            console.log(`Date: ${item.date}, Link: ${item.link}, Price: ${item.price}`);
                        });
                    });
                }
            })
            .catch((error) => {
                console.error('Error fetching initial data:', error);
            });
    }

    // Function to create button
    function createButton(searchText) {
        // Check if a button with the same text already exists
        var existingButton = Array.from(scrollBox.getElementsByTagName('button')).find(button => button.textContent === searchText);

        // Create a new button if no existing button was found
        if (!existingButton) {
            var button = document.createElement('button');
            button.textContent = searchText;

            // Handle button click
            button.addEventListener('click', function() {
                var buttonText = this.textContent;

                // Send the button text to the Flask server
                fetch('/button_click', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ button_text: buttonText }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data === "Wait") {
                        console.log("Server is still processing. Please wait.");
                    } else {
                        console.log('Button click response:', data);
                        createGraph(data);
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
            });

            // Append the button to the scrollBox
            if (scrollBox && typeof scrollBox.appendChild === 'function') {
                scrollBox.appendChild(button);
            } else {
                console.error("Element with id 'scrollBox' not found or does not support appendChild.");
            }
        }
    }

    // Variable to hold the Chart instance
    let myChart = null;

    // Function to create graph
    function createGraph(graphData) {
        // Process the data to extract the prices and formatted dates
        var prices = graphData.map(item => item.price);
        var dates = graphData.map(item => new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));

        // Update the link to the newest product
        var latestIndex = dates.length - 1;
        var latestLink = graphData[latestIndex].link;
        document.getElementById('latestProductLink').href = latestLink;

        // Get the context of the canvas element we want to select
        var ctx = document.getElementById('myChart').getContext('2d');

        // Check if a Chart instance already exists, and destroy it if it does
        if (myChart) {
            myChart.destroy();
        }

        // Create a new Chart instance
        myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Price',
                    data: prices,
                    borderColor: 'rgb(75, 192, 192)',
                    fill: false
                }]
            },
            options: {
                scales: {
                    xAxes: [{
                        type: 'time',
                        time: {
                            unit: 'day'
                        }
                    }]
                }
            }
        });
    }

    // Handle search input change
    document.getElementById('searchInput').addEventListener('change', function() {
        var searchText = this.value;

        // Check if a button with the same text already exists
        var existingButton = Array.from(scrollBox.getElementsByTagName('button')).find(button => button.textContent === searchText);

        // Create a new button if no existing button was found
        if (!existingButton) {
            createButton(searchText);
        }

        // Send the search term to the Flask server
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ search_term: searchText }),
        })
        .then(response => response.json())
        .then(data => {
            if (data === "Wait") {
                console.log("Server is still processing. Please wait.");
            } else {
                console.log('Response:', data);
                createGraph(data);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});
