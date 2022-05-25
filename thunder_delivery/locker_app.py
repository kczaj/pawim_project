import hashlib
import json
import os

import redis
from flask import Flask, render_template, request, make_response, abort, redirect, send_from_directory, jsonify
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, unset_jwt_cookies
from flask_restplus import Api, Resource, fields

from errors import BadRequestError, NotFoundError, ForbiddenError

from db_app import sort_critera

app = Flask(__name__, static_url_path="")
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)
TOKEN_EXPIRES = 300

app.config["JWT_SECRET_KEY"] = os.environ.get("LOGIN_JWT_SECRET")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = TOKEN_EXPIRES
app.config['JWT_TOKEN_LOCATION'] = ['cookies']

api_app = Api(app=app, version="1.0", title="ThunderDelivery Parcel Locker API",
              description="Description of API for ThunderDelivery App", default_mediatype="multipart/form-data")

jwt = JWTManager(app)

page_namespace = api_app.namespace("home", description="Pages API")
locker_namespace = api_app.namespace("locker", description="Locker API")
package_namespace = api_app.namespace("packages", description="Package API")

PACKAGES_PER_PAGE = 2


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
        locker_id = request.cookies.get("locker_id")
        if locker_id is None or locker_id not in db.smembers("lockers"):
            return make_response(render_template("locker/index.html"), 200)
        else:
            return make_response(render_template("locker/locker.html"), 200)


@page_namespace.route("/send/")
class LockerSend(Resource):

    @api_app.doc(responses={200: "OK"})
    def get(self):
        locker_id = request.cookies.get("locker_id")
        if locker_id is None or locker_id not in db.smembers("lockers"):
            return redirect(api_app.base_url + "home/")
        else:
            return make_response(render_template("locker/send.html"), 200)


@page_namespace.route("/pickup/")
class LockerPickUp(Resource):

    @api_app.doc(responses={200: "OK"})
    def get(self):
        locker_id = request.cookies.get("locker_id")
        if locker_id is None or locker_id not in db.smembers("lockers"):
            return redirect(api_app.base_url + "home/")
        else:
            return make_response(render_template("locker/pickup.html"), 200)


@page_namespace.route("/list/")
class PackageList(Resource):

    @api_app.doc(responses={200: "OK"})
    def get(self):
        locker_id = request.cookies.get("locker_id")
        token = request.cookies.get("token")
        app.logger.debug(token)
        if (locker_id is None or locker_id not in db.smembers("lockers")) or (token is None or db.exists(token) == 0):
            return redirect(api_app.base_url + "home/")
        else:
            return make_response(render_template("locker/list.html"), 200)


@locker_namespace.route("/<string:id>/")
class Locker(Resource):

    @api_app.doc(responses={200: "OK", 400: "Bad request", 404: "Not found"})
    def get(self, id):
        try:
            if id is None or id == "":
                raise BadRequestError
            if id in db.smembers("lockers"):
                response = make_response({"status": "OK", "statusCode": "200"}, 200)
                response.set_cookie("locker_id", id)
                return response
            else:
                raise NotFoundError
        except BadRequestError as e:
            locker_namespace.abort(400, e.__doc__, status="Bad request", statusCode="400")
        except NotFoundError as e:
            locker_namespace.abort(404, e.__doc__, status="Not found", statusCode="404")

    @api_app.doc(responses={200: "OK", 400: "Bad request", 404: "Not found"})
    def post(self, id):
        locker_id = request.cookies.get("locker_id")
        package_id = request.form.get("id")
        try:
            if package_id is None or package_id == "":
                raise BadRequestError
            if db.exists(package_id) == 0 and package_id not in db.hkeys("packages"):
                raise NotFoundError
            if locker_id is None or locker_id == "" or locker_id not in db.smembers("lockers"):
                raise BadRequestError

            if db.hget(package_id, "status") != "NEW":
                raise ForbiddenError
            name = locker_id + "_packages"
            db.sadd(name, package_id)
            db.hset(package_id, "status", "LOCKER")
            return make_response({"status": "OK", "statusCode": "200"}, 200)
        except BadRequestError as e:
            locker_namespace.abort(400, e.__doc__, status="Bad request", statusCode="400")
        except NotFoundError as e:
            locker_namespace.abort(404, e.__doc__, status="Not found", statusCode="404")
        except ForbiddenError as e:
            locker_namespace.abort(403, e.__doc__, status="Forbidden", statusCode="403")


