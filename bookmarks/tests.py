from datetime import datetime
import bookmarks_db
import unittest

class TestBookmarksDb(unittest.TestCase):
	def _create_user(self, name):
		return bookmarks_db.User(name, now=self.now)

	def setUp(self):
		unittest.TestCase.setUp(self)
		self.now = datetime(2012, 10, 15, 12, 30, 45)
		self.session = bookmarks_db.session
		bookmarks_db.create_all()
	
	def tearDown(self):
		unittest.TestCase.tearDown(self)
		bookmarks_db.drop_all()
	
	def test_create_user(self):
		user = self._create_user('user1')
		self.session.add(user)
		self.session.commit()

	def test_create_delete_bookmarks(self):
		pass


if __name__ == '__main__':
	unittest.main()

