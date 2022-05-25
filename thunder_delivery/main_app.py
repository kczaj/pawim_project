import base64
import hashlib
import os
import uuid

import redis
from flask import Flask, render_template, request, make_response, abort, redirect, send_from_directory, url_for
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, unset_jwt_cookies
from flask_restplus import Api, Resource, fields
from authlib.integrations.flask_client import OAuth

from errors import UnauthorizedUserError, BadRequestError, NotFoundError

from oauth_config import *

baseURL = "https://localhost:8080"

app = Flask(__name__, static_url_path="")
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)
TOKEN_EXPIRES = 300

app.config["JWT_SECRET_KEY"] = os.environ.get("LOGIN_JWT_SECRET")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = TOKEN_EXPIRES
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.secret_key = SECRET_KEY

api_app = Api(app=app, version="1.0", title="ThunderDelivery API",
              description="Description of API for ThunderDelivery App", default_mediatype="multipart/form-data")

jwt = JWTManager(app)
oauth = OAuth(app)

auth0 = oauth.register(
    "PAMiW",
    api_base_url=OAUTH_BASE_URL,
    client_id=OAUTH_CLIENT_ID,
    client_secret=OAUTH_CLIENT_SECRET,
    access_token_url=OAUTH_ACCESS_TOKEN_URL,
    authorize_url=OAUTH_AUTHORIZE_URL,
    client_kwargs={"scope": OAUTH_SCOPE})


def make_couriers():
    usernames = ["kurier_courier", "drugiKurier_courier"]
    password = "zaq1@WSX"
    pesel = "11080696276"
    name = "Imie"
    surname = "Nazwisko"
    birth = "10/12/1999"
    street = "Dluga"
    number = "2"
    code = "02-332"
    country = "Polska"
    for username in usernames:
        if db.exists(username) == 1:
            continue
        else:
            db.hset(username, "username", username)
            db.hset(username, "password", hashlib.sha256(password.encode("utf-8")).hexdigest())
            db.hset(username, "pesel", pesel)
            db.hset(username, "name", name)
            db.hset(username, "surname", surname)
            db.hset(username, "birth_date", birth)
            db.hset(username, "street", street)
            db.hset(username, "number", number)
            db.hset(username, "code", code)
            db.hset(username, "country", country)


def make_lockers():
    lockers = ["locker_1", "locker_2"]
    for locker in lockers:
        if locker in db.smembers("lockers"):
            continue
        else:
            db.sadd("lockers", locker)


@app.before_first_request
def setup():
    make_couriers()
    make_lockers()


page_namespace = api_app.namespace("home", description="Pages API")
login_namespace = api_app.namespace("login", description="Login API")
register_namespace = api_app.namespace("register", description="Register API")
logout_namespace = api_app.namespace("logout", description="Logout API")
username_check_namespace = api_app.namespace("username", description="Username API")


@page_namespace.route("/")
class Home(Resource):

    @api_app.doc(responses={200: "OK", 401: "Unauthorized"})
    def get(self):
        permissions = check_cookie_permission(request)
        if permissions[0]:
            return redirect(api_app.base_url + "home/user")
        return make_response(render_template("main/index.html"))


@page_namespace.route("/login")
class Login(Resource):

    @api_app.doc(responses={200: "OK", 401: "Unauthorized"})
    def get(self):
        permissions = check_cookie_permission(request)
        if permissions[0]:
            return redirect(api_app.base_url + "home/user")
        return make_response(render_template("main/login.html"))


@page_namespace.route("/register")
class Register(Resource):

    @api_app.doc(responses={200: "OK", 401: "Unauthorized"})
    def get(self):
        permissions = check_cookie_permission(request)
        if permissions[0]:
            return redirect(api_app.base_url + "home/user")
        return make_response(render_template("main/register.html"))


@page_namespace.route("/user")
class User(Resource):

    @api_app.doc(responses={200: "OK", 401: "Unauthorized"})
    def get(self):
        permissions = check_cookie_permission(request)
        if permissions[0]:
            response = make_response(
                render_template("main/site_after_log.html", username=permissions[1]))
            response = make_session_cookies(response, permissions[1], request)
            return response
        else:
            raise UnauthorizedUserError


@page_namespace.route("/user/newshipping")
class NewShiping(Resource):

    @api_app.doc(responses={200: "OK", 401: "Unauthorized"})
    def get(self):
        permissions = check_cookie_permission(request)
        if permissions[0]:
            response = make_response(render_template("main/new_package_site.html", username=permissions[1]))
            response = make_session_cookies(response, permissions[1], request)
            return response
        else:
            raise UnauthorizedUserError


