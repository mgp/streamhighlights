from datetime import datetime, timedelta
import db
import unittest


"""Base class for test cases that use the database.
"""
class DbTestCase(unittest.TestCase):
	"""Utility method for creating a user."""
	def _create_user(self, name):
		user = db.User(name, self.now)
		self.session.add(user)
		self.session.commit()
		return user.id

	def setUp(self):
		unittest.TestCase.setUp(self)
		self.now = datetime(2012, 10, 15, 12, 30, 45)
		self.session = db.session
		db.create_all()
	
	def tearDown(self):
		db.drop_all()
		unittest.TestCase.tearDown(self)

