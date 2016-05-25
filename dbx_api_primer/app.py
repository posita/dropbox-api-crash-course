# -*-mode: python; encoding: utf-8; test-case-name: tests.test_app-*-

# ========================================================================
"""
  Copyright |(c)| 2017 `Dropbox, Inc.`_

  .. |(c)| unicode:: u+a9
  .. _`Dropbox, Inc.`: https://www.dropbox.com/

  Please see the accompanying ``LICENSE`` and ``CREDITS`` file(s) for
  rights and restrictions governing use of this software. All rights not
  expressly waived or licensed are reserved. If such a file did not
  accompany this software, then please contact the author before viewing
  or using this software in any capacity.
"""
# ========================================================================

from __future__ import (
    absolute_import, division, print_function, unicode_literals,
)
from builtins import *  # noqa: F401,F403; pylint: disable=redefined-builtin,unused-wildcard-import,useless-suppression,wildcard-import
from future.builtins.disabled import *  # noqa: F401,F403; pylint: disable=redefined-builtin,unused-wildcard-import,useless-suppression,wildcard-import

# ---- Imports -----------------------------------------------------------

from future.moves.urllib.parse import urljoin
from future.utils import bytes_to_native_str

import hashlib
import hmac
import os
import sqlite3

import dropbox
import flask

# Used for the tutorial
import datetime  # noqa: F401; pylint: disable=unused-import
import humanize  # noqa: F401; pylint: disable=unused-import

# ---- Constants ---------------------------------------------------------

__all__ = ()

_SESSION_USER_ID = 'user-id'
_SESSION_DBX_AUTH_STATE = 'dbx-auth-state'
_APP = flask.Flask(__name__)

# ---- Functions ---------------------------------------------------------

# ========================================================================
@_APP.route('/', methods=( 'GET', 'POST' ))
def route_():
    db = get_db()
    user_id = flask.session.get(_SESSION_USER_ID)
    user_dbx_acct_entry = None

    if user_id is not None:
        user_dbx_acct_entry = db_user_dbx_acct_select_one_by_user_id(db, user_id)

        if user_dbx_acct_entry is None:
            # They have a stale user ID, but we don't know why, so just
            # treat them as a new browser
            user_id = None
            flask.session.pop(_SESSION_USER_ID, None)

    if flask.request.method == 'GET':
        # This displays the main page, which changes based on whether
        # the session contains a valid user ID
        template_vars = {
            'title': _APP.config['SITE_TITLE'],
        }

        if user_dbx_acct_entry is not None:
            user_name = user_dbx_acct_entry[bytes_to_native_str(b'user_name')]
            user_email = user_dbx_acct_entry[bytes_to_native_str(b'user_email')]
            template_vars['user_name'] = user_name

            if user_email is not None:
                template_vars['user_email'] = user_email

            # TODO: Maybe we should do something fun here?

        return flask.render_template('settings.html', **template_vars)
    elif flask.request.method == 'POST':
        action = flask.request.form.get('action')

        if action == 'enable':
            # Start the auth flow
            return flask.redirect(flask.url_for('route_start'))
        elif action == 'disable':
            # We need to try to revoke all the tokens we have and clear
            # this session. See WARNING comment in ``route_finish``.
            if user_dbx_acct_entry is not None:
                dbx_acct_id = user_dbx_acct_entry[bytes_to_native_str(b'dbx_acct_id')]
                db_user_update_for_delete_by_dbx_acct_id(db, dbx_acct_id)

                for user_entry in db_user_select_all_deleted_by_dbx_acct_id(db, dbx_acct_id):
                    dbx_auth_token = user_entry[bytes_to_native_str(b'dbx_auth_token')]
                    dbx = dropbox.Dropbox(dbx_auth_token)

                    try:
                        dbx.auth_token_revoke()
                    except dropbox.exceptions.AuthError:
                        # Token is already revoked
                        _APP.logger.info('token "%s" already revoked', dbx_auth_token)

                    user_id = user_entry[bytes_to_native_str(b'user_id')]
                    db_user_delete(db, user_id)

                db.commit()
                flask.session.pop(_SESSION_USER_ID, None)

            return flask.redirect(flask.url_for('route_'))
        else:
            flask.abort(400)  # bad request