@login_namespace.route("/")
class LoginData(Resource):

    def __init__(self, args):
        super().__init__(args)

    login_model = api_app.model("Login model",
                                {
                                    "username": fields.String(required=True, description="Username",
                                                              help="Username cannot be blank"),
                                    "password": fields.String(required=True, description="Password",
                                                              help="Password cannot be blank")
                                })

    post_parser = api_app.parser()
    post_parser.add_argument('username', location='form', type='string', required=True)
    post_parser.add_argument('password', location='form', type='string', required=True)

    @api_app.expect(post_parser, validate=True)
    @api_app.doc(responses={200: "Logged in", 401: "Wrong password or username", 400: "Invalid arguments",
                            404: "No such username"})
    # @api_app.consume('multipart/form-data')
    def post(self):
        try:
            username = request.form["username"].encode("utf-8")
            password = request.form["password"].encode("utf-8")
            if username is not None and password is not None:
                if db.exists(username):
                    real_password = db.hget(username, "password")
                    if hashlib.sha256(password).hexdigest() == real_password:
                        body = {
                            "message": "Correct login",
                            "error_code": "200"
                        }
                        response = make_response(body, 200)
                        response = make_session_cookies(response, username.decode("utf-8"))
                        return response
                    else:
                        raise UnauthorizedUserError
                else:
                    raise NotFoundError
            else:
                raise BadRequestError
        except UnauthorizedUserError as e:
            login_namespace.abort(401, e.__doc__, status="Unauthorized.", statusCode="401")
        except NotFoundError as e:
            login_namespace.abort(404, e.__doc__, status="Not found.", statusCode="404")
        except BadRequestError as e:
            login_namespace.abort(400, e.__doc__, status="Bad request.", statusCode="400")


@register_namespace.route("/")
class RegisterData(Resource):
    def __init__(self, args):
        super().__init__(args)

    register_model = api_app.model("Register model",
                                   {
                                       "username": fields.String(required=True, description="Username",
                                                                 help="Username cannot be blank"),
                                       "password": fields.String(required=True, description="Password",
                                                                 help="Password cannot be blank"),
                                       "pesel": fields.String(required=True, description="PESEL",
                                                              help="PESEL cannot be blank"),
                                       "name": fields.String(required=True, description="Name",
                                                             help="Name cannot be blank"),
                                       "surname": fields.String(required=True, description="Surname",
                                                                help="Surname cannot be blank"),
                                       "birth_data": fields.String(required=True, description="Birth date",
                                                                   help="Birth date cannot be blank"),
                                       "street": fields.String(required=True, description="Street",
                                                               help="Street cannot be blank"),
                                       "number": fields.String(required=True, description="Number",
                                                               help="Number cannot be blank"),
                                       "code": fields.String(required=True, description="Postal code",
                                                             help="Code cannot be blank"),
                                       "country": fields.String(required=True, description="Country",
                                                                help="Country cannot be blank"),
                                   })

    post_parser = api_app.parser()
    post_parser.add_argument('username', location='form', type='string', required=True)
    post_parser.add_argument('password', location='form', type='string', required=True)
    post_parser.add_argument('pesel', location='form', type='string', required=True)
    post_parser.add_argument('name', location='form', type='string', required=True)
    post_parser.add_argument('surname', location='form', type='string', required=True)
    post_parser.add_argument('birth_data', location='form', type='string', required=True)
    post_parser.add_argument('street', location='form', type='string', required=True)
    post_parser.add_argument('number', location='form', type='string', required=True)
    post_parser.add_argument('code', location='form', type='string', required=True)
    post_parser.add_argument('country', location='form', type='string', required=True)

    @api_app.expect(post_parser, validate=True)
    @api_app.doc(responses={201: "Created", 401: "Login taken", 400: "Invalid arguments"})
    def post(self):
        try:
            username = request.form["username"].encode("utf-8")
            if username is None:
                raise BadRequestError
            if db.exists(username) == 1:
                raise UnauthorizedUserError
            else:
                db.hset(username, "username", username)
                db.hset(username, "password", hashlib.sha256(request.form["password"].encode("utf-8")).hexdigest())
                db.hset(username, "pesel", request.form["pesel"].encode("utf-8"))
                db.hset(username, "name", request.form["name"].encode("utf-8"))
                db.hset(username, "surname", request.form["surname"].encode("utf-8"))
                db.hset(username, "birth_date", request.form["birth_date"].encode("utf-8"))
                db.hset(username, "street", request.form["street"].encode("utf-8"))
                db.hset(username, "number", request.form["number"].encode("utf-8"))
                db.hset(username, "code", request.form["code"].encode("utf-8"))
                db.hset(username, "country", request.form["country"].encode("utf-8"))
                body = {
                    "message": "Registered successfully",
                    "error_code": "201"
                }
                response = make_response(body, 201)
                response = make_session_cookies(response, username.decode("utf-8"))
                return response
        except UnauthorizedUserError as e:
            register_namespace.abort(401, e.__doc__, status="Unauthorized. Login already taken", statusCode="401")
        except BadRequestError as e:
            register_namespace.abort(400, e.__doc__, status="Bad request.", statusCode="400")


