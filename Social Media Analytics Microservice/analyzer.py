from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the auth token
auth_token = os.getenv("AUTH_TOKEN")


class Social_Media_Analytics(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/users':
            self.get_top_users()
        elif self.path.startswith('/posts'):
            self.get_top_posts()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def get_top_users(self):
        users = self.fetch_data('http://20.244.56.144/test/users')
        posts = self.fetch_data('http://20.244.56.144/test/users/1/posts')

        user_post_count = {}
        for post in posts.get('posts', []):
            user_id = post['userid']
            user_post_count[user_id] = user_post_count.get(user_id, 0) + 1

        sorted_users = sorted(user_post_count.items(),
                              key=lambda x: x[1], reverse=True)[:5]

        top_users = [{"user_id": user_id, "name": users['users'].get(
            str(user_id), "Unknown"), "post_count": count} for user_id, count in sorted_users]

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(top_users).encode())

    def get_top_posts(self):
        query = self.path.split('?')[-1]
        params = dict(qc.split('=') for qc in query.split('&'))
        post_type = params.get('type', 'popular')

        posts = self.fetch_data('http://20.244.56.144/test/users/1/posts')
        comments = self.fetch_data(
            'http://20.244.56.144/test/posts/150/comments')

        post_comment_count = {}
        for comment in comments.get('comments', []):
            post_id = comment['postid']
            post_comment_count[post_id] = post_comment_count.get(
                post_id, 0) + 1

        if post_type == 'popular':
            max_comments = max(post_comment_count.values(), default=0)
            top_posts = [post for post in posts.get(
                'posts', []) if post_comment_count.get(post['id'], 0) == max_comments]
        else:
            top_posts = sorted(posts.get('posts', []),
                               key=lambda x: x['id'], reverse=True)[:5]

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(top_posts).encode())

    def fetch_data(self, url):
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Bearer {auth_token}')
        try:
            with urllib.request.urlopen(req) as response:
                data = response.read().decode()
                return json.loads(data)
        except urllib.error.URLError as e:
            print(f"Error fetching data from {url}: {e}")
            return {}


def run(server_class=HTTPServer, handler_class=Social_Media_Analytics, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
