Get the list of products
----------------------------
curl -i  http://localhost:5000/ratings/api/v1.0/products

Give a rating for specific product
-----------------------------------
curl -i  -H "Content-Type: application/json" -X PUT -d '{"ratings": "1"}' http://localhost:5000/ratings/api/v1.0/products/1337

Add a new product
---------------------
curl -i -u Simon:Welcome -H "Content-Type: application/json" -X POST -d '{"id": 7, "name": "cup"}' http://localhost:5000/ratings/api/v1.0/admin

Get a specific product by id
-----------------------------
curl -i http://localhost:5000/ratings/api/v1.0/products/1337

Get the over all votes for each rating
-----------------------------------------
curl -u Simon:Welcome http://localhost:5000/ratings/api/v1.0/admin

Delete the particular product by its id
------------------------------------------
curl -i -u Simon:Welcome -X DELETE http://localhost:5000/ratings/api/v1.0/admin/7
