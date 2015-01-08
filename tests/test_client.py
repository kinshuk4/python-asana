from .helpers import *

from mock import patch

class TestClient(ClientTestCase):

    def test_users_me_not_authorized(self):
        res = {
            "errors": [
                { "message": "Not Authorized" }
            ]
        }
        responses.add(GET, 'http://app/users/me', status=401, body=json.dumps(res), match_querystring=True)
        self.assertRaises(asana.error.NoAuthorizationError, self.client.users.me)

    def test_tasks_find_all_invalid_request(self):
        res = {
            "errors": [
                { "message": "workspace: Missing input" }
            ]
        }
        responses.add(GET, 'http://app/tasks', status=400, body=json.dumps(res), match_querystring=True)
        self.assertRaises(asana.error.InvalidRequestError, self.client.tasks.find_all)

    def test_users_me_server_error(self):
        res = {
            "errors": [
                {
                    "message": "Server Error",
                    "phrase": "6 sad squid snuggle softly"
                }
            ]
        }
        responses.add(GET, 'http://app/users/me', status=500, body=json.dumps(res), match_querystring=True)
        self.assertRaises(asana.error.ServerError, self.client.users.me)

    def test_users_find_by_id_not_found(self):
        res = {
            "errors": [
                { "message": "user: Unknown object: 1234124312341" }
            ]
        }
        responses.add(GET, 'http://app/users/1234', status=404, body=json.dumps(res), match_querystring=True)
        self.assertRaises(asana.error.NotFoundError, self.client.users.find_by_id, (1234))

    def test_users_find_by_id_forbidden(self):
        res = {
            "errors": [
                { "message": "user: Forbidden" }
            ]
        }
        responses.add(GET, 'http://app/users/1234', status=403, body=json.dumps(res), match_querystring=True)
        self.assertRaises(asana.error.ForbiddenError, self.client.users.find_by_id, (1234))

    def test_option_pretty(self):
        res = {
            "data": { "email": "sanchez@...", "id": 999, "name": "Greg Sanchez" }
        }
        # responses.add(GET, 'http://app/users/me?opt_pretty', status=200, body=json.dumps(res), match_querystring=True)
        responses.add(GET, 'http://app/users/me?opt_pretty=true', status=200, body=json.dumps(res), match_querystring=True)
        self.assertEqual(self.client.users.me(pretty=True), res['data']) 

    def test_option_fields(self):
        res = {
            "data": { "name": "Make a list", "notes": "Check it twice!", "id": 1224 }
        }
        responses.add(GET, 'http://app/tasks/1224?opt_fields=name%2Cnotes', status=200, body=json.dumps(res), match_querystring=True)
        self.assertEqual(self.client.tasks.find_by_id(1224, fields=['name','notes']), res['data'])

    def test_option_expand(self):
        req = {
            'data': { 'assignee': 1234 },
            'options': { 'expand' : ['projects'] }
        }
        res = {
            "data": {
                "id": 1001,
                "projects": [
                    {
                        "archived": false,
                        "created_at": "",
                        "followers": [],
                        "modified_at": "",
                        "notes": "",
                        "id": 1331,
                        "name": "Things to buy"
                    }
                ]
                # ...
            }
        }
        responses.add(PUT, 'http://app/tasks/1001', status=200, body=json.dumps(res), match_querystring=True)
        # -d "assignee=1234" \
        # -d "options.expand=%2Aprojects%2A"
        self.assertEqual(self.client.tasks.update(1001, req['data'], expand=['projects']), res['data'])
        self.assertEqual(json.loads(responses.calls[0].request.body), req)

    def test_pagination(self):
        res = {
            "data": [
                { "id": 1000, "name": "Task 1" }
            ],
            "next_page": {
                "offset": "yJ0eXAiOiJKV1QiLCJhbGciOiJIRzI1NiJ9",
                "path": "/tasks?project=1337&limit=5&offset=yJ0eXAiOiJKV1QiLCJhbGciOiJIRzI1NiJ9",
                "uri": "https://app.asana.com/api/1.0/tasks?project=1337&limit=5&offset=yJ0eXAiOiJKV1QiLCJhbGciOiJIRzI1NiJ9"
            }
        }
        # responses.add(GET, 'http://app/tasks?project=1337&limit=5&offset=eyJ0eXAiOJiKV1iQLCJhbGciOiJIUzI1NiJ9', status=200, body=json.dumps(res), match_querystring=True)
        responses.add(GET, 'http://app/projects/1337/tasks?limit=5&offset=eyJ0eXAiOJiKV1iQLCJhbGciOiJIUzI1NiJ9', status=200, body=json.dumps(res), match_querystring=True)

        self.assertEqual(self.client.tasks.find_by_project(1337, { 'limit': 5, 'offset': 'eyJ0eXAiOJiKV1iQLCJhbGciOiJIUzI1NiJ9'}), res['data'])

    def test_pagination_iterator(self):
        responses.add(GET, 'http://app/projects/1337/tasks?limit=2', status=200, body=json.dumps({ 'data': ['a', 'b'], 'next_page': { 'offset': 'a' } }), match_querystring=True)
        responses.add(GET, 'http://app/projects/1337/tasks?limit=2&offset=a', status=200, body=json.dumps({ 'data': ['c'], 'next_page': null }), match_querystring=True)

        iterator = self.client.tasks.find_by_project_iterator(1337, { 'limit': '2' })
        self.assertEqual(next(iterator), 'a')
        self.assertEqual(next(iterator), 'b')
        self.assertEqual(next(iterator), 'c')
        self.assertRaises(StopIteration, next, (iterator))

    @patch('time.sleep')
    def test_rate_limiting(self, time_sleep):
        res = [
            (429, { 'Retry-After': '10' }, '{}'),
            (200, {}, json.dumps({ 'data': 'me' }))
        ]
        responses.add_callback(responses.GET, 'http://app/users/me', callback=lambda r: res.pop(0), content_type='application/json')

        self.assertEqual(self.client.users.me(), 'me')
        self.assertEqual(len(responses.calls), 2)
        time_sleep.assert_called_once_with(10)

    @patch('time.sleep')
    def test_rate_limited_twice(self, time_sleep):
        res = [
            (429, { 'Retry-After': '10' }, '{}'),
            (429, { 'Retry-After': '1' }, '{}'),
            (200, {}, json.dumps({ 'data': 'me' }))
        ]
        responses.add_callback(responses.GET, 'http://app/users/me', callback=lambda r: res.pop(0), content_type='application/json')

        self.assertEqual(self.client.users.me(), 'me')
        self.assertEqual(len(responses.calls), 3)
        time_sleep.assert_called_twice()
