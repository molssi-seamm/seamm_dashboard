import argparse
from pathlib import Path
import sys

import seamm_util

parser = seamm_util.seamm_parser()

# Options for the dashboard
parser.add_argument_group(
    "SEAMM",
    "dashboard options",
    "The options for the dashboard",
)

parser.add_argument(
    "SEAMM",
    "--initialize",
    group="dashboard options",
    action="store_true",
    help="initialize, or reinitialize, from the job files",
)
parser.add_argument(
    "SEAMM",
    "--no-check",
    group="dashboard options",
    action="store_true",
    help="do not check that jobs are in the database",
)

parser.add_argument(
    "SEAMM",
    "--console-log-level",
    group="dashboard options",
    default="INFO",
    choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"],
    type=str.upper,
    help="the logging level for the dashboard console",
)

parser.add_argument(
    "SEAMM",
    "--log_dir",
    group="dashboard options",
    default="${root}/logs",
    action="store",
    help="The directory for logging",
)

# The rest of the options are for Flask, SQLAlchemy, Bootstrap, etc.
# and will be added to the Flask configuration.

# Flask options
parser.add_argument_group(
    "SEAMM",
    "flask options",
    "The options for Flask",
)

parser.add_argument(
    "SEAMM",
    "--env",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "What environment the app is running in. Flask and extensions may "
        "enable behaviors based on the environment, such as enabling debug "
        "mode. The env attribute maps to this config key. This is set by the "
        "FLASK_ENV environment variable and may not behave as expected if set "
        "in code."
        "\n"
        "Do not enable development when deploying in production."
        "\n"
        "Default: production"
    ),
)

parser.add_argument(
    "SEAMM",
    "--debug",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Whether debug mode is enabled. When using flask run to start the "
        "development server, an interactive debugger will be shown for "
        "unhandled exceptions, and the server will be reloaded when code "
        "changes. The debug attribute maps to this config key. This is "
        "enabled when ENV is 'development' and is overridden by the "
        "FLASK_DEBUG environment variable. It may not behave as expected if "
        "set in code."
        "\n"
        "Do not enable debug mode when deploying in production."
        "\n"
        "Default: True if ENV is 'development', or False otherwise."
    ),
)

parser.add_argument(
    "SEAMM",
    "--testing",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Enable testing mode. Exceptions are propagated rather than handled "
        "by the the app’s error handlers. Extensions may also change their "
        "behavior to facilitate easier testing. You should enable this in "
        "your own tests."
        "\n"
        "Default: False"
    ),
)

parser.add_argument(
    "SEAMM",
    "--propagate-exceptions",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Exceptions are re-raised rather than being handled by the app’s "
        "error handlers. If not set, this is implicitly true if TESTING or "
        "DEBUG is enabled."
        "\n"
        "Default = None"
    ),
)

parser.add_argument(
    "SEAMM",
    "--preserve-context-on-exception",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Don't pop the request context when an exception occurs. If not set, "
        "this is true if DEBUG is true. This allows debuggers to introspect "
        "the request data on errors, and should normally not need to be set "
        "directly."
        "\n"
        "Default = None"
    ),
)

parser.add_argument(
    "SEAMM",
    "--trap-http-exceptions",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "If there is no handler for an HTTPException-type exception, re-raise "
        "it to be handled by the interactive debugger instead of returning it "
        "as a simple error response."
        "\n"
        "Default = False"
    ),
)

parser.add_argument(
    "SEAMM",
    "--trap-bad-request-errors",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Trying to access a key that doesn’t exist from request dicts like "
        "args and form will return a 400 Bad Request error page. Enable this "
        "to treat the error as an unhandled exception instead so that you get "
        "the interactive debugger. This is a more specific version of "
        "TRAP_HTTP_EXCEPTIONS. If unset, it is enabled in debug mode."
        "\n"
        "Default = None"
    ),
)

parser.add_argument(
    "SEAMM",
    "--secret-key",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "A secret key that will be used for securely signing the session "
        "cookie and can be used for any other security related needs by "
        "extensions or your application. It should be a long random string of "
        "bytes, although unicode is accepted too. For example, copy the "
        "output of this to your config:"
        "\n"
        "$ python -c 'import os; print(os.urandom(16))'"
        "b'_5#y2L\"F4Q8z\n\xec]/'"
        "\n"
        "Do not reveal the secret key when posting questions or committing "
        "code."
        "\n"
        "Default = None"
    ),
)