@logout_namespace.route("/")
class LogoutData(Resource):

    @api_app.doc(responses={200: "Loged out", 401: "Unauthorized"})
    def post(self):
        try:
            permissions = check_cookie_permission(request)
            if permissions[0]:
                db.hdel("session_ids", request.cookies.get("session_id"))
                db.hdel("jwts", permissions[1])
                response = make_response({
                    "message": "Loged out",
                    "error": 200
                }, 200)
                response.set_cookie("session_id", expires=0)
                unset_jwt_cookies(response)
                if request.cookies.get("oauth") == "true":
                    response.set_cookie("oauth", expires=0)
                    return logout()
                return response
            else:
                raise UnauthorizedUserError
        except UnauthorizedUserError as e:
            login_namespace.abort(401, e.__doc__, status="Unauthorized.", statusCode="401")


@username_check_namespace.route("/<string:username>")
class UsernameCheckData(Resource):

    @api_app.doc(responses={200: "Login taken", 400: "Invalid argument", 404: "Login free"})
    def get(self, username):
        try:
            if username is None:
                raise BadRequestError
            if db.exists(username) == 1:
                body = {
                    "message": "Login is already taken.",
                    "error_code": "200"
                }
                return make_response(body, 200)
            else:
                body = {
                    "message": "Login is free.",
                    "error_code": "404"
                }
                return make_response(body, 404)
        except BadRequestError as e:
            username_check_namespace.abort(400, e.__doc__, status="Bad request.", statusCode="400")


@app.route("/callback")
def callback():
    auth0.authorize_access_token()
    resp = auth0.get("userinfo")
    nickname = resp.json()[NICKNAME]
    username = nickname + "_oauth"

    if db.exists(username) == 0:
        db.hset(username, "username", username)

    response = redirect(api_app.base_url + "home/user")
    response = make_session_cookies(response, username)
    response.set_cookie("oauth", "true")

    return response


@app.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=OAUTH_CALLBACK_URL,
        audience="")


@app.route("/logout")
def logout():
    url_params = "returnTo=" + url_for("logout_info", _external=True)
    url_params += "&"
    url_params += "client_id=" + OAUTH_CLIENT_ID

    return redirect(auth0.api_base_url + "/v2/logout?" + url_params)


@app.route("/logout_info")
def logout_info():
    return redirect(api_app.base_url + "home/")


@app.errorhandler(400)
def page_not_found(error):
    message = "Seems like you can't speak to me."
    return make_response(render_template("main/page_error.html", message=message), 400)


@app.errorhandler(UnauthorizedUserError)
def page_unauthorized(error):
    message = "Seems like you aren't authorized."
    return make_response(render_template("main/page_error.html", message=message), 401)


@app.errorhandler(403)
def page_forbidden(error):
    message = "Seems like you can't get here."
    return make_response(render_template("main/page_error.html", message=message), 403)


@app.errorhandler(404)
def page_not_found(error):
    message = "Seems like we can't find that page."
    return make_response(render_template("main/page_error.html", message=message), 404)


@app.errorhandler(500)
def internal_error(error):
    message = "Seems like we have issues on the server."
    return make_response(render_template("main/page_error.html", message=message), 500)


def make_session_cookies(response, username, req=None):
    if req is not None:
        db.hdel("session_ids", request.cookies.get("session_id"))
        db.hdel("jwts", username)
    username_decoded = username
    session_id = hashlib.sha256(username_decoded.encode("utf-8")).hexdigest() + "_" + uuid.uuid4().__str__()
    session_id = base64.b64encode(session_id.encode("utf-8"))
    jwt_token = create_access_token(identity=username_decoded)
    db.hset("session_ids", session_id, username_decoded)
    db.hset("jwts", username_decoded, jwt_token)
    response.set_cookie("session_id", session_id, max_age=TOKEN_EXPIRES, secure=True, httponly=True)
    set_access_cookies(response, jwt_token, TOKEN_EXPIRES)
    return response


def check_cookie_permission(req):
    cookie = req.cookies.get("session_id")
    if cookie is None:
        return False, ""
    decoded_cookie = base64.b64decode(cookie.encode("utf-8"))
    username = decoded_cookie.decode("utf-8").split("_")[0]
    username_in_db = db.hget("session_ids", cookie)
    if decoded_cookie is not None and username_in_db is not None and username == hashlib.sha256(
            username_in_db.encode("utf-8")).hexdigest():
        return True, username_in_db
    else:
        return False, ""
