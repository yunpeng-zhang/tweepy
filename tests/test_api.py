import os
import random
import shutil
import time
import unittest
from ast import literal_eval

from .config import tape, TweepyTestCase, use_replay, username
from tweepy import API, FileCache, Friendship, MemoryCache
from tweepy.parsers import Parser

test_tweet_id = '266367358078169089'
tweet_text = 'testing 1000'

"""Unit tests"""


class TweepyErrorTests(unittest.TestCase):

    def testpickle(self):
        """Verify exceptions can be pickled and unpickled."""
        import pickle
        from tweepy.error import TweepError

        e = TweepError('no reason', {'status': 200})
        e2 = pickle.loads(pickle.dumps(e))

        self.assertEqual(e.reason, e2.reason)
        self.assertEqual(e.response, e2.response)


class TweepyAPITests(TweepyTestCase):

    #@tape.use_cassette('testfailure.json')
    #def testapierror(self):
    #    from tweepy.error import TweepError
    #
    #    with self.assertRaises(TweepError) as cm:
    #        self.api.direct_messages()
    #
    #    reason, = literal_eval(cm.exception.reason)
    #    self.assertEqual(reason['message'], 'Bad Authentication data.')
    #    self.assertEqual(reason['code'], 215)
    #    self.assertEqual(cm.exception.api_code, 215)

    # TODO: Actually have some sort of better assertion
    @tape.use_cassette('testgetoembed.json')
    def testgetoembed(self):
        data = self.api.get_oembed("https://twitter.com/Twitter/status/" + test_tweet_id)
        self.assertEqual(data['author_name'], "Twitter")

    @tape.use_cassette('testparserargumenthastobeaparserinstance.json')
    def testparserargumenthastobeaparserinstance(self):
        """ Testing the issue https://github.com/tweepy/tweepy/issues/421"""
        self.assertRaises(TypeError, API, self.auth, parser=Parser)

    @tape.use_cassette('testhometimeline.json')
    def testhometimeline(self):
        self.api.home_timeline()

    @tape.use_cassette('testusertimeline.json')
    def testusertimeline(self):
        self.api.user_timeline()
        self.api.user_timeline(screen_name='Twitter')

    @tape.use_cassette('testmentionstimeline.json')
    def testmentionstimeline(self):
        self.api.mentions_timeline()

    @tape.use_cassette('testretweetsofme.json')
    def testretweetsofme(self):
        self.api.retweets_of_me()

    @tape.use_cassette('testretweetandunretweet.json')
    def testretweetandunretweet(self):
        self.api.retweet(test_tweet_id)
        self.api.unretweet(test_tweet_id)

    @tape.use_cassette('testretweets.json')
    def testretweets(self):
        self.api.retweets(test_tweet_id)

    @tape.use_cassette('testretweeters.json')
    def testretweeters(self):
        self.api.retweeters(test_tweet_id)

    @tape.use_cassette('testgetstatus.json')
    def testgetstatus(self):
        self.api.get_status(id=test_tweet_id)

    @tape.use_cassette('testupdateanddestroystatus.json')
    def testupdateanddestroystatus(self):
        # test update
        update = self.api.update_status(status=tweet_text)
        self.assertEqual(update.text, tweet_text)

        # test destroy
        deleted = self.api.destroy_status(id=update.id)
        self.assertEqual(deleted.id, update.id)

    @tape.use_cassette('testupdateanddestroystatus.json')
    def testupdateanddestroystatuswithoutkwarg(self):
        # test update, passing text as a positional argument (#554)
        update = self.api.update_status(tweet_text)
        self.assertEqual(update.text, tweet_text)

        # test destroy
        deleted = self.api.destroy_status(id=update.id)
        self.assertEqual(deleted.id, update.id)

    @tape.use_cassette('testupdatestatuswithmedia.yaml', serializer='yaml')
    def testupdatestatuswithmedia(self):
        update = self.api.update_with_media('examples/banner.png', status=tweet_text)
        self.assertIn(tweet_text + ' https://t.co', update.text)

    @tape.use_cassette('testgetuser.yaml', serializer='yaml')
    def testgetuser(self):
        u = self.api.get_user(screen_name='Twitter')
        self.assertEqual(u.screen_name, 'Twitter')

        u = self.api.get_user(user_id=783214)
        self.assertEqual(u.screen_name, 'Twitter')

    @tape.use_cassette('testlookupusers.json')
    def testlookupusers(self):
        def check(users):
            self.assertEqual(len(users), 2)
        check(self.api.lookup_users(user_id=[6844292, 6253282]))
        check(self.api.lookup_users(screen_name=['twitterapi', 'twitter']))

    @tape.use_cassette('testsearchusers.json')
    def testsearchusers(self):
        self.api.search_users('twitter')

    @tape.use_cassette('testme.json')
    def testme(self):
        me = self.api.me()
        self.assertEqual(me.screen_name, username)

    @tape.use_cassette('testlistdirectmessages.json')
    def testlistdirectmessages(self):
        self.api.list_direct_messages()

    @tape.use_cassette('testsendanddestroydirectmessage.json')
    def testsendanddestroydirectmessage(self):
        me = self.api.me()

        # send
        sent_dm = self.api.send_direct_message(me.id, text='test message')
        self.assertEqual(sent_dm.message_create['message_data']['text'], 'test message')
        self.assertEqual(int(sent_dm.message_create['sender_id']), me.id)
        self.assertEqual(int(sent_dm.message_create['target']['recipient_id']), me.id)

        # destroy
        self.api.destroy_direct_message(sent_dm.id)

    @tape.use_cassette('testcreatedestroyfriendship.yaml', serializer='yaml')
    def testcreatedestroyfriendship(self):
        enemy = self.api.destroy_friendship(screen_name='Twitter')
        self.assertEqual(enemy.screen_name, 'Twitter')

        friend = self.api.create_friendship(screen_name='Twitter')
        self.assertEqual(friend.screen_name, 'Twitter')

    @tape.use_cassette('testshowfriendship.json')
    def testshowfriendship(self):
        source, target = self.api.show_friendship(target_screen_name='twitter')
        self.assertTrue(isinstance(source, Friendship))
        self.assertTrue(isinstance(target, Friendship))

    @tape.use_cassette('testfriendsids.yaml', serializer='yaml')
    def testfriendsids(self):
        self.api.friends_ids(screen_name=username)

    @tape.use_cassette('testfollowersids.yaml', serializer='yaml')
    def testfollowersids(self):
        self.api.followers_ids(screen_name=username)

    @tape.use_cassette('testfriends.yaml', serializer='yaml')
    def testfriends(self):
        self.api.friends(screen_name=username)

    @tape.use_cassette('testfollowers.yaml', serializer='yaml')
    def testfollowers(self):
        self.api.followers(screen_name=username)

    @tape.use_cassette('testverifycredentials.json')
    def testverifycredentials(self):
        self.api.verify_credentials()

        # make sure that `me.status.entities` is not an empty dict
        me = self.api.verify_credentials(include_entities=True)
        self.assertTrue(me.status.entities)

        # `status` shouldn't be included
        me = self.api.verify_credentials(skip_status=True)
        self.assertFalse(hasattr(me, 'status'))

    @tape.use_cassette('testratelimitstatus.json')
    def testratelimitstatus(self):
        self.api.rate_limit_status()

    @tape.use_cassette('testupdateprofilecolors.json')
    def testupdateprofilecolors(self):
        original = self.api.me()
        updated = self.api.update_profile(profile_link_color='D0F900')

        # restore colors
        self.api.update_profile(
            profile_link_color=original.profile_link_color,
        )

        self.assertEqual(updated.profile_background_color, '000000')
        self.assertEqual(updated.profile_text_color, '000000')
        self.assertEqual(updated.profile_link_color, 'D0F900')
        self.assertEqual(updated.profile_sidebar_fill_color, '000000')
        self.assertEqual(updated.profile_sidebar_border_color, '000000')

    """
    def testupateprofileimage(self):
        self.api.update_profile_image('examples/profile.png')
    """

    @tape.use_cassette('testupdateprofilebannerimage.yaml', serializer='yaml')
    def testupdateprofilebannerimage(self):
        self.api.update_profile_banner('examples/banner.png')

    @tape.use_cassette('testupdateprofile.json')
    def testupdateprofile(self):
        original = self.api.me()
        profile = {
            'name': 'Tweepy test 123',
            'location': 'pytopia',
            'description': 'just testing things out'
        }
        updated = self.api.update_profile(**profile)
        self.api.update_profile(
            name = original.name, url = original.url,
            location = original.location, description = original.description
        )

        for k,v in profile.items():
            if k == 'email': continue
            self.assertEqual(getattr(updated, k), v)

    @tape.use_cassette('testfavorites.json')
    def testfavorites(self):
        self.api.favorites()

    @tape.use_cassette('testcreatedestroyfavorite.json')
    def testcreatedestroyfavorite(self):
        self.api.create_favorite(145344012)
        self.api.destroy_favorite(145344012)

    @tape.use_cassette('testcreatedestroyblock.yaml', serializer='yaml')
    def testcreatedestroyblock(self):
        self.api.create_block(screen_name='twitter')
        self.api.destroy_block(screen_name='twitter')
        self.api.create_friendship(screen_name='twitter')  # restore

    @tape.use_cassette('testblocks.json')
    def testblocks(self):
        self.api.blocks()

    @tape.use_cassette('testblocksids.json')
    def testblocksids(self):
        self.api.blocks_ids()

    # TODO: Rewrite test to be less brittle. It fails way too often.
    # def testcreateupdatedestroylist(self):
    #     params = {
    #         'owner_screen_name': username,
    #         'slug': 'tweeps'
    #     }
    #     l = self.api.create_list(name=params['slug'], **params)
    #     l = self.api.update_list(list_id=l.id, description='updated!')
    #     self.assertEqual(l.description, 'updated!')
    #     self.api.destroy_list(list_id=l.id)

    @tape.use_cassette('testlistsall.json')
    def testlistsall(self):
        self.api.lists_all()

    @tape.use_cassette('testlistsmemberships.json')
    def testlistsmemberships(self):
        self.api.lists_memberships()

    @tape.use_cassette('testlistsownerships.json')
    def testlistsownerships(self):
        self.api.lists_ownerships()

    @tape.use_cassette('testlistssubscriptions.json')
    def testlistssubscriptions(self):
        self.api.lists_subscriptions()

    @tape.use_cassette('testlisttimeline.json')
    def testlisttimeline(self):
        self.api.list_timeline(owner_screen_name='Twitter', slug='Official-Twitter-Accounts')

    @tape.use_cassette('testgetlist.json')
    def testgetlist(self):
        self.api.get_list(owner_screen_name='Twitter', slug='Official-Twitter-Accounts')

    @tape.use_cassette('testaddremovelistmember.json')
    def testaddremovelistmember(self):
        params = {
            'slug': 'test',
            'owner_screen_name': username,
            'screen_name': 'twitter'
        }

        def assert_list(l):
            self.assertEqual(l.name, params['slug'])

        assert_list(self.api.add_list_member(**params))
        assert_list(self.api.remove_list_member(**params))

    @tape.use_cassette('testaddremovelistmembers.json')
    def testaddremovelistmembers(self):
        params = {
            'slug': 'test',
            'owner_screen_name': username,
            'screen_name': ['Twitter', 'TwitterAPI']
        }

        def assert_list(l):
            self.assertEqual(l.name, params['slug'])

        assert_list(self.api.add_list_members(**params))
        assert_list(self.api.remove_list_members(**params))

    @tape.use_cassette('testlistmembers.json')
    def testlistmembers(self):
        self.api.list_members(owner_screen_name='Twitter', slug='Official-Twitter-Accounts')

    @tape.use_cassette('testshowlistmember.json')
    def testshowlistmember(self):
        self.assertTrue(self.api.show_list_member(owner_screen_name='Twitter', slug='Official-Twitter-Accounts', screen_name='TwitterAPI'))

    @tape.use_cassette('testsubscribeunsubscribelist.json')
    def testsubscribeunsubscribelist(self):
        params = {
            'owner_screen_name': 'Twitter',
            'slug': 'Official-Twitter-Accounts'
        }
        self.api.subscribe_list(**params)
        self.api.unsubscribe_list(**params)

    @tape.use_cassette('testlistsubscribers.json')
    def testlistsubscribers(self):
        self.api.list_subscribers(owner_screen_name='Twitter', slug='Official-Twitter-Accounts')

    @tape.use_cassette('testshowlistsubscriber.json')
    def testshowlistsubscriber(self):
        self.assertTrue(self.api.show_list_subscriber(owner_screen_name='Twitter', slug='Official-Twitter-Accounts', screen_name='TwitterMktg'))

    @tape.use_cassette('testsavedsearches.json')
    def testsavedsearches(self):
        s = self.api.create_saved_search('test')
        self.api.saved_searches()
        self.assertEqual(self.api.get_saved_search(s.id).query, 'test')
        self.api.destroy_saved_search(s.id)

    @tape.use_cassette('testsearch.json')
    def testsearch(self):
        self.api.search('tweepy')

    @tape.use_cassette('testgeoapis.json')
    def testgeoapis(self):
        def place_name_in_list(place_name, place_list):
            """Return True if a given place_name is in place_list."""
            return any(x.full_name.lower() == place_name.lower() for x in place_list)

        # Test various API functions using Austin, TX, USA
        self.assertEqual(self.api.geo_id(place_id='1ffd3558f2e98349').full_name, 'Dogpatch, San Francisco')
        self.assertTrue(place_name_in_list('Austin, TX',
            self.api.reverse_geocode(lat=30.2673701685, long= -97.7426147461)))  # Austin, TX, USA

    @tape.use_cassette('testsupportedlanguages.json')
    def testsupportedlanguages(self):
        languages = self.api.supported_languages()
        expected_dict = {
            "code": "en",
            "debug": False,
            "local_name": "English",
            "name": "English",
            "status": "production"
        }
        self.assertTrue(expected_dict in languages)

    @tape.use_cassette('testcachedresult.yaml', serializer='yaml')
    def testcachedresult(self):
        self.api.cache = MemoryCache()
        self.api.home_timeline()
        self.assertFalse(self.api.cached_result)
        self.api.home_timeline()
        self.assertTrue(self.api.cached_result)

    @tape.use_cassette('testcachedresult.yaml', serializer='yaml')
    def testcachedifferentqueryparameters(self):
        self.api.cache = MemoryCache()

        user1 = self.api.get_user(screen_name='TweepyDev')
        self.assertFalse(self.api.cached_result)
        self.assertEqual('TweepyDev', user1.screen_name)

        user2 = self.api.get_user(screen_name='Twitter')
        self.assertEqual('Twitter', user2.screen_name)
        self.assertFalse(self.api.cached_result)