parser.add_argument(
    "SEAMM",
    "--jwt-secret-key",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        """
        A secret key for the JWT token.
        """
    ),
)

parser.add_argument(
    "SEAMM",
    "--session-cookie-name",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "The name of the session cookie. Can be changed in case you already "
        "have a cookie with the same name."
        "\n"
        "Default = session"
    ),
)

parser.add_argument(
    "SEAMM",
    "--session-cookie-domain",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "The domain match rule that the session cookie will be valid for. If "
        "not set, the cookie will be valid for all subdomains of SERVER_NAME. "
        "If False, the cookie’s domain will not be set."
        "\n"
        "Default = None"
    ),
)

parser.add_argument(
    "SEAMM",
    "--session-cookie-path",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "The path that the session cookie will be valid for. If not set, the "
        "cookie will be valid underneath APPLICATION_ROOT or / if that is not "
        "set."
        "\n"
        "Default = None"
    ),
)

parser.add_argument(
    "SEAMM",
    "--session-cookie-secure",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Browsers will only send cookies with requests over HTTPS if the "
        "cookie is marked “secure”. The application must be served over HTTPS "
        "for this to make sense."
        "\n"
        "Default = False"
    ),
)

parser.add_argument(
    "SEAMM",
    "--session-cookie-samesite",
    group="flask options",
    default="Lax",
    help=(
        "Restrict how cookies are sent with requests from external sites. Can "
        "be set to 'Lax' (recommended) or 'Strict'. See Set-Cookie options."
        "\n"
        "Default = 'Lax'"
    ),
)

parser.add_argument(
    "SEAMM",
    "--permanent-session-lifetime",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "If session.permanent is true, the cookie’s expiration will be set "
        "this number of seconds in the future. Can either be a "
        "datetime.timedelta or an int."
        "\n"
        "Flask’s default cookie implementation validates that the "
        "cryptographic signature is not older than this value."
        "\n"
        "Default: datetime.timedelta(days=31)"
    ),
)

parser.add_argument(
    "SEAMM",
    "--session-refresh-each-request",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Control whether the cookie is sent with every response when "
        "session.permanent is true. Sending the cookie every time (the "
        "default) can more reliably keep the session from expiring, but uses "
        "more bandwidth. Non-permanent sessions are not affected."
        "\n"
        "Default = True"
    ),
)

parser.add_argument(
    "SEAMM",
    "--use-x-sendfile",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "When serving files, set the X-Sendfile header instead of serving the "
        "data with Flask. Some web servers, such as Apache, recognize this "
        "and serve the data more efficiently. This only makes sense when "
        "using such a server."
        "\n"
        "Default = False"
    ),
)

parser.add_argument(
    "SEAMM",
    "--send-file-max-age-default",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "When serving files, set the cache control max age to this number of "
        "seconds. Can either be a datetime.timedelta or an int. Override this "
        "value on a per-file basis using get_send_file_max_age() on the "
        "application or blueprint."
        "\n"
        "Default: timedelta(hours=12) (43200 seconds)"
    ),
)

parser.add_argument(
    "SEAMM",
    "--server-name",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Inform the application what host and port it is bound to. Required "
        "for subdomain route matching support."
        "\n"
        "If set, will be used for the session cookie domain if "
        "SESSION_COOKIE_DOMAIN is not set. Modern web browsers will not allow "
        "setting cookies for domains without a dot. To use a domain locally, "
        "add any names that should route to the app to your hosts file."
        "\n"
        "127.0.0.1 localhost.dev"
        "If set, url_for can generate external URLs with only an application "
        "context instead of a request context."
        "\n"
        "Default: None"
    ),
)

parser.add_argument(
    "SEAMM",
    "--application-root",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Inform the application what path it is mounted under by the "
        "application / web server. This is used for generating URLs outside "
        "the context of a request (inside a request, the dispatcher is "
        "responsible for setting SCRIPT_NAME instead; see Application "
        "Dispatching for examples of dispatch configuration)."
        "\n"
        "Will be used for the session cookie path if SESSION_COOKIE_PATH is "
        "not set."
        "\n"
        "Default = '/'"
    ),
)

parser.add_argument(
    "SEAMM",
    "--preferred-url-scheme",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Use this scheme for generating external URLs when not in a request "
        "context."
        "\n"
        "default='http'"
    ),
)

parser.add_argument(
    "SEAMM",
    "--max-content-length",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Don't read more than this many bytes from the incoming request data. "
        "If not set and the request does not specify a CONTENT_LENGTH, no "
        "data will be read for security."
        "\n"
        "Default: None"
    ),
)

