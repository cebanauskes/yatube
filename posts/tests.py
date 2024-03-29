from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth import get_user_model
from .models import Post, Group, Follow, Comment
import time
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.cache.backends import locmem
from django.urls import reverse

User = get_user_model()

TEST_CACHE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

@override_settings(CACHES=TEST_CACHE)
class TestProfile(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', email='bk@gmail.com', password=12345)
        self.client.login(username='test', password=12345)
        self.user2 = User.objects.create_user(username='second', email='second@gmail.com', password=8886777)
        self.user3 = User.objects.create_user(username='third', email='third@gmail.com', password=33344456)
        
    def test_create_profile(self):
        response = self.client.get(f"/test/")
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        post_new = {
            'text': 'Полиция всегда защищала тебя, с любой неприятностью ты мог обратиться в суд. Тебе не нужен был такой друг как я.',
            }
        response = self.client.post('/new/', post_new)
        self.assertEqual(response.status_code, 302)

    def test_pub_post(self):
        post_new = Post.objects.create(text='Полиция всегда защищала тебя, с любой неприятностью ты мог обратиться в суд. Тебе не нужен был такой друг как я.', author=self.user)
        post_id = post_new.pk
        response = self.client.get('/')
        self.assertContains(response, post_new, status_code=200, count=1)
        response = self.client.get('/test/')
        self.assertContains(response, post_new, status_code=200, count=1)
        response = self.client.get(f"/test/{post_id}/")
        self.assertContains(response, post_new, status_code=200, count=1)

    def test_post_edit(self):
        post_new = Post.objects.create(text='Полиция всегда защищала тебя, с любой неприятностью ты мог обратиться в суд. Тебе не нужен был такой друг как я.', author =self.user)
        post_id = post_new.pk
        post_author = post_new.author
        post_new.text = 'Ты даже не называешь меня Крестным отцом'
        post_new.save()
        self.assertEqual(post_new.text, 'Ты даже не называешь меня Крестным отцом')
        response = self.client.get('/')
        self.assertContains(response, post_new, status_code=200, count=1)
        response = self.client.get(f'/{post_author}/')
        self.assertContains(response, post_new, status_code=200, count=1)
        response = self.client.get(f"/{post_author}/{post_id}/")
        self.assertContains(response, post_new, status_code=200, count=1)

    def test_404_code(self):
        response = self.client.get('/4865555/')
        self.assertEqual(response.status_code, 404)
    
        
    def test_img_tag(self):

        group = Group.objects.create(title='title', slug='slug', description='description')
        with open('media/posts/original.jpg', 'rb') as fp:
            self.client.post("/new/", {'text': 'fred', 'group': group.pk, 'image': fp})
            urls = {'', '/test/', '/group/slug/'}
            for url in urls:
                response = self.client.get(url)
                self.assertContains(response, '<img ', status_code=200)

    def test_type_of_file(self):
        group = Group.objects.create(title='title', slug='slug', description='description')
        with open('media/VNZh.doc', 'rb') as fp:
            self.client.post("/new/", {'text': 'fred', 'group': group.pk, 'image': fp})
            urls = {'', '/test/', '/group/slug/'}
            for url in urls:
                response = self.client.get(url)
                self.assertNotContains(response, '<img ', status_code=200)

    def test_subscribe_and_unsubscribe(self):
        Post.objects.create(text='Terna', author=self.user2)
        self.client.get(f'/{self.user2.username}/follow')
        follow = Follow.objects.filter(user=self.user, author=self.user2).count()
        self.assertNotEqual(follow, 0)
        self.client.get(f'/{self.user2.username}/unfollow')
        follow = Follow.objects.filter(user=self.user, author=self.user2).count()
        self.assertEqual(follow, 0)

    def test_news_feed(self):
        Post.objects.create(text='Rusu', author=self.user2)
        Post.objects.create(text='Stefan', author=self.user3)
        self.client.get(f'/{self.user2.username}/follow')
        response = self.client.get('/follow/')
        self.assertContains(response, 'Rusu')
        self.assertNotContains(response, 'Stefan')

@override_settings(CACHES=TEST_CACHE)
class TestUnauthorized(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', email='bk@gmail.com', password=12345)

    def test_new_post(self):
        response = self.client.get('/new/', follow=True )
        self.assertRedirects(response, '/auth/login/?next=/new/', status_code=302, target_status_code=200)

    def test_comment(self):
        post = Post.objects.create(text='abcdefg', author=self.user)
        response = self.client.get(f"/{self.user.username}/{post.pk}/comment")
        self.assertRedirects(response, f'/auth/login/?next=/{self.user.username}/{post.pk}/comment', status_code=302, target_status_code=200)
        self.client.login(username='test', password=12345)
        self.client.post(f"/{self.user.username}/{post.pk}/comment", {'text': 'pula'})
        comment = Comment.objects.filter(text='pula').count()
        self.assertNotEqual(comment, 0)


class TestWithCache(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', email='bk@gmail.com', password=12345)
        self.client.login(username='test', password=12345)
    def test_cache_index(self):
        self.client.post("/new/", {'text': 'Popescu',})
        response = self.client.get('/')
        self.assertContains(response, 'Popescu', html=False)
        self.client.post('/new/', {'text': 'Stefan Cel Mare'})
        response = self.client.get('/')
        self.assertNotContains(response, 'Stefan Cel Mare', html=False)
        time.sleep(21)
        response = self.client.get('/')
        self.assertContains(response, 'Stefan Cel Mare', html=False)

