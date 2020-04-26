import configargparse

parser = configargparse.get_argument_parser(
    name='dashboard',
    auto_env_var_prefix='',
    default_config_files=[
        '/etc/seamm/seamm-dashboard.ini', '/etc/seamm/seamm.ini',
        '~/.seamm/seamm-dashboard.ini', '~/.seamm/seamm.ini'
    ]
)

parser.add_argument(
    '--dashboard-configfile',
    is_config_file=True,
    default=None,
    help='a configuration file to override others'
)

# Where the datastore is located (from seamm.ini)
parser.add_argument(
    '--datastore',
    dest='datastore',
    default='.',
    action='store',
    env_var='SEAMM_DATASTORE',
    help='The datastore (directory).'
)
parser.add_argument(
    '--initialize',
    action='store_true',
    help='initialize, or reinitialize, from the job files'
)
parser.add_argument(
    '--no-check',
    action='store_true',
    help='do not check that jobs are in the database'
)

# Options for the dashboard
parser.add_argument(
    '--log-level',
    default='INFO',
    choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'],
    type=str.upper,
    help='the logging level for the dashboard'
)

parser.add_argument(
    '--console-log-level',
    default='INFO',
    choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'],
    type=str.upper,
    help='the logging level for the dashboard console'
)

parser.add_argument(
    '--log_dir',
    default='%datastore%/logs',
    action='store',
    env_var='SEAMM_LOGDIR',
    help='The directory for logging'
)

# The rest of the options are for Flask, SQLAlchemy, Bootstrap, etc.
# and will be added to the Flaks configuration.

# Flask options
parser.add_argument(
    '--env',
    default=configargparse.SUPPRESS,
    env_var='FLASK_ENV',
    help=(
        'What environment the app is running in. Flask and extensions may '
        'enable behaviors based on the environment, such as enabling debug '
        'mode. The env attribute maps to this config key. This is set by the '
        'FLASK_ENV environment variable and may not behave as expected if set '
        'in code.'
        '\n'
        'Do not enable development when deploying in production.'
        '\n'
        'Default: production'
    )
)

parser.add_argument(
    '--debug',
    default=configargparse.SUPPRESS,
    env_var='FLASK_DEBUG',
    help=(
        'Whether debug mode is enabled. When using flask run to start the '
        'development server, an interactive debugger will be shown for '
        'unhandled exceptions, and the server will be reloaded when code '
        'changes. The debug attribute maps to this config key. This is '
        "enabled when ENV is 'development' and is overridden by the "
        'FLASK_DEBUG environment variable. It may not behave as expected if '
        'set in code.'
        '\n'
        'Do not enable debug mode when deploying in production.'
        '\n'
        "Default: True if ENV is 'development', or False otherwise."
    )
)

parser.add_argument(
    '--testing',
    default=configargparse.SUPPRESS,
    help=(
        'Enable testing mode. Exceptions are propagated rather than handled '
        'by the the app’s error handlers. Extensions may also change their '
        'behavior to facilitate easier testing. You should enable this in '
        'your own tests.'
        '\n'
        'Default: False'
    )
)

parser.add_argument(
    '--propagate-exceptions',
    default=configargparse.SUPPRESS,
    help=(
        'Exceptions are re-raised rather than being handled by the app’s '
        'error handlers. If not set, this is implicitly true if TESTING or '
        'DEBUG is enabled.'
        '\n'
        'Default = None'
    )
)

parser.add_argument(
    '--preserve-context-on-exception',
    default=configargparse.SUPPRESS,
    help=(
        "Don't pop the request context when an exception occurs. If not set, "
        'this is true if DEBUG is true. This allows debuggers to introspect '
        'the request data on errors, and should normally not need to be set '
        'directly.'
        '\n'
        'Default = None'
    )
)