parser.add_argument(
    "SEAMM",
    "--json-as-ascii",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Serialize objects to ASCII-encoded JSON. If this is disabled, the "
        "JSON will be returned as a Unicode string, or encoded as UTF-8 by "
        "jsonify. This has security implications when rendering the JSON into "
        "JavaScript in templates, and should typically remain enabled."
        "\n"
        "default=True"
    ),
)

parser.add_argument(
    "SEAMM",
    "--json-sort-keys",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Sort the keys of JSON objects alphabetically. This is useful for "
        "caching because it ensures the data is serialized the same way no "
        "matter what Python’s hash seed is. While not recommended, you can "
        "disable this for a possible performance improvement at the cost of "
        "caching."
        "\n"
        "default=True"
    ),
)

parser.add_argument(
    "SEAMM",
    "--jsonify-prettyprint-regular",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "jsonify responses will be output with newlines, spaces, and "
        "indentation for easier reading by humans. Always enabled in debug "
        "mode."
        "\n"
        "default=False"
    ),
)

parser.add_argument(
    "SEAMM",
    "--jsonify-mimetype",
    group="flask options",
    default=argparse.SUPPRESS,
    help=("The mimetype of jsonify responses." "\n" "default='application/json'"),
)

parser.add_argument(
    "SEAMM",
    "--templates-auto-reload",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Reload templates when they are changed. If not set, it will be "
        "enabled in debug mode."
        "\n"
        "Default: None"
    ),
)

parser.add_argument(
    "SEAMM",
    "--explain-template-loading",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Log debugging information tracing how a template file was loaded. "
        "This can be useful to figure out why a template was not loaded or "
        "the wrong file appears to be loaded."
        "\n"
        "default=False"
    ),
)

parser.add_argument(
    "SEAMM",
    "--max-cookie-size",
    group="flask options",
    default=argparse.SUPPRESS,
    help=(
        "Warn if cookie headers are larger than this many bytes. Defaults to "
        "4093. Larger cookies may be silently ignored by browsers. Set to 0 "
        "to disable the warning."
        "\n"
        "default=4093"
    ),
)

# SQLAlchemy options
parser.add_argument_group(
    "SEAMM",
    "sqlalchemy options",
    "The SQLAlchemy options for the dashboard",
)

parser.add_argument(
    "SEAMM",
    "--sqlalchemy-database-uri",
    group="sqlalchemy options",
    default="",
    help=(
        "The database URI that should be used for the connection. Examples:"
        "\n"
        "sqlite:////tmp/test.db"
        "\n"
        "mysql://username:password@server/db"
    ),
)

parser.add_argument(
    "SEAMM",
    "--sqlalchemy-binds",
    group="sqlalchemy options",
    default=argparse.SUPPRESS,
    help=(
        "A dictionary that maps bind keys to SQLAlchemy connection URIs. For "
        "more information about binds see Multiple Databases with Binds."
    ),
)

parser.add_argument(
    "SEAMM",
    "--sqlalchemy-echo",
    group="sqlalchemy options",
    default=argparse.SUPPRESS,
    help=(
        "If set to True SQLAlchemy will log all the statements issued to "
        "stderr which can be useful for debugging."
    ),
)

parser.add_argument(
    "SEAMM",
    "--sqlalchemy-record-queries",
    group="sqlalchemy options",
    default=argparse.SUPPRESS,
    help=(
        "Can be used to explicitly disable or enable query recording. Query "
        "recording automatically happens in debug or testing mode. See "
        "get_debug_queries() for more information."
    ),
)

parser.add_argument(
    "SEAMM",
    "--sqlalchemy-track-modifications",
    group="sqlalchemy options",
    default=False,
    help=(
        "If set to True, Flask-SQLAlchemy will track modifications of objects "
        "and emit signals. The default is None, which enables tracking but "
        "issues a warning that it will be disabled by default in the future. "
        "This requires extra memory and should be disabled if not needed."
        "\n"
        "default=False"
    ),
)

parser.add_argument(
    "SEAMM",
    "--sqlalchemy-engine-options",
    group="sqlalchemy options",
    default=argparse.SUPPRESS,
    help=(
        "A dictionary of keyword args to send to create_engine(). See also "
        "engine_options to SQLAlchemy."
    ),
)

# Bootstrap options
parser.add_argument_group(
    "SEAMM",
    "bootstrap options",
    "The Bootstrap options for the dashboard",
)

