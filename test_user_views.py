"""User view tests."""

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
from app import app, CURR_USER_KEY
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_user_followers(self):
        """Can user see any follower/following relationship when logged in"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                    
                u3 = User.signup(username="testuser3",
                                email="test3@test.com",
                                password="testuser",
                                image_url=None)
                db.session.commit()
                self.testuser2.followers.append(u3)
                db.session.add(self.testuser2)
                db.session.commit()
            resp = c.get(f'/users/{self.testuser2.id}/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('alt="Image for testuser3"', html)

    
    
    def test_user_following(self):
        """Can user see any follower/following relationship when logged in"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                    
                u3 = User.signup(username="testuser3",
                                email="test3@test.com",
                                password="testuser",
                                image_url=None)

                db.session.commit()
                self.testuser2.following.append(u3)
                db.session.add(self.testuser2)
                db.session.commit()

            resp = c.get(f'/users/{self.testuser2.id}/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('alt="Image for testuser3"', html)


    def test_logged_out_followers(self):
        """Does app prohibit user from seeing follower/following relationships when logged out"""
        with self.client as c:
            with c.session_transaction() as sess:
                u3 = User.signup(username="testuser3",
                                email="test3@test.com",
                                password="testuser",
                                image_url=None)
                db.session.commit()
                self.testuser2.followers.append(u3)
                db.session.add(self.testuser2)
                db.session.commit()
            resp = c.get(f'/users/{self.testuser2.id}/followers', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)
            

    def test_logged_out_following(self):
        """Does app prohibit user from seeing follower/following relationships when logged out"""
        with self.client as c:
            with c.session_transaction() as sess:
                u3 = User.signup(username="testuser3",
                                email="test3@test.com",
                                password="testuser",
                                image_url=None)
                db.session.commit()
                self.testuser2.following.append(u3)
                db.session.add(self.testuser2)
                db.session.commit()
            resp = c.get(f'/users/{self.testuser2.id}/following', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)
            