parser.add_argument(
    '--trap-http-exceptions',
    default=configargparse.SUPPRESS,
    help=(
        'If there is no handler for an HTTPException-type exception, re-raise '
        'it to be handled by the interactive debugger instead of returning it '
        'as a simple error response.'
        '\n'
        'Default = False'
    )
)

parser.add_argument(
    '--trap-bad-request-errors',
    default=configargparse.SUPPRESS,
    help=(
        'Trying to access a key that doesn’t exist from request dicts like '
        'args and form will return a 400 Bad Request error page. Enable this '
        'to treat the error as an unhandled exception instead so that you get '
        'the interactive debugger. This is a more specific version of '
        'TRAP_HTTP_EXCEPTIONS. If unset, it is enabled in debug mode.'
        '\n'
        'Default = None'
    )
)

parser.add_argument(
    '--secret-key',
    default=configargparse.SUPPRESS,
    help=(
        'A secret key that will be used for securely signing the session '
        'cookie and can be used for any other security related needs by '
        'extensions or your application. It should be a long random string of '
        'bytes, although unicode is accepted too. For example, copy the '
        'output of this to your config:'
        '\n'
        "$ python -c 'import os; print(os.urandom(16))'"
        "b'_5#y2L\"F4Q8z\n\xec]/'"
        '\n'
        'Do not reveal the secret key when posting questions or committing '
        'code.'
        '\n'
        'Default = None'
    )
)

parser.add_argument(
    '--session-cookie-name',
    default=configargparse.SUPPRESS,
    help=(
        'The name of the session cookie. Can be changed in case you already '
        'have a cookie with the same name.'
        '\n'
        'Default = session'
    )
)

parser.add_argument(
    '--session-cookie-domain',
    default=configargparse.SUPPRESS,
    help=(
        'The domain match rule that the session cookie will be valid for. If '
        'not set, the cookie will be valid for all subdomains of SERVER_NAME. '
        'If False, the cookie’s domain will not be set.'
        '\n'
        'Default = None'
    )
)

parser.add_argument(
    '--session-cookie-path',
    default=configargparse.SUPPRESS,
    help=(
        'The path that the session cookie will be valid for. If not set, the '
        'cookie will be valid underneath APPLICATION_ROOT or / if that is not '
        'set.'
        '\n'
        'Default = None'
    )
)

parser.add_argument(
    '--session-cookie-secure',
    default=configargparse.SUPPRESS,
    help=(
        'Browsers will only send cookies with requests over HTTPS if the '
        'cookie is marked “secure”. The application must be served over HTTPS '
        'for this to make sense.'
        '\n'
        'Default = False'
    )
)

parser.add_argument(
    '--session-cookie-samesite',
    default='Lax',
    help=(
        'Restrict how cookies are sent with requests from external sites. Can '
        "be set to 'Lax' (recommended) or 'Strict'. See Set-Cookie options."
        '\n'
        "Default = 'Lax'"
    )
)

parser.add_argument(
    '--permanent-session-lifetime',
    default=configargparse.SUPPRESS,
    help=(
        'If session.permanent is true, the cookie’s expiration will be set '
        'this number of seconds in the future. Can either be a '
        'datetime.timedelta or an int.'
        '\n'
        'Flask’s default cookie implementation validates that the '
        'cryptographic signature is not older than this value.'
        '\n'
        'Default: datetime.timedelta(days=31)'
    )
)

parser.add_argument(
    '--session-refresh-each-request',
    default=configargparse.SUPPRESS,
    help=(
        'Control whether the cookie is sent with every response when '
        'session.permanent is true. Sending the cookie every time (the '
        'default) can more reliably keep the session from expiring, but uses '
        'more bandwidth. Non-permanent sessions are not affected.'
        '\n'
        'Default = True'
    )
)

parser.add_argument(
    '--use-x-sendfile',
    default=configargparse.SUPPRESS,
    help=(
        'When serving files, set the X-Sendfile header instead of serving the '
        'data with Flask. Some web servers, such as Apache, recognize this '
        'and serve the data more efficiently. This only makes sense when '
        'using such a server.'
        '\n'
        'Default = False'
    )
)

