import hashlib
import json
import os

import redis
from flask import Flask, render_template, request, make_response, abort, redirect, send_from_directory, send_file, \
    jsonify, url_for
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required, \
    get_jwt_identity
from flask_restplus import Api, Resource, fields

from errors import UnauthorizedUserError, NotFoundError, BadRequestError, ForbiddenError
from main_app import make_session_cookies, check_cookie_permission
from db_app import sort_critera, make_id
from authlib.integrations.flask_client import OAuth

from oauth_config import *

app = Flask(__name__, static_url_path="")
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)
TOKEN_EXPIRES = 300

app.config["JWT_SECRET_KEY"] = os.environ.get("LOGIN_JWT_SECRET")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = TOKEN_EXPIRES
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
PACKAGES_PER_PAGE = 3
app.secret_key = SECRET_KEY

api_app = Api(app=app, version="1.0", title="ThunderDelivery Courier App API",
              description="Description of API for ThunderDelivery App", default_mediatype="multipart/form-data")

jwt = JWTManager(app)

page_namespace = api_app.namespace("home", description="Pages API")
login_namespace = api_app.namespace("login", description="Login API")
logout_namespace = api_app.namespace("logout", description="Logout API")
packages_namespace = api_app.namespace("packages", description="Package API")
access_namespace = api_app.namespace("access", description="Access locker API")
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


@page_namespace.route("/")
class Home(Resource):

    @api_app.doc(responses={200: "OK"})
    def get(self):
        return make_response(render_template("courier/index.html"), 200)


@page_namespace.route("/user/")
class User(Resource):

    @api_app.doc(responses={200: "OK", 401: "Unauthorized"})
    def get(self):
        permissions = check_cookie_permission(request)
        if permissions[0]:
            response = make_response(
                render_template("courier/site_after_log.html"))
            response = make_session_cookies(response, permissions[1], request)
            return response
        else:
            raise UnauthorizedUserError


@page_namespace.route("/pick/")
class PickUp(Resource):

    @api_app.doc(responses={200: "OK", 401: "Unauthorized"})
    def get(self):
        permissions = check_cookie_permission(request)
        if permissions[0]:
            response = make_response(
                render_template("courier/pick_up_package.html"))
            response = make_session_cookies(response, permissions[1], request)
            return response
        else:
            raise UnauthorizedUserError


@page_namespace.route("/access/")
class AccessLocker(Resource):

    @api_app.doc(responses={200: "OK", 401: "Unauthorized"})
    def get(self):
        permissions = check_cookie_permission(request)
        if permissions[0]:
            response = make_response(
                render_template("courier/access_locker.html"))
            response = make_session_cookies(response, permissions[1], request)
            return response
        else:
            raise UnauthorizedUserError


@page_namespace.route("/offline/")
class Offline(Resource):

    @api_app.doc(responses={200: "OK"})
    def get(self):
        return make_response(render_template("courier/offline.html"), 200)


@page_namespace.route("/error/")
class Error(Resource):

    @api_app.doc(responses={200: "OK"})
    def get(self):
        return make_response(render_template("courier/error.html"), 200)


@login_namespace.route("/")
class LoginData(Resource):

    def __init__(self, args):
        super().__init__(args)

    post_parser = api_app.parser()
    post_parser.add_argument('username', location='form', type='string', required=True)
    post_parser.add_argument('password', location='form', type='string', required=True)

    @api_app.expect(post_parser, validate=True)
    @api_app.doc(responses={200: "Loged in", 401: "Wrong password or username", 400: "Invalid arguments",
                            404: "No such username"})
    def post(self):
        try:
            username = request.form["username"]
            password = request.form["password"].encode("utf-8")
            username = username + "_courier"
            username = username.encode("utf-8")
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
            logout_namespace.abort(401, e.__doc__, status="Unauthorized.", statusCode="401")


