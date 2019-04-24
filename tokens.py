from enum import Enum


class Token(Enum):
    """This class is an Enumeration for WikiMedia Tokens.
    Most of them are self explaining.

    History:
        v1.27: 'login' and 'createaccount' were introduced.
    """

    CREATE_ACCOUNT = 'createaccount'
    CSRF = 'csrf'
    DELETE_GLOBAL_ACCOUNT = 'deleteglobalaccount'
    LOGIN = 'login'
    PATROL = 'patrol'
    ROLLBACK = 'rollback'
    SET_GLOBAL_ACCOUNT_STATUS = 'setglobalaccountstatus'
    USER_RIGHTS = 'userrights'
    WATCH = 'watch'