# ========================================================================
@_APP.route('/finish')
def route_finish():
    # This is basically modified from the example code at
    # <http://dropbox-sdk-python.readthedocs.io/en/master/moduledoc.html#dropbox.oauth.DropboxOAuth2Flow>
    auth_flow = _new_dbx_auth_flow(flask.session)

    try:
        auth_res = auth_flow.finish(flask.request.args)
    except dropbox.oauth.BadRequestException:
        flask.abort(400)
    except dropbox.oauth.BadStateException:
        # Start the auth flow again
        return flask.redirect(flask.url_for('route_start'))
    except dropbox.oauth.CsrfException:
        flask.abort(403)
    except dropbox.oauth.NotApprovedException:
        flask.abort(401)
    except dropbox.oauth.ProviderException as exc:
        _APP.logger.info('auth error: %s', exc)
        flask.abort(403)

    # Compare our saved random state with what comes back from Dropbox
    dbx_auth_state = flask.session.pop(_SESSION_DBX_AUTH_STATE, None)

    if dbx_auth_state is None \
            or auth_res.url_state != dbx_auth_state:
        _APP.logger.info('browser state (%s) does not equal returned state (%s)', dbx_auth_state, auth_res.url_state)
        flask.abort(403)

    # Brilliant! Now we can DO stuff!
    dbx_auth_token = auth_res.access_token
    dbx_acct_id = auth_res.account_id

    # TODO: Maybe now that we have an auth token, we can retrieve the
    # user's Dropbox account name and e-mail using the API?
    user_name = '<USE THE API TO RETRIEVE ME!>'
    user_email = None

    # Fake a secure-ish user ID and save the new user. See warning below.
    user_id_seed = bytes(dbx_acct_id, encoding='utf-8') + os.urandom(24)
    user_id = hashlib.sha256(user_id_seed).hexdigest()

    db = get_db()

    try:
        db_dbx_acct_insert(db, dbx_acct_id, user_name, user_email)
    except sqlite3.IntegrityError:
        # The user's account record is already there, so we update the
        # name and e-mail to the latest
        db_dbx_acct_update(db, dbx_acct_id, user_name, user_email)

    db_user_insert(db, user_id, dbx_acct_id, dbx_auth_token)
    db.commit()

    # WARNING: This is just to make our demo simpler. Don't ever use Flask
    # sessions this way if your want to be #WorthyOfTrust. See
    # <https://blog.miguelgrinberg.com/post/how-secure-is-the-flask-user-session>.
    #
    # Further, even if this WERE secure (which it isn't), this effectively
    # treats Dropbox as an identity provider, which we shouldn't do. From
    # <https://www.dropbox.com/developers/documentation/http/documentation#authorization>:
    #
    #   Note: OAuth is an authorization protocol, not an authentication
    #   protocol. Dropbox should not be used as an identity provider.
    #
    # What we should be doing instead is having logins of our own that
    # refer to at most one auth token. Ye have been warned.
    flask.session[_SESSION_USER_ID] = user_id

    return flask.redirect(flask.url_for('route_'))

# ========================================================================
@_APP.route('/start')
def route_start():
    # This is basically modified from the example code at
    # <http://dropbox-sdk-python.readthedocs.io/en/master/moduledoc.html#dropbox.oauth.DropboxOAuth2Flow>
    dbx_auth_state = hashlib.sha256(os.urandom(24)).hexdigest()
    # Save our random state in the browser so we can compare it with what
    # comes back from Dropbox later
    flask.session[_SESSION_DBX_AUTH_STATE] = dbx_auth_state
    auth_url = _new_dbx_auth_flow(flask.session).start(dbx_auth_state)

    return flask.redirect(auth_url)

