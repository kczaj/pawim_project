import datetime
import hashlib
import json
import os
import uuid

import redis
from werkzeug.datastructures import FileStorage
from errors import BadRequestError, NotFoundError, ForbiddenError
from flask import Flask, request, make_response, jsonify, send_file, redirect
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_restplus import Api, Resource
from package import Person, Address, Package

app = Flask(__name__, static_url_path="")
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)
cors = CORS(app)

app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config["JWT_SECRET_KEY"] = os.environ.get("LOGIN_JWT_SECRET")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 300
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = {'png', 'jpg'}

FILES_PATH = "/thunder_delivery/files/"
PACKAGES_PER_PAGE = 5

jwt = JWTManager(app)

api_app = Api(app=app, version="1.0", title="ThunderDeliveryDB API",
              description="Description of API for ThunderDeliveryDB App", default_mediatype="multipart/form-data")

package_namespace = api_app.namespace("packages", description="Packages API")
pdf_namespace = api_app.namespace("pdf", description="PDF API")


def clear_package_db():
    ids = db.hgetall("packages")
    for package in ids:
        db.delete(package)
    db.delete("packages_Andrzej")
    db.delete("packages")


# clear_package_db()

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


@package_namespace.route("/")
class Packages(Resource):

    @api_app.doc(responses={200: "OK", 401: "Unauthorized"})
    @jwt_required
    @cross_origin(origins=["https://localhost:8080"], supports_credentials=True)
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


def sort_critera(e):
    return db.hget(e, "created")


@package_namespace.route("/<int:start>/")
class PackagesPaginated(Resource):

    @api_app.doc(responses={200: "OK", 401: "Unauthorized", 400: "Bad request"})
    @jwt_required
    @cross_origin(origins=["https://localhost:8080"], supports_credentials=True)
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
                    "created": db.hget("packages", package_id),
                    "status": db.hget(package_id, "status"),
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


@package_namespace.route("/add/")
class AddPackage(Resource):
    post_parser = api_app.parser()
    post_parser.add_argument('sender_name', location='form', type='string', required=True)
    post_parser.add_argument('sender_surname', location='form', type='string', required=True)
    post_parser.add_argument('sender_street', location='form', type='string', required=True)
    post_parser.add_argument('sender_number', location='form', type='string', required=True)
    post_parser.add_argument('sender_code', location='form', type='string', required=True)
    post_parser.add_argument('sender_phone', location='form', type='string', required=True)
    post_parser.add_argument('receiver_name', location='form', type='string', required=True)
    post_parser.add_argument('receiver_surname', location='form', type='string', required=True)
    post_parser.add_argument('receiver_street', location='form', type='string', required=True)
    post_parser.add_argument('receiver_number', location='form', type='string', required=True)
    post_parser.add_argument('receiver_code', location='form', type='string', required=True)
    post_parser.add_argument('receiver_phone', location='form', type='string', required=True)
    post_parser.add_argument('photo', location='files', type='FileStorage', required=True)

    @api_app.doc(responses={201: "Created", 401: "Unauthorized", 400: "Bad request"})
    @jwt_required
    @cross_origin(origins=["https://localhost:8080"], supports_credentials=True)
    @api_app.expect(post_parser, validate=True)
    def post(self):
        try:
            if not os.path.exists(FILES_PATH):
                os.mkdir(FILES_PATH)

            sender_name = request.form.get("sender_name")
            sender_surname = request.form.get("sender_surname")
            sender_street = request.form.get("sender_street")
            sender_number = request.form.get("sender_number")
            sender_code = request.form.get("sender_code")
            sender_phone = request.form.get("sender_phone")
            receiver_name = request.form.get("receiver_name")
            receiver_surname = request.form.get("receiver_surname")
            receiver_street = request.form.get("receiver_street")
            receiver_number = request.form.get("receiver_number")
            receiver_code = request.form.get("receiver_code")
            receiver_phone = request.form.get("receiver_phone")
            photo = request.files["photo"] if request.files["photo"] is not None else "None"

            if sender_name is not None and sender_surname is not None and sender_street is not None and sender_number is not None and sender_code is not None and sender_phone is not None and receiver_name is not None and receiver_surname is not None and receiver_street is not None and receiver_number is not None and receiver_code is not None and receiver_phone is not None:
                username = str(get_jwt_identity())
                if check_fields(sender_name, sender_surname, sender_street, sender_number, sender_code, sender_phone,
                                receiver_name, receiver_surname,
                                receiver_street, receiver_number, receiver_code, receiver_phone, photo):
                    ids = db.hgetall("packages")
                    package_id = str(make_id(ids))
                    date = datetime.datetime.now()
                    db.hset("packages", package_id, date.__str__())
                    app.logger.debug(package_id)

                    name = "packages_" + username
                    db.sadd(name, package_id)

                    ext = photo.filename.split(".")[1]
                    file_name = package_id + '.' + ext
                    photo_path = save_file(photo, file_name)

                    db.hset(package_id, "sender_name", sender_name.encode("utf-8"))
                    db.hset(package_id, "sender_surname", sender_surname.encode("utf-8"))
                    db.hset(package_id, "sender_street", sender_street.encode("utf-8"))
                    db.hset(package_id, "sender_number", sender_number.encode("utf-8"))
                    db.hset(package_id, "sender_code", sender_code.encode("utf-8"))
                    db.hset(package_id, "sender_phone", sender_phone.encode("utf-8"))
                    db.hset(package_id, "receiver_name", receiver_name.encode("utf-8"))
                    db.hset(package_id, "receiver_surname", receiver_surname.encode("utf-8"))
                    db.hset(package_id, "receiver_street", receiver_street.encode("utf-8"))
                    db.hset(package_id, "receiver_number", receiver_number.encode("utf-8"))
                    db.hset(package_id, "receiver_code", receiver_code.encode("utf-8"))
                    db.hset(package_id, "receiver_phone", receiver_phone.encode("utf-8"))
                    db.hset(package_id, "status", "NEW")
                    db.hset(package_id, "photo", photo_path)
                    db.hset(package_id, "created", date.__str__())
                    db.hset(package_id, "path", "")
                    app.logger.debug(db.hget(package_id, "photo"))

                    response = make_response({
                        "message": "Created.",
                        "error": 201
                    }, 201)
                    return response
                else:
                    raise BadRequestError
            else:
                raise BadRequestError
        except BadRequestError as e:
            package_namespace.abort(400, e.__doc__, status="Bad request.", statusCode="400")