parser.add_argument(
    "SEAMM",
    "--bootstrap-use-minified",
    group="bootstrap options",
    default=argparse.SUPPRESS,
    help=(
        "Whether or not to use the minified versions of the css/js files."
        "\n"
        "default=True"
    ),
)

parser.add_argument(
    "SEAMM",
    "--bootstrap-serve-local",
    group="bootstrap options",
    default=argparse.SUPPRESS,
    help=(
        "If True, Bootstrap resources will be served from the local app "
        "instance every time. See CDN support for details."
        "\n"
        "default=False"
    ),
)

parser.add_argument(
    "SEAMM",
    "--bootstrap-local-subdomain",
    group="bootstrap options",
    default=argparse.SUPPRESS,
    help=(
        "Passes a subdomain parameter to the generated Blueprint. Useful "
        "when serving assets locally from a different subdomain."
    ),
)

parser.add_argument(
    "SEAMM",
    "--bootstrap-cdn-force-ssl",
    group="bootstrap options",
    default=argparse.SUPPRESS,
    help=(
        "If a CDN resource url starts with //, prepend 'https:' to it."
        "\n"
        "default=True"
    ),
)

parser.add_argument(
    "SEAMM",
    "--bootstrap-querystring-revving",
    group="bootstrap options",
    default=argparse.SUPPRESS,
    help=(
        "If True, will append a querystring with the current version to all "
        "static resources served locally. This ensures that upon upgrading "
        "Flask-Bootstrap, these resources are refreshed."
        "\n"
        "default=True"
    ),
)

# Mail arguments - for flask mail
# https://pythonhosted.org/Flask-Mail/
parser.add_argument_group(
    "SEAMM",
    "mail options",
    "The FlaskMail options for the dashboard",
)

parser.add_argument(
    "SEAMM",
    "--mail-server",
    group="mail options",
    default=argparse.SUPPRESS,
    help="default=localhost",
)

parser.add_argument(
    "SEAMM",
    "--mail-port",
    group="mail options",
    default=argparse.SUPPRESS,
    help=("" "default=25"),
)

parser.add_argument(
    "SEAMM",
    "--mail-use-TLS",
    group="mail options",
    default=argparse.SUPPRESS,
    help=("" "default=False"),
)

parser.add_argument(
    "SEAMM",
    "--mail-use-SSL",
    group="mail options",
    default=argparse.SUPPRESS,
    help=("" "default=False"),
)

parser.add_argument(
    "SEAMM",
    "--mail-debug",
    group="mail options",
    default=argparse.SUPPRESS,
    help=("", "default=app.debug"),
)

parser.add_argument(
    "SEAMM",
    "--mail-username",
    group="mail options",
    default=argparse.SUPPRESS,
    help=("" "default=None"),
)

parser.add_argument(
    "SEAMM",
    "--mail-password",
    group="mail options",
    default=argparse.SUPPRESS,
    help=("" "default=None"),
)

parser.add_argument(
    "SEAMM",
    "--mail-default-sender",
    group="mail options",
    default=argparse.SUPPRESS,
    help=("" "default=None"),
)

parser.add_argument(
    "SEAMM",
    "--mail-max-emails",
    group="mail options",
    default=argparse.SUPPRESS,
    help=("" "default=None"),
)

parser.add_argument(
    "SEAMM",
    "--mail-suppress-send",
    group="mail options",
    default=argparse.SUPPRESS,
    help=("" "default=app.testing"),
)

parser.add_argument(
    "SEAMM",
    "--mail-ascii-attachments",
    group="mail options",
    default=argparse.SUPPRESS,
    help=("" "default=False"),
)

parser.add_argument(
    "SEAMM",
    "--mail-subject-prefix",
    group="mail options",
    default=argparse.SUPPRESS,
    help=(""),
)

parser.add_argument(
    "SEAMM", "--mail-sender", group="mail options", default=argparse.SUPPRESS, help=("")
)

# And handle the command-line arguments and ini file options.
# Working around pytest :-(
if "pytest" in sys.argv[0]:
    parser.parse_args([])
else:
    parser.parse_args()
options = parser.get_options("SEAMM")

# Fix the database uri
if "sqlalchemy_database_uri" in options and options["sqlalchemy_database_uri"] == "":
    path = Path(options["datastore"]).expanduser().resolve() / "seamm.db"
    options["sqlalchemy_database_uri"] = f"sqlite:///{str(path)}"

if __name__ == "__main__":
    import pprint

    # options, unknown = parser.parse_known_args()

    pprint.pprint(vars(options))
