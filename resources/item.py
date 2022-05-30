from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from models.item import ItemModel


class Item(Resource):

    # 1. Using parser to only allow extract information we want from the
    # request (POST/ PUT). Also, it will specify the parameters that
    # are required to be passed in
    # 2. placed the "parser" as an variable of "Item" class. So it can
    # be reused by different endpoints
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help="This field cannot be left blank")
    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help="Every item needs a store id")

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404

    def post(self, name):

        # if the item exists, we don't want to add this item
        if ItemModel.find_by_name(name):
            return {'message': f"An item with name {name} already exists"}, 400

        # get data from parser
        data = Item.parser.parse_args()

        # Otherwise, add the new item
        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            # 500 = internal server error
            return {"message", "An error occured inserting the item"}, 500

        return item.json(), 201

    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()

        return {'message': 'Item deleted'}

    def put(self, name):

        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data['price']
            item.store_id = data['store_id']

        item.save_to_db()
        return item.json()


class ItemList(Resource):
    def get(self):
        # return {'item': list(map(lambda x: x.json(), ItemModel.query.all()))}
        return {'item': [x.json() for x in ItemModel.query.all()]}
