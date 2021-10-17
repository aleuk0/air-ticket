# AIR-TICKET
Сarriage of skis

All reservation progress saved in info.logs

## How to start
1. pip install -r requirements.txt
2. run app.py to start API

## How to make request
We should use this keywords to make a reserve:

number: str - reserve ID, 6 numbers or latin letters, format ABC123

passengerId: str - surname, only latin letters, format Ivanov

## Example
curl -H "Content-Type: application/json" -X POST http://127.0.0.1:8080/applications -d '{"number": "AAA123", "passengerId": "Ivanov"}'
