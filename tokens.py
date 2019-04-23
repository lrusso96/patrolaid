from enum import Enum


class Token(Enum):
    CREATE_ACCOUNT = 'createaccount'
    CSRF = 'csrf'
    DELETE_GLOBAL_ACCOUNT = 'deleteglobalaccount'
    LOGIN = 'login'
    PATROL = 'patrol'
    ROLLBACK = 'rollback'
    SET_GLOBAL_ACCOUNT_STATUS = 'setglobalaccountstatus'
    USER_RIGHTS = 'userrights'
    WATCH = 'watch'
