"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

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

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_message_logged_out(self):
        """Will app prohibit user from adding a message when logged out"""

        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = db.session.query(Message).all()
            self.assertEqual(len(msg), 0)

    def test_delete_message(self):
        """Can user delete a message when logged in"""

        with self.client as c:   
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                msg = Message(text="hello", user_id=self.testuser.id)
                db.session.add(msg)
                db.session.commit()

            resp = c.post(f'/messages/{msg.id}/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            message = db.session.execute(db.select(Message)).first()
            self.assertEqual(message, None)

    def test_delete_msg_logged_out(self):
        """Does app prohibit user from deleting a message when logged out"""

        with self.client as c:
            with c.session_transaction() as sess:
                msg = Message(text="hello", user_id=self.testuser.id)
                db.session.add(msg)
                db.session.commit()

            resp = c.post(f'/messages/{msg.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            message = db.session.query(Message).all()
            self.assertEqual(len(message), 1)
            self.assertIn('Access unauthorized', html)

    def test_delete_msg_wrong_user(self):
        """Does app prohibit user from deleting a message when logged out"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                u2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)

                db.session.commit()

                msg = Message(text="hello", user_id=u2.id)
                db.session.add(msg)
                db.session.commit()

            resp = c.post(f'/messages/{msg.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            message = db.session.query(Message).all()
            self.assertEqual(len(message), 1)
            self.assertIn('Access unauthorized', html)

    def test_add_msg_wrong_user(self):
        """Does app prohibit user from adding a message as the incorrect user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                u2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)

                db.session.commit()

            resp = c.post('/messages/new', data={'text': 'Hello',  'user_id': f'{u2.id}'},follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            message = db.session.query(Message).first()
            self.assertEqual(message.user_id, self.testuser.id)
            self.assertIn("@testuser</a>", html)




     
