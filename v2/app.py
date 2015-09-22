"""
Products ratings RESTful server implemented using the
Flask-RESTful extension.

Author: Manvisha Kodali
"""
import os
from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError


app = Flask(__name__, static_url_path="")
app.config['SECRET_KEY'] = '123456789'

#create database
#DATABASE_URL = 'postgresql://scot:tiger@localhost:5432/mydbname'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
api = Api(app)
db = SQLAlchemy(app)

# Create a DBAPI connection
engine = db.create_engine(os.environ['DATABASE_URL'])
#engine = db.create_engine()

# Declare an instance of the base class for mapping tables
Base = declarative_base()

############
## Models ##
###########

# Map a table to a class by inheriting base class
class Products(Base):
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    productratings = db.relationship('ProductsRatings', backref='products',
                                          lazy='dynamic')
    def __init__(self, product_id, name):
        self.product_id = product_id
        self.name = name
    
    def add(self, product):
        db.session.add(product)
	return session_commit()


class Ratings(Base):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, unique=True)
    productratings = db.relationship('ProductsRatings', backref='ratings',
                                           lazy='dynamic')
    def __init__(self, rating):
        self.rating = rating
    
    def add(self, rating):
        db.session.add(rating)
	return session_commit()


class ProductsRatings(Base):
    __tablename__ = 'productratings'

    product_rating_id =  db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    rating = db.Column(db.Integer, db.ForeignKey('ratings.id'))
    comment = db.Column(db.String())
    time_frame = db.Column(db.DateTime)

    def __init__(self, product_id, rating, comment, time_frame):
	self.product_id = product_id
        self.rating = rating
	self.comment = comment
	self.time_frame = time_frame

    def add(self, rating):
        db.session.add(rating)
	return session_commit()


def session_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        reason=str(e)

Base.metadata.create_all(engine)

##################
## Controllers ###
#################

product_fields = { 
    'product_id': fields.Integer,
    'name': fields.String
}

rating_field = { 
    'rating': fields.Integer(default=0),
}

products_ratings_fields = {
    'product_id': fields.Integer,
    'name': fields.String,
    'rating': fields.Integer(default=0),
    'comment': fields.String,
    'time_frame': fields.DateTime
}


class ProductListAPI(Resource):
    
    def get(self, id=None):
	"""
	We return the specific product based on its id. If the id is None
        then return all the products. If the given product id is unavailabe
        then returns the 404 error.
	"""
	if id == None:
	   return {'products': [marshal(product, product_fields) for product in 
	           db.session.query(Products).all()]}
	products = [marshal(product, product_fields) for product in 
	                  db.session.query(Products).all()]
	product = [product for product in products if product['product_id'] == id]
	if len(product) == 0:
	    abort(404)
	return {'product': marshal(product[0], product_fields)}

class ProductRatingAPI(Resource):
    def __init__(self):
        """ 
        The client must provide their rating to rate the product based
        on its id. The comment is optional. If no comment is provided 
	then the null string will be added to the database.
        """
	self.reqparse = reqparse.RequestParser()
	self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('rating', type=str, required=True,
	         help='You must provide rating in 1 to 5', location='json')
	self.reqparse.add_argument('comment', type=str, location='json',
	                             default="")
	super(ProductRatingAPI, self).__init__()

    def put(self, id):
        """
	Product id, rating, comment (optional), and time frame (UTC) are
	added to the ProductsRatings table. First we check the id which
	clients wants to rate, is exist or not. Then, we check the entered
	rating is with in our ratings or not.
	"""
	products = [marshal(product, product_fields) for product in 
	                  db.session.query(Products).all()]
        product = [product for product in products if product['product_id'] == id]
	if len(product) == 0:
	    abort(404)
	
	args = self.reqparse.parse_args()
        # retrive the all allowed ratings from database
	allowed_ratings = [marshal(r, rating_field) for r in 
	                          db.session.query(Ratings).all()]
	rating = [ r['rating'] for r in allowed_ratings 
	                       if r['rating'] == int(args['rating'])]
	if len(rating) == 0:
	    return {'result': 'Failed! Please enter your rating betweeen 1 to 5'}
	   # abort(404)
	rating = rating[0]
        product = [product for product in products if product['product_id'] == id]
	product = product[0]
	product_id = id
	comment = args['comment']
	time_frame = datetime.utcnow()
	feedback = ProductsRatings(product_id=product_id, rating=rating,
	                          comment=comment, time_frame=time_frame)
	feedback_add = feedback.add(feedback)
	if not feedback_add:
	    return make_response(jsonify({'result': 'Your rating successfully added'}), 202)
	else:
	    return make_response(jsonify({'result': 'Failed!'}), 400)


