import unittest
from app import create_app
from app.models import db, Product
from marshmallow import ValidationError


class TestProduct(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.payLoad = {
            "name": "Brakes",
            "brand": "Brand A",
            "price": 100.00,
            "category_id":1,
            "description":"Description",
            
        }
        with self.app.app_context():
            db.drop_all() # Drop all tables before creating new ones
            db.create_all() # Create all tables
            db.session.add(Product(**self.payLoad))
            db.session.commit()
        self.client = self.app.test_client()
        
    def test_create_product(self): # Create product with valid payload
        
        response = self.client.post('/products/', json=self.payLoad)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], "Successfully created product")
    
    def test_fields_required(self): 
        payload = self.payLoad.copy()
        payload.pop('name')
        
        response = self.client.post('/products/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['name'][0], "Missing data for required field.")
    
    def test_get_all_products(self):
        response = self.client.get('/products/', query_string={'page': 1, 'per_page': 10})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json['items'], list)
    
    def test_get_products_by_id(self): 
        response = self.client.get('products/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], self.payLoad['name'])
    
    def test_get_products_invalid_id(self): 
        response = self.client.get('products/9999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Invalid product")

    def test_update_products(self): 
        
        payLoad = self.payLoad.copy()
        payLoad["name"] = "Updated Name"
        response = self.client.put('products/1', json=payLoad)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Successfully updated product")
        self.assertEqual(response.json['product']['name'], payLoad["name"])
        
    def test_update_invalid_products(self): 
        
        payLoad = self.payLoad.copy()
        payLoad["name"] = "Updated Name"
        response = self.client.put('products/999', json=payLoad)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Product not found")
        
    def test_delete__products(self): 
        
        response = self.client.delete('products/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Successfully deleted product")
    
    def test_delete_invalid_products(self): 
        
        response = self.client.delete('products/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Product not found")
    
    def test_search_product_by_name(self): 
        
        response = self.client.get('/products/search', query_string={"name": self.payLoad['name']})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
    
    def test_search_product_no_params(self): 
    
        response = self.client.get('/products/search')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Please provide a name or brand to search")
   
    
    