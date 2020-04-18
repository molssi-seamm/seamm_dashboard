#!/usr/bin/env python
import configargparse
from app import create_app, setup_logging

import logging
import os
import time

from make_datastore import create_datastore


if __name__ == "__main__":
    # Argument/config parsing
    parser = configargparse.ArgParser(
        auto_env_var_prefix='',
        default_config_files=[
            '/etc/seamm/seamm.ini',
            '~/.seamm/seamm.ini',
        ]
    )
    parser.add_argument(
        '--seamm-configfile',
        is_config_file=True,
        default=None,
        help='a configuration file to override others'
    )

    # Options for the dashboard
    parser.add_argument(
        "--log-level",
        default='INFO',
        choices=[
            'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'
        ],
        type=str.upper,
        help="the logging level for the dashboard"
    )
    parser.add_argument(
        "--console-log-level",
        default='INFO',
        choices=[
            'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'
        ],
        type=str.upper,
        help="the logging level for the dashboard console"
    )
    parser.add_argument(
        '--mode',
        choices=['production', 'development', 'testing'],
        type=str.lower,
        default='production',
        help='the mode to run in'
    )
    parser.add_argument(
        "--datastore",
        dest="datastore",
        default='.',
        action="store",
        env_var='SEAMM_DATASTORE',
        help="The datastore (directory)."
    )
    parser.add_argument(
        "--database",
        dest="database",
        default='seamm.db',
        action="store",
        env_var='SEAMM_DATABASE',
        help="The database file."
    )
    parser.add_argument(
        '--initialize',
        action='store_true',
        help='initialize the database from scratch'
    )

    options, unknown = parser.parse_known_args()

    # Setup logging
    setup_logging(options)
    logger = logging.getLogger()

    # And proceed. First check if the database exists
    db_file = os.path.join(
        os.path.expanduser(options.datastore), options.database
    )
    initialize = not os.path.exists(db_file)
    
    if options.initialize and os.path.exists(db_file):
        os.remove(db_file)

    app = create_app(options)

    if initialize or options.initialize:
        logger.info('Initializing the database ({})'.format(db_file))
        t0 = time.perf_counter()
        with app.app_context():        
            n_projects, n_jobs = create_datastore(
                os.path.join(options.datastore, 'projects')
            )
        t1 = time.perf_counter()
        logger.info('Imported {} jobs in {} projects in {:.2f} s.'
                    .format(n_jobs, n_projects, t1 - t0))

    app.run(debug=False)  # , use_reloader=False)