@packages_namespace.route("/")
class Packages(Resource):

    def __init__(self, args):
        super().__init__(args)

    @api_app.doc(responses={200: "OK", 401: "Unauthorized"})
    @jwt_required
    def get(self):
        username = get_jwt_identity()
        db_name = "packages_" + username
        package_ids = db.smembers(db_name)
        packages = []
        for package_id in package_ids:
            package = {
                "created": db.hget("packages", package_id),
                "status": db.hget(package_id, "status"),
                "id": package_id
            }
            package = json.dumps(package)
            packages.append(package)

        return make_response(jsonify({"packages": packages}), 200)

    post_parser = api_app.parser()
    post_parser.add_argument('id', location='form', type='string', required=True)

    @api_app.doc(responses={200: "OK", 400: "Bad request", 404: "Not found", 403: "Forbidden", 401: "Unauthorized"})
    @jwt_required
    @api_app.expect(post_parser, validate=True)
    def post(self):
        username = get_jwt_identity()
        id = request.form.get("id")
        try:
            if id is None or id == "":
                raise BadRequestError
            if db.exists(id) == 1:
                status = db.hget(id, "status")
                if status == "NEW":
                    db.hset(id, "status", "COURIER")
                    name = "packages_" + username
                    db.sadd(name, id)
                else:
                    raise ForbiddenError
            else:
                raise NotFoundError
        except NotFoundError as e:
            packages_namespace.abort(404, e.__doc__, status="Not found", statusCode="404")
        except ForbiddenError as e:
            packages_namespace.abort(403, e.__doc__, status="Forbidden", statusCode="403")
        except BadRequestError as e:
            packages_namespace.abort(400, e.__doc__, status="Bad request", statusCode="400")


@packages_namespace.route("/<int:start>/")
class PaginatedPackages(Resource):

    @api_app.doc(responses={200: "OK", 401: "Unauthorized"})
    @jwt_required
    def get(self, start):
        try:
            if start - PACKAGES_PER_PAGE < -PACKAGES_PER_PAGE:
                raise BadRequestError
            username = get_jwt_identity()
            db_name = "packages_" + username
            package_ids_in_db = list(db.smembers(db_name))
            package_ids_in_db.sort(key=sort_critera)
            packages = []
            package_ids = package_ids_in_db[start:start + PACKAGES_PER_PAGE]
            for package_id in package_ids:
                package = {
                    "street": db.hget(package_id, "receiver_street"),
                    "number": db.hget(package_id, "receiver_number"),
                    "code": db.hget(package_id, "receiver_code"),
                    "id": package_id
                }
                package = json.dumps(package)
                packages.append(package)

            if start == 0:
                prev_url = ""
            else:
                prev_url = api_app.base_url + "packages/" + str(start - PACKAGES_PER_PAGE) + "/"

            if start + PACKAGES_PER_PAGE >= len(package_ids_in_db):
                next_url = ""
            else:
                next_url = api_app.base_url + "packages/" + str(start + PACKAGES_PER_PAGE) + "/"

            return make_response(jsonify({"packages": packages, "prev_url": prev_url, "next_url": next_url}), 200)

        except BadRequestError as e:
            packages_namespace.abort(400, e.__doc__, status="Bad request", statusCode="400")


@access_namespace.route("/<string:locker_id>/")
class AccessLocker(Resource):

    @api_app.doc(responses={200: "OK", 401: "Unauthorized"})
    @jwt_required
    def get(self, locker_id):
        try:
            if locker_id is None or locker_id not in db.smembers("lockers") or locker_id == "":
                raise BadRequestError
            lista = []
            token = make_id(lista)
            courier_id = get_jwt_identity()
            db.hset(token, "locker_id", locker_id)
            db.hset(token, "courier_id", courier_id)
            db.expire(token, 60)

            return make_response({"status": "OK", "statusCode": "200", "token": token})
        except BadRequestError as e:
            access_namespace.abort(400, e.__doc__, status="Bad request", statusCode="400")


@app.route("/callback")
def callback():
    auth0.authorize_access_token()
    resp = auth0.get("userinfo")
    nickname = resp.json()[NICKNAME]
    username = nickname + "_courier_oauth"

    if db.exists(username) == 0:
        db.hset(username, "username", username)

    response = redirect(api_app.base_url + "home/user")
    response = make_session_cookies(response, username)
    response.set_cookie("oauth", "true")
    response.set_cookie("courier_id", nickname, max_age=10)

    return response


@app.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=OAUTH_CALLBACK_URL_COURIER,
        audience="")


@app.route("/logout_info")
def logout_info():
    return redirect(api_app.base_url + "home/")


@app.route("/logoutt")
def logout():
    url_params = "returnTo=" + url_for("logout_info", _external=True)
    url_params += "&"
    url_params += "client_id=" + OAUTH_CLIENT_ID

    return redirect(auth0.api_base_url + "/v2/logout?" + url_params)


@app.errorhandler(UnauthorizedUserError)
def page_unauthorized(error):
    message = "Seems like you aren't authorized."
    return make_response(render_template("courier/page_error.html", message=message), 401)