# Create authentication credentials for an admin
auth = HTTPBasicAuth()
@auth.get_password
def get_password(adminname):
    if adminname == 'Simon':
        return 'Welcome'
    return None

# Handle the unauthenticated people
@auth.error_handler
def unauthorized():
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)

class AdminAPI(Resource):
    
    decorators = [auth.login_required]

    def __init__(self):
	self.reqparse = reqparse.RequestParser()
	self.reqparse.add_argument('start', type=str, location='json', 
	                            default='2015-01-01 00:00:00')
	self.reqparse.add_argument('end', type=str, location='json',
	                            default=str(datetime.utcnow()))
	super(AdminAPI, self).__init__()

    def get(self):
        # start = '2015-09-21 15:28:12.622034'
	# end = '2015-09-21 15:59:12.622034'
	args = self.reqparse.parse_args()
	start = args['start']
	end = args['end']
	
        #products_ratings = [marshal(products_ratings, products_ratings_fields) 
	#                    for products_ratings in 
	#	                  db.session.query(ProductRatings).all()]
	query_ratings_count = db.session.query(ProductsRatings.rating, 
	                    func.count(ProductsRatings.rating))
	filter_by_time = query_ratings_count.filter((ProductsRatings.time_frame >= 
	start) & (ProductsRatings.time_frame <= end))
	group_by_rating = filter_by_time.group_by(ProductsRatings.rating).all()
	
	over_all_votes = {}
	for (rating, count) in group_by_rating:
		over_all_votes[str(rating)+" star"] = str(count) + ' votes'
        
	return {'over all votes in a time frame ' + start + ' ' + end: over_all_votes}


class AdminPostAPI(Resource):
    """
    Create a new product
    """
    decorators = [auth.login_required]

    def __init__(self):
	self.reqparse = reqparse.RequestParser()
	self.reqparse.add_argument('id', type=int, required=True,
	                            help='No product id provided',
			            location='json')
	self.reqparse.add_argument('name', type=str, required=True,
	                            help='No product name provided',
			            location='json')
    def post(self):
        args = self.reqparse.parse_args()
        product_id = args['id']
        name = args['name']
        product = Products(product_id=product_id,
                          name=name)
        product_add = product.add(product)
	if not product_add:
	    return {'result': 'New product successfully added'}
	else:
	    return {'result': 'Failed!'}

class AdminDeleteAPI(Resource):
    """
    Delete a product
    """
    decorators = [auth.login_required]

    def delete(self, id):
	p_id = db.session.query(Products).filter(Products.product_id==id)
	print p_id.all()
	if  p_id.all():
	    p_id.delete()
	    db.session.commit()
	    return {'result': 'Product successfully deleted'}
	else:
	    return make_response(jsonify({'result': 'Product id is not exist in database'}), 404)

api.add_resource(ProductListAPI, '/ratings/api/v2.0/products', endpoint='products')
api.add_resource(ProductListAPI, '/ratings/api/v2.0/products/<int:id>', endpoint='product')
api.add_resource(ProductRatingAPI, '/ratings/api/v2.0/products/<int:id>', endpoint='product_rating')
api.add_resource(AdminAPI, '/ratings/api/v2.0/admin', endpoint='admin')
api.add_resource(AdminPostAPI, '/ratings/api/v2.0/admin', endpoint='admin_post')
api.add_resource(AdminDeleteAPI, '/ratings/api/v2.0/admin/<int:id>', endpoint='admin_delete')



class dbInit:
    """
    create initial database
    """
    def __init__(self):
        product1 = Products(product_id=815, name='Foobar-Soundsystem')
        db.session.add(product1)
        product1 = Products(product_id=1337, name='Soundblaster Pro')
        db.session.add(product1)

        rating1 = Ratings(rating=1)
        db.session.add(rating1)
        rating2 = Ratings(rating=2)
        db.session.add(rating2)
        rating3 = Ratings(rating=3)
        db.session.add(rating3)
        rating4 = Ratings(rating=4)
        db.session.add(rating4)
        rating5 = Ratings(rating=5)
        db.session.add(rating5)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print (str(e))


engine.dispose()

if __name__ == '__main__':
    """
    If you enable debug support the server will reload itself on code 
    changes ,and it will also provide you with a helpful debugger if 
    things go wrong.
    Note: debug mode must never be used on production machines.
    """
    # dbInit() # Run this one time to create initial database
    app.run(debug=True)
