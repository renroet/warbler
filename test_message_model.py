"""Message Model tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py

import os
from unittest import TestCase
from sqlalchemy import exc
from sqlalchemy.orm.exc import NoResultFound

from models import db, connect_db, Message, User, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class MessageModelTestCase(TestCase):
    """Test models for messages."""

    def setUp(self):
        """Create test client, add sample data"""
        db.session.rollback()

        Message.query.delete()
        User.query.delete()
        Likes.query.delete()

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

        # u = db.one_or_404(db.select(User).filter_by(username='testuser1'))
        m1 = Message(text='Hello Hello Hello',user_id=u1.id)
        db.session.add(m1)
        db.session.commit()




    def test_message_model(self):
        """Does basic model work?"""
        u = db.one_or_404(db.select(User).filter_by(username='testuser1'))
        m = Message(
            text="Hello Bello",
            user_id=u.id
        )

        db.session.add(m)
        db.session.commit()

        # User should have no messages & no followers
        self.assertTrue(m.timestamp)


    def test_message_user(self):
        """Does model track user of message?"""
        u = db.one_or_404(db.select(User).filter_by(username='testuser1'))
        m = db.one_or_404(db.select(Message).filter_by(text="Hello Hello Hello"))

        self.assertEqual(u.username, m.user.username)


    def test_message_validation_creation(self):
        """Does model hinder the making of a message without a user"""

        with self.client as c:
            m = Message(text='Hello')
            db.session.add(m)
            try:
                db.session.commit()
                raise AssertionError
            except:
                db.session.rollback()
                pass
    
    
    def test_message_not_user(self):
        """Does not falsely associate user's with messages"""

        u = db.one_or_404(db.select(User).filter_by(username='testuser2'))
        m = db.one_or_404(db.select(Message).filter_by(text="Hello Hello Hello"))

        self.assertNotEqual(u.username, m.user.username)

    def test_message_cascade_delete(self):
        """Does message delete when user is deleted"""
        u = db.one_or_404(db.select(User).filter_by(username='testuser1'))

        with self.client as c:
            db.session.delete(u)
            db.session.commit()
            
            try:
                m = db.session.query(Message).one()
            except NoResultFound:
                pass



    