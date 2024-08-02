function analyzeSentiment() {
    const reviews = document.getElementById('reviewInput').value.split('\n').filter(line => line.trim() !== '');
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reviews: reviews })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('overall').innerHTML=data.sentiment;
        document.getElementById('positiveAspects').innerText = data.positive.join(', ');
        document.getElementById('negativeAspects').innerText = data.negative.join(', ');
    });
}