# ========================================================================
@_APP.route('/webhook', methods=( 'GET', 'POST' ))
def route_webhook():
    if flask.request.method == 'GET':
        return flask.request.args.get('challenge', '')
    elif flask.request.method == 'POST':
        # Make sure we have a valid request. See
        # <https://www.dropbox.com/developers/reference/webhooks#notifications>.
        signature = flask.request.headers.get('X-Dropbox-Signature')
        expected = hmac.new(_APP.config['DXB_APP_SECRET'], flask.request.data, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(signature, expected):
            flask.abort(403)

        # This is just to make our demo simpler. We shouldn't normally do
        # any processing here. From
        # <https://www.dropbox.com/developers/reference/webhooks#best-practices>:
        #
        #   Your app only has ten seconds to respond to webhook requests.
        #   ... To make sure you can always respond within ten seconds,
        #   you should always do your work on a separate thread ... or
        #   asynchronously using a queue.

        # TODO: What fun things can we do here?

# ========================================================================
def _new_dbx_auth_flow(session):
    return dropbox.DropboxOAuth2Flow(
        _APP.config['DBX_APP_KEY'],
        _APP.config['DBX_APP_SECRET'],
        urljoin(_APP.config['BASE_URL'], flask.url_for('route_finish')),
        session,
        'dbx-auth-csrf-token',
    )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Pretty much everything below this point is unrelated to using the
# Dropbox API
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# ========================================================================
@_APP.teardown_appcontext
def close_db(_):
    if hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db.close()

# ========================================================================
@_APP.cli.command('initdb')
def initdb_command():
    init_db()
    print('initialized database')

# ========================================================================
def connect_db():
    rv = sqlite3.connect(_APP.config['DATABASE'])
    rv.row_factory = sqlite3.Row

    return rv

# ========================================================================
def db_dbx_acct_insert(db, dbx_acct_id, user_name, user_email):
    db.execute(
        """
        INSERT INTO dbx_accts ( dbx_acct_id, user_name, user_email )
        VALUES ( ?, ?, ? )
        """,
        ( dbx_acct_id, user_name, user_email ),
    )

# ========================================================================
def db_dbx_acct_update(db, dbx_acct_id, user_name, user_email):
    db.execute(
        """
        UPDATE dbx_accts SET user_name = ?, user_email = ?
        WHERE dbx_acct_id = ?
        """,
        ( user_name, user_email, dbx_acct_id ),
    )

# ========================================================================
def db_dbx_acct_select(db, dbx_acct_id):
    cur = db.execute(
        """
        SELECT dbx_acct_id, user_name, user_email
        FROM dbx_accts
        WHERE dbx_acct_id = ?
        """,
        ( dbx_acct_id, ),
    )

    return cur.fetchone()

# ========================================================================
def db_user_dbx_acct_select_one_by_user_id(db, user_id):
    cur = db.execute(
        """
        SELECT
            u.user_id AS user_id,
            u.dbx_acct_id AS dbx_acct_id,
            u.dbx_auth_token AS dbx_auth_token,
            da.user_name AS user_name,
            da.user_email AS user_email
        FROM users AS u
        JOIN dbx_accts AS da
        ON da.dbx_acct_id = u.dbx_acct_id
        WHERE u.user_id = ?
        """,
        ( user_id, ),
    )

    return cur.fetchone()

# ========================================================================
def db_user_delete(db, user_id):
    db.execute(
        """
        DELETE FROM users
        WHERE user_id = ?
        """,
        ( user_id, ),
    )

# ========================================================================
def db_user_insert(db, user_id, dbx_acct_id, dbx_auth_token=None):
    db.execute(
        """
        INSERT INTO users ( user_id, dbx_acct_id, dbx_auth_token )
        VALUES ( ?, ?, ? )
        """,
        ( user_id, dbx_acct_id, dbx_auth_token ),
    )

# ========================================================================
def db_user_select_all_deleted_by_dbx_acct_id(db, dbx_acct_id):
    cur = db.execute(
        """
        SELECT user_id, dbx_acct_id, dbx_auth_token
        FROM users
        WHERE dbx_acct_id = ?
        AND user_id LIKE '%-deleted'
        """,
        ( dbx_acct_id, ),
    )

    return cur.fetchall()

# ========================================================================
def db_user_update_for_delete_by_dbx_acct_id(db, dbx_acct_id):
    db.execute(
        """
        UPDATE users
        SET user_id = user_id || '-deleted'
        WHERE dbx_acct_id = ?
        """,
        ( dbx_acct_id, ),
    )

# ========================================================================
def get_db():
    if not hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db = connect_db()

    return flask.g.sqlite_db

# ========================================================================
def init_db():
    db = get_db()

    with _APP.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

    db.commit()

# ---- Initialization ----------------------------------------------------

_APP.config.from_object(__name__)

_APP.config.update(dict(
    DATABASE=os.path.join(_APP.root_path, 'primer.db'),
    SECRET_KEY=bytes_to_native_str(b'__SET_ME__'),
    DBX_APP_KEY=bytes_to_native_str(b'__SET_ME__'),
    DBX_APP_SECRET=bytes_to_native_str(b'__SET_ME__'),
    SITE_TITLE=bytes_to_native_str(b'__SET_ME__'),
    BASE_URL=b'http://localhost:5000/',
))

_APP.config.from_envvar('DBX_API_PRIMER_SETTINGS', silent=True)

if _APP.config['SECRET_KEY'] == bytes_to_native_str(b'__SET_ME__'):
    _APP.logger.critical('SECRET_KEY must be set')
