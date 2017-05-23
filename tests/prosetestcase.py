from flask import Flask


__author__ = 'slippers'


class ProseTestCase():

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = "test-secret"
        self.app.config["WTF_CSRF_ENABLED"] = False  # to bypass CSRF token
        self.client = self.app.test_client()

        @self.app.route("/")
        def index():
            return "Hello World!"

    def _create_storage(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def tearDown(self):
        raise NotImplementedError("Subclass must implement abstract method")
