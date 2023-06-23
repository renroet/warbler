"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserModelTestCase(TestCase):
    """Test models for user."""

    def setUp(self):
        """Create test client, add sample data."""
        # db.session.rollback()

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        db.session.add(u1)

        u2 =  User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        db.session.add(u2)
        db.session.commit()


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)


    def test_repr(self):
        """Does repr work"""
        user = db.one_or_404(db.select(User).filter_by(username='testuser2'))
        res = db.session.execute(db.select(User).filter_by(username ='testuser2')).one()
        
        result = f'<User #{user.id}: testuser2, test2@test.com>' 
        sol = repr(user)

        self.assertIn(result, sol)  

    def test_is_following(self):
        """Does following users work"""
        u1 = db.one_or_404(db.select(User).filter_by(username='testuser1'))
        u2 = db.one_or_404(db.select(User).filter_by(username='testuser2'))
        u1.following.append(u2)
        
        self.assertIn(u2, u1.following)
        self.assertEqual(len(u1.following), 1)

    def test_is_not_following(self):
        """Does model correctly detect when users are not following eachother"""
        u1 = db.one_or_404(db.select(User).filter_by(username='testuser1'))
        u2 = db.one_or_404(db.select(User).filter_by(username='testuser2'))
        
        res = u1.following

        self.assertNotIn(u2, u1.following)
        self.assertEqual(len(u1.following), 0)

    
    def test_is_followed_by(self):
        """Does following users work"""
        u1 = db.one_or_404(db.select(User).filter_by(username='testuser1'))
        u2 = db.one_or_404(db.select(User).filter_by(username='testuser2'))
        u2.following.append(u1)
        
        self.assertIn(u2, u1.followers)
        self.assertEqual(len(u1.followers), 1)

    def test_is_not_followed_by(self):
        """Does model correctly detect when a user is not being followed"""
        u1 = db.one_or_404(db.select(User).filter_by(username='testuser1'))
        u2 = db.one_or_404(db.select(User).filter_by(username='testuser2'))
        
        res = u1.followers

        self.assertNotIn(u2, u1.followers)
        self.assertEqual(len(u1.followers), 0)

    def test_user_signup(self):
        """Does method create new User upon signup"""
        u = User.signup('testuser3', "test@test.com", "HASHED_PASSWORD", 'image.url')
        
        self.assertTrue(u.username)

    def test_user_signup_validation(self):
        """Does signup fail with invalid input (repeated username in this instance)"""
        with self.client as c:
            u = User.signup('testuser2', "test@test.com", "HASHED_PASSWORD", 'image.url')
            db.session.add(u)
            try:
                db.session.commit()
                raise AssertionError
            except:
                db.session.rollback()
                pass

    def test_user_authenticate(self):
        """Is established user able to be authenticated"""
        with self.client as c:
            u = User.signup('testuser3', "test@test.com", "HASHED_PASSWORD", 'image.url')
            # db.session.commit()
            username = u.username
            self.assertTrue(User.authenticate(username, "HASHED_PASSWORD"))

    
    def test_username_authentication_failure(self):
        with self.client as c:
            u = User.signup('testuser3', "test@test.com", "HASHED_PASSWORD", 'image.url')
            # db.session.commit()
            username = 'bestuser'
            self.assertFalse(User.authenticate(username, "HASHED_PASSWORD"))
    
    def test_password_authentication_failure(self):
        with self.client as c:
            u = User.signup('testuser3', "test@test.com", "HASHED_PASSWORD", 'image.url')
            # db.session.commit()
            username = u.username
            self.assertFalse(User.authenticate(username, "HASHED_PAS3WORD"))

    