@locker_namespace.route("/<string:id>/access/<string:token>/")
class Access(Resource):

    @api_app.doc(responses={200: "OK", 400: "Bad request", 403: "Forbidden"})
    def get(self, id, token):
        try:
            locker_id = request.cookies.get("locker_id")
            if locker_id is None or locker_id == "" or locker_id not in db.smembers("lockers"):
                raise BadRequestError
            if db.hgetall(token) is None or db.hget(token, "locker_id") != locker_id:
                raise ForbiddenError
            else:
                response = make_response({"status": "OK", "statusCode": "200"}, 200)
                response.set_cookie("courier_id", db.hget(token, "courier_id"), max_age=60)
                response.set_cookie("token", token, max_age=60)
                return response
        except ForbiddenError as e:
            locker_namespace.abort(403, e.__doc__, status="Forbidden", statusCode="403")
        except BadRequestError as e:
            locker_namespace.abort(400, e.__doc__, status="Bad request", statusCode="400")


@package_namespace.route("/<int:start>/")
class PaginatedPackages(Resource):

    @api_app.doc(responses={200: "OK", 400: "Bad request", 403: "Forbidden"})
    def get(self, start):
        try:
            token = request.cookies.get("token")
            if token is None or db.exists(token) == 0:
                raise ForbiddenError
            locker_id = request.cookies.get("locker_id")

            if locker_id is None or locker_id not in db.smembers("lockers"):
                raise BadRequestError
            if start - PACKAGES_PER_PAGE < -PACKAGES_PER_PAGE:
                raise BadRequestError
            db_name = locker_id + "_packages"
            package_ids_in_db = list(db.smembers(db_name))
            package_ids_in_db.sort(key=sort_critera)
            packages = []
            package_ids = package_ids_in_db[start:start + PACKAGES_PER_PAGE]
            for package_id in package_ids:
                package = {
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
            package_namespace.abort(400, e.__doc__, status="Bad request", statusCode="400")
        except ForbiddenError as e:
            package_namespace.abort(403, e.__doc__, status="Forbidden", statusCode="403")


@package_namespace.route("/<string:package_id>/")
class Package(Resource):

    @api_app.doc(responses={200: "OK", 400: "Bad request", 403: "Forbidden"})
    def post(self, package_id):
        token = request.cookies.get("token")
        courier_id = request.cookies.get("courier_id")
        locker_id = request.cookies.get("locker_id")

        try:
            if token is None or courier_id is None or locker_id is None:
                raise BadRequestError
            if token is None or db.exists(token) == 0 or db.hget(token, "locker_id") != locker_id or db.hget(token,
                                                                                                             "courier_id") != courier_id:
                raise ForbiddenError
            locker_db = locker_id + "_packages"
            app.logger.debug(locker_db)
            db.smembers(locker_db)
            if package_id is None or package_id not in db.hkeys("packages") or package_id not in db.smembers(
                    locker_db) or db.hget(package_id, "status") != "LOCKER":
                raise BadRequestError

            courier_db = "packages_" + courier_id
            db.srem(locker_db, package_id)
            db.sadd(courier_db, package_id)
            db.hset(package_id, "status", "COURIER_L")
            return make_response({"status": "OK", "statusCode": "200"}, 200)

        except ForbiddenError as e:
            package_namespace.abort(403, e.__doc__, status="Forbidden", statusCode="403")
        except BadRequestError as e:
            package_namespace.abort(400, e.__doc__, status="Bad request", statusCode="400")