parser.add_argument(
    '--send-file-max-age-default',
    default=configargparse.SUPPRESS,
    help=(
        'When serving files, set the cache control max age to this number of '
        'seconds. Can either be a datetime.timedelta or an int. Override this '
        'value on a per-file basis using get_send_file_max_age() on the '
        'application or blueprint.'
        '\n'
        'Default: timedelta(hours=12) (43200 seconds)'
    )
)

parser.add_argument(
    '--server-name',
    default=configargparse.SUPPRESS,
    help=(
        'Inform the application what host and port it is bound to. Required '
        'for subdomain route matching support.'
        '\n'
        'If set, will be used for the session cookie domain if '
        'SESSION_COOKIE_DOMAIN is not set. Modern web browsers will not allow '
        'setting cookies for domains without a dot. To use a domain locally, '
        'add any names that should route to the app to your hosts file.'
        '\n'
        '127.0.0.1 localhost.dev'
        'If set, url_for can generate external URLs with only an application '
        'context instead of a request context.'
        '\n'
        'Default: None'
    )
)

parser.add_argument(
    '--application-root',
    default=configargparse.SUPPRESS,
    help=(
        'Inform the application what path it is mounted under by the '
        'application / web server. This is used for generating URLs outside '
        'the context of a request (inside a request, the dispatcher is '
        'responsible for setting SCRIPT_NAME instead; see Application '
        'Dispatching for examples of dispatch configuration).'
        '\n'
        'Will be used for the session cookie path if SESSION_COOKIE_PATH is '
        'not set.'
        '\n'
        "Default = '/'"
    )
)

parser.add_argument(
    '--preferred-url-scheme',
    default=configargparse.SUPPRESS,
    help=(
        'Use this scheme for generating external URLs when not in a request '
        'context.'
        '\n'
        "default='http'"
    )
)

parser.add_argument(
    '--max-content-length',
    default=configargparse.SUPPRESS,
    help=(
        "Don't read more than this many bytes from the incoming request data. "
        'If not set and the request does not specify a CONTENT_LENGTH, no '
        'data will be read for security.'
        '\n'
        'Default: None'
    )
)

parser.add_argument(
    '--json-as-ascii',
    default=configargparse.SUPPRESS,
    help=(
        'Serialize objects to ASCII-encoded JSON. If this is disabled, the '
        'JSON will be returned as a Unicode string, or encoded as UTF-8 by '
        'jsonify. This has security implications when rendering the JSON into '
        'JavaScript in templates, and should typically remain enabled.'
        '\n'
        'default=True'
    )
)

parser.add_argument(
    '--json-sort-keys',
    default=configargparse.SUPPRESS,
    help=(
        'Sort the keys of JSON objects alphabetically. This is useful for '
        'caching because it ensures the data is serialized the same way no '
        'matter what Python’s hash seed is. While not recommended, you can '
        'disable this for a possible performance improvement at the cost of '
        'caching.'
        '\n'
        'default=True'
    )
)

parser.add_argument(
    '--jsonify-prettyprint-regular',
    default=configargparse.SUPPRESS,
    help=(
        'jsonify responses will be output with newlines, spaces, and '
        'indentation for easier reading by humans. Always enabled in debug '
        'mode.'
        '\n'
        'default=False'
    )
)

parser.add_argument(
    '--jsonify-mimetype',
    default=configargparse.SUPPRESS,
    help=(
        'The mimetype of jsonify responses.'
        '\n'
        "default='application/json'"
    )
)

parser.add_argument(
    '--templates-auto-reload',
    default=configargparse.SUPPRESS,
    help=(
        'Reload templates when they are changed. If not set, it will be '
        'enabled in debug mode.'
        '\n'
        'Default: None'
    )
)

