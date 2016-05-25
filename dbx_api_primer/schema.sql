PRAGMA fullfsync = 1 ;
PRAGMA encoding = 'UTF-8' ;

CREATE TABLE IF NOT EXISTS dbx_accts (
    dbx_acct_id TEXT PRIMARY KEY NOT NULL,
    user_name TEXT NOT NULL,
    user_email TEXT
) ;

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY NOT NULL,
    dbx_acct_id TEXT NOT NULL REFERENCES dbx_users ( dbx_acct_id ),
    dbx_auth_token TEXT NOT NULL
) ;
