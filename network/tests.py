from django.http import response
from django.test import TestCase, Client, client
from .models import Posts, Follow, User
# Create your tests here.


class PostsTestCase(TestCase):

    def setUp(self):

        # Create Users
        u1 = User.objects.create(username = "aaa", email="aaa@test.com", password="aaa")
        u1.set_password("aaa")
        u1.save()
        u2 = User.objects.create(username = "bbb", email="bbb@test.com", password="bbb")
        u2.set_password("bbb")
        u2.save()

        # Create Posts
        p1 = Posts.objects.create(content="abc", likes=0, timestamp="Oct. 28, 2021, 4 p.m.", poster=u1)
        p1.likedBy.add(None)
        p2 = Posts.objects.create(content="xyz", likes=-1, timestamp="Oct. 28, 2021, 4 p.m.", poster=u1)
        p2.likedBy.add(u1)
        p3 = Posts.objects.create(content="", likes=0, timestamp="Oct. 27, 2021, 4 p.m.", poster=u2)
        p3.likedBy.add(u2)

    def test_valid_post(self):
        u1 = User.objects.get(username="aaa")
        p = Posts.objects.get(likedBy=None, poster=u1, content="abc")
        self.assertTrue(p.is_valid_post())


    def test_invalid_postLikes(self):
        u1 = User.objects.get(username="aaa")
        p = Posts.objects.get(likedBy=u1, poster=u1)
        self.assertFalse(p.is_valid_post())

    def test_invalid_postContent(self):
        u2 = User.objects.get(username="bbb")
        p = Posts.objects.get(likedBy=u2, poster=u2)
        self.assertFalse(p.is_valid_post())

    def test_valid_index(self):
        c = Client()
        response = c.get("")
        # Redirects to login page
        self.assertEqual(response.status_code, 302)

    def test_valid_followingPage(self):
        c = Client()
        response = c.get("/following")
        self.assertEqual(response.status_code, 302)

    def test_valid_userPage(self):
        c = Client()
        response = c.get("/aaa/")
        self.assertEqual(response.status_code, 302)

    def test_valid_userFollowersPage(self):
        c = Client()
        response = c.get("/aaa/followers")
        self.assertEqual(response.status_code, 302)

    def test_valid_login(self):
        c = Client()
        c.login(username = 'aaa', password = 'aaa')
        response = c.get("")
        self.assertEqual(response.status_code, 200)

    def test_valid_profile(self):
        c = Client()
        c.login(username = "aaa", password = "aaa")
        response = c.get("/aaa/")
        self.assertEqual(response.status_code, 200)

    def test_valid_following(self):
        c = Client()
        c.login(username = "aaa", password = "aaa")
        response = c.get("/following")
        self.assertEqual(response.status_code, 200)

    def test_valid_followers(self):
        c = Client()
        c.login(username = "aaa", password = "aaa")
        response = c.get("/aaa/followers")
        self.assertEqual(response.status_code, 200)