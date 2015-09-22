Get the list of products
----------------------------
curl -i  http://localhost:5000/ratings/api/v2.0/products

Get a specific product by id
-----------------------------
curl -i http://localhost:5000/ratings/api/v2.0/products/1337

Give a rating for specific product
-----------------------------------
curl -i  -H "Content-Type: application/json" -X PUT -d '{"rating": 1}' http://localhost:5000/ratings/api/v2.0/products/1337

Add a new product
---------------------
curl -i -u Simon:Welcome -H "Content-Type: application/json" -X POST -d '{"id": 7, "name": "cup"}' http://localhost:5000/ratings/api/v2.0/admin

Get the over all votes for each rating in a given time frame
-------------------------------------------------------------
curl -u Simon:Welcome -H "Content-Type: application/json" -X GET -d '{"start": "2015-01-01 00:00:00", "end": "2015-09-21 19:36:26.712866"}' http://localhost:5000/ratings/api/v2.0/admin

Delete the particular product by its id
------------------------------------------
curl -i -u Simon:Welcome -X DELETE http://localhost:5000/ratings/api/v2.0/admin/7