@pdf_namespace.route("/<string:package_id>")
class DownloadPDF(Resource):

    @api_app.doc(responses={201: "Created", 401: "Unauthorized", 400: "Bad request"})
    @jwt_required
    @cross_origin(origins=["https://localhost:8080"], supports_credentials=True)
    def get(self, package_id):
        try:
            if not os.path.exists(FILES_PATH):
                os.mkdir(FILES_PATH)

            name = "packages_" + str(get_jwt_identity())
            package_list = db.hgetall("packages")
            user_packages = db.smembers(name)

            if package_id in package_list and package_id in user_packages:
                sender_address = Address(db.hget(package_id, "sender_street"), db.hget(package_id, "sender_number"),
                                         db.hget(package_id, "sender_code"))
                sender = Person(db.hget(package_id, "sender_name"), db.hget(package_id, "sender_surname"),
                                sender_address,
                                db.hget(package_id, "sender_phone"))
                receiver_address = Address(db.hget(package_id, "receiver_street"),
                                           db.hget(package_id, "receiver_number"),
                                           db.hget(package_id, "receiver_code"))
                receiver = Person(db.hget(package_id, "receiver_name"), db.hget(package_id, "receiver_surname"),
                                  receiver_address, db.hget(package_id, "receiver_phone"))
                package = Package(sender, receiver, db.hget(package_id, "created"), package_id,
                                  db.hget(package_id, "photo"))

                path = db.hget(package_id, "path")
                filename = package_id + ".pdf"

                if path != "" and os.path.exists(path):
                    try:
                        return make_response(send_file(path, attachment_filename=filename, as_attachment=True), 200)
                    except Exception as c:
                        app.logger.debug(c)
                else:
                    fullname = package.generate_and_save(FILES_PATH)
                    db.hset(package_id, "path", fullname)
                    return make_response(send_file(fullname, attachment_filename=filename, as_attachment=True), 201)
            else:
                raise NotFoundError
        except NotFoundError as e:
            pdf_namespace.abort(404, e.__doc__, status="Package not found", statusCode="404")

    @api_app.doc(responses={201: "Deleted", 401: "Unauthorized", 403: "Forbidden"})
    @jwt_required
    @cross_origin(origins=["https://localhost:8080"], supports_credentials=True)
    def delete(self, package_id):
        try:
            name = "packages_" + str(get_jwt_identity())
            package_list = db.hgetall("packages")
            user_packages = db.smembers(name)

            if db.hget(package_id, "status") != "NEW":
                raise ForbiddenError

            if package_id in package_list and package_id in user_packages:
                status = db.hget(package_id, "status")
                if status == "NEW":
                    pdf_file = db.hget(package_id, "path")
                    photo_path = db.hget(package_id, "photo")
                    db.delete(package_id)
                    db.hdel("packages", package_id)
                    db.srem(name, package_id)
                    if pdf_file != "" and os.path.exists(pdf_file):
                        os.remove(pdf_file)
                    if photo_path != "" and os.path.exists(photo_path):
                        os.remove(photo_path)
                    return make_response({"status": "Deleted", "statusCode": "200"}, 200)
                else:
                    raise ForbiddenError
            else:
                raise NotFoundError
        except NotFoundError as e:
            pdf_namespace.abort(404, e.__doc__, status="Package not found", statusCode="404")
        except ForbiddenError as e:
            pdf_namespace.abort(403, e.__doc__, status="Forbidden action", statusCode="403")

    @api_app.doc(responses={201: "Deleted", 401: "Unauthorized"})
    @jwt_required
    @cross_origin(origins=["*"], supports_credentials=True)
    def options(self):
        return make_response({"status": "OK", "statusCode": "200"}, 200)


def make_id(ids):
    while True:
        package_id = uuid.uuid4().__str__()
        if package_id not in ids and db.exists(package_id) == 0:
            return package_id


def check_fields(sender_name, sender_surname, sender_street, sender_number, sender_code, sender_phone, receiver_name,
                 receiver_surname, receiver_street, receiver_number, receiver_code, receiver_phone, photo):
    return True


def save_file(photo, file_name):
    if len(photo.filename) > 0:
        path_to_file = os.path.join(FILES_PATH, file_name)
        photo.save(path_to_file)
        return path_to_file
    else:
        return ""


@app.errorhandler(400)
def page_not_found(error):
    app.logger.error("BAD REQUEST")
    return redirect("/")


@app.errorhandler(401)
def page_unauthorized(error):
    app.logger.error("UNAUTHORIZED")
    return redirect(api_app.base_url + "/")


@app.errorhandler(403)
def page_not_found(error):
    app.logger.error("FORBIDDEN")
    return redirect(api_app.base_url + "/")


@app.errorhandler(404)
def page_not_found(error):
    app.logger.error("NOT FOUND")
    return redirect(api_app.base_url + "/")


@app.errorhandler(500)
def page_not_found(error):
    app.logger.error("INTERNAL SERVER ERROR")
    return redirect(api_app.base_url + "/")
