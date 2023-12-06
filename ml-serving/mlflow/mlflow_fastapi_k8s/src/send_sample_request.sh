curl -X POST "http://localhost:8000/predict/" \
    -H "accept: application/json" -H "Content-Type: application/json" \
    -d '{"feature1": 5.1, "feature2": 3.5, "feature3": 1.4, "feature4": 0.2}'