class TweepyCacheTests(unittest.TestCase):
    timeout = 0.5
    memcache_servers = ['127.0.0.1:11211']  # must be running for test to pass

    def _run_tests(self, do_cleanup=True):
        # test store and get
        self.cache.store('testkey', 'testvalue')
        self.assertEqual(self.cache.get('testkey'), 'testvalue',
            'Stored value does not match retrieved value')

        # test timeout
        time.sleep(self.timeout)
        self.assertEqual(self.cache.get('testkey'), None,
            'Cache entry should have expired')

        # test cleanup
        if do_cleanup:
            self.cache.store('testkey', 'testvalue')
            time.sleep(self.timeout)
            self.cache.cleanup()
            self.assertEqual(self.cache.count(), 0, 'Cache cleanup failed')

        # test count
        for i in range(20):
            self.cache.store(f'testkey{i}', 'testvalue')
        self.assertEqual(self.cache.count(), 20, 'Count is wrong')

        # test flush
        self.cache.flush()
        self.assertEqual(self.cache.count(), 0, 'Cache failed to flush')

    def testmemorycache(self):
        self.cache = MemoryCache(timeout=self.timeout)
        self._run_tests()

    def testfilecache(self):
        os.mkdir('cache_test_dir')
        try:
            self.cache = FileCache('cache_test_dir', self.timeout)
            self._run_tests()
            self.cache.flush()
        finally:
            if os.path.exists('cache_test_dir'):
                shutil.rmtree('cache_test_dir')


if __name__ == '__main__':
    unittest.main()