parser.add_argument(
    '--explain-template-loading',
    default=configargparse.SUPPRESS,
    help=(
        'Log debugging information tracing how a template file was loaded. '
        'This can be useful to figure out why a template was not loaded or '
        'the wrong file appears to be loaded.'
        '\n'
        'default=False'
    )
)

parser.add_argument(
    '--max-cookie-size',
    default=configargparse.SUPPRESS,
    help=(
        'Warn if cookie headers are larger than this many bytes. Defaults to '
        '4093. Larger cookies may be silently ignored by browsers. Set to 0 '
        'to disable the warning.'
        '\n'
        'default=4093'
    )
)

parser.add_argument(
    '--sqlalchemy-database-uri',
    default='sqlite:///%datastore%/seamm.db',
    help=(
        'The database URI that should be used for the connection. Examples:'
        '\n'
        'sqlite:////tmp/test.db'
        '\n'
        'mysql://username:password@server/db'
    )
)

parser.add_argument(
    '--sqlalchemy-binds',
    default=configargparse.SUPPRESS,
    help=(
        'A dictionary that maps bind keys to SQLAlchemy connection URIs. For '
        'more information about binds see Multiple Databases with Binds.'
    )
)

parser.add_argument(
    '--sqlalchemy-echo',
    default=configargparse.SUPPRESS,
    help=(
        'If set to True SQLAlchemy will log all the statements issued to '
        'stderr which can be useful for debugging.'
    )
)

parser.add_argument(
    '--sqlalchemy-record-queries',
    default=configargparse.SUPPRESS,
    help=(
        'Can be used to explicitly disable or enable query recording. Query '
        'recording automatically happens in debug or testing mode. See '
        'get_debug_queries() for more information.'
    )
)

parser.add_argument(
    '--sqlalchemy-track-modifications',
    default=False,
    help=(
        'If set to True, Flask-SQLAlchemy will track modifications of objects '
        'and emit signals. The default is None, which enables tracking but '
        'issues a warning that it will be disabled by default in the future. '
        'This requires extra memory and should be disabled if not needed.'
        '\n'
        'default=False'
    )
)

parser.add_argument(
    '--sqlalchemy-engine-options',
    default=configargparse.SUPPRESS,
    help=(
        'A dictionary of keyword args to send to create_engine(). See also '
        'engine_options to SQLAlchemy.'
    )
)

parser.add_argument(
    '--bootstrap-use-minified',
    default=configargparse.SUPPRESS,
    help=(
        'Whether or not to use the minified versions of the css/js files.'
        '\n'
        'default=True'
    )
)

parser.add_argument(
    '--bootstrap-serve-local',
    default=configargparse.SUPPRESS,
    help=(
        'If True, Bootstrap resources will be served from the local app '
        'instance every time. See CDN support for details.'
        '\n'
        'default=False'
    )
)

parser.add_argument(
    '--bootstrap-local-subdomain',
    default=configargparse.SUPPRESS,
    help=(
        'Passes a subdomain parameter to the generated Blueprint. Useful '
        'when serving assets locally from a different subdomain.'
    )
)

parser.add_argument(
    '--bootstrap-cdn-force-ssl',
    default=configargparse.SUPPRESS,
    help=(
        "If a CDN resource url starts with //, prepend 'https:' to it."
        '\n'
        'default=True'
    )
)

parser.add_argument(
    '--bootstrap-querystring-revving',
    default=configargparse.SUPPRESS,
    help=(
        'If True, will append a querystring with the current version to all '
        'static resources served locally. This ensures that upon upgrading '
        'Flask-Bootstrap, these resources are refreshed.'
        '\n'
        'default=True'
    )
)

options, unknown_options = parser.parse_known_args()

if __name__ == "__main__":
    import pprint

    # options, unknown = parser.parse_known_args()

    pprint.pprint(vars(options))
