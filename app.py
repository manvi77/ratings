"""
Products ratings RESTful server implemented using the
Flask-RESTful extension.

Author: Manvisha Kodali

TODO: Link the database (mostly PostgreSQL). Store 
and retrieve the overall votes with the timestamp.
"""

from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth
from datetime import datetime


app = Flask(__name__, static_url_path="")
api = Api(app)
auth = HTTPBasicAuth()

# Create authentication credentials for an admin
@auth.get_password
def get_password(username):
    if username == 'Simon':
        return 'Welcome'
    return None

# Handle the unauthenticated people
@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying 
    # the default auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)

# create a database for two products in a list of dictionaries
# each product is representd in a dictionary
products = [
    {
        'id': 815,
        'name': u'Foobar_Soundsystem',
	'ratings': {'1':0, '2':0, '3':0, '4':0, '5':0},
        'comments': [],
	'modified_on': None 
    },
    {
        'id': 1337,
        'name': u'Soundblaster Pro',
	'ratings': {'1':0, '2':0, '3':0, '4':0, '5':0},
        'comments': [],
	'modified_on': None
    }
]

# define the fields for the ratings, which can be used to
# format the output
ratings_fields = {
	'1': fields.Integer(default=0),
	'2': fields.Integer(default=0),
	'3': fields.Integer(default=0),
	'4': fields.Integer(default=0),
	'5': fields.Integer(default=0)
}

# define the fields of the each product. The ratings is nested
# from ratings fields
product_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'comments': fields.List(fields.String),
    'ratings': fields.Nested(ratings_fields),
    'modified_on':fields.DateTime(dt_format='rfc822')

}


# create the resource for products list
class ProductListAPI(Resource):
    """
    Get the list of products. Both admin and clients can look at the
    list of products. Thus we are not providing any authentication.
    """
    def get(self):
        return {'products': [marshal(product, product_fields) for product in products]}


# create the resource for a product
class ProductAPI(Resource):
    """
    In this class client can give a rating (must) and comment (optional)
    for a specific product based on its id.
    """
    def __init__(self):
	"""
	The client must provide their rating to rate the product based
	on its id. The comment is optional. If no comment is provided 
	then the null string will append to the list of comments. They
	can view a specific product by id.
	"""
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('ratings', type=str, required=True,
			help='You must provide rating in 1 to 5',
			location='json')
        self.reqparse.add_argument('comments', type=str, location='json')
        super(ProductAPI, self).__init__()
    
    def get(self, id):
	"""
	We return the specific product based on its id. If the id is not
	unique that means we may have more than one product for a particular
	id, in that case we are considering only the first product. 
	If no product is avaliable for the asking id, then it returns 404 
	error.
	"""
        product = [product for product in products if product['id'] == id]
        if len(product) == 0:
            abort(404)
        return {'product': marshal(product[0], product_fields)}

    def put(self, id):
	"""
	To update the ratings of the particular product, first we need to
	find the product which clients wants to rate. If there is no 
	product then return 404 error. Once we find the product then
	update all values of the product keys provided by the clients.
	"""
        product = [product for product in products if product['id'] == id]
        if len(product) == 0:
            abort(404)
        product = product[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
		if k == 'ratings':
			product['ratings'][v] += 1
		elif k== 'comments':
			if v is not None:
               		    product[k].append(v)
			else:
			    product[k].append('')
        return {'product': marshal(product, product_fields)}


# create a resource for product list
class AdminAPI(Resource):
    """
    Since this is AdminAPI, must need authentication to access this
    resource.
    Since the Resouce class inherits from Flask's MethodView, it is 
    possible to attach decorators to the methods by defining a 
    decorators class variable. And add auth.login_required to the
    decorator. From this class:
    + Admin can add a new product to the existing list by post method.
    + Admin can get how many feedback answers were given per rating 
     a given timeframe by get method.
    + Admin can delete a product by its id
    """
    decorators = [auth.login_required]
    def __init__(self):
	"""
	To add a product, the id and name are compulsory.
	Comments are optional, ratings are automatically initialized to
	zeros.
	"""
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=int, required=True,
                                   help='No product id provided',
                                   location='json')
        self.reqparse.add_argument('name', type=str, required=True,
                                   help='No product name provided',
                                   location='json')
        self.reqparse.add_argument('comment', type=list, default=[],
                                   location='json')
        self.reqparse.add_argument('modified_on',type=datetime,
				    default=datetime.now(), location='json')
	
        super(AdminAPI, self).__init__()


    def post(self):
	"""
	Add a new product. One thing we can do is the checking of the id
	is it unique or not. Return the product by formatting to the
	product fields.
	Return 201 code: request has been fulfilled and resulted in a 
	new resource being created.
	"""
        args = self.reqparse.parse_args()
        product = {
            'id': args['id'],
            'name': args['name'],
            'comments': args['comment']
        }
	product['ratings'] = {'1':0, '2':0, '3':0, '4':0, '5':0}
        products.append(product)
        return {'product': marshal(product, product_fields)}, 201
    
    def get(self):
	"""
	Get the over all votes for each rating.
	Return the over all votes in ratings fields format.
	"""
	overall_votes ={'1':0, '2':0, '3':0, '4':0, '5':0 }
	for product in products:
		for k in product['ratings']:
			overall_votes[k] += product['ratings'][k]
		
	return {'Overall votes': marshal(overall_votes, ratings_fields)}
    
# Create the resource to delete admin    
class AdminDeleteAPI(Resource):
    """
    Delete a particular product by its id
    """
    decorators = [auth.login_required]
    def delete(self, id):
	"""
	Delete the particular product based on id. If there is no product
	with that particular id then return 404 Not Found error.
	"""
        product = [product for product in products if product['id'] == id]
        if len(product) == 0:
            abort(404)
        products.remove(product[0])
        return {'result': True}


api.add_resource(ProductListAPI, '/ratings/api/v1.0/products', endpoint='products')
api.add_resource(ProductAPI, '/ratings/api/v1.0/products/<int:id>', endpoint='product')
api.add_resource(AdminAPI, '/ratings/api/v1.0/admin', endpoint='admin')
api.add_resource(AdminDeleteAPI, '/ratings/api/v1.0/admin/<int:id>', endpoint='delete')


if __name__ == '__main__':
    """
    If you enable debug support the server will reload itself on code changes, 
    and it will also provide you with a helpful debugger if things go wrong.
    Note: debug mode must never be used on production machines.
    """
    app.run(debug=True)
