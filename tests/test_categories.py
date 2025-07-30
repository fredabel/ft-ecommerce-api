import unittest
from app import create_app
from app.models import db, Category
from marshmallow import ValidationError


class TestCategory(unittest.TestCase):
    def setUp(self):
        pass
