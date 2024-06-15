import traceback
from django.db import connections


def get_vms_system_connection():
    return connections["vms_system"].cursor()


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def run_query(cursor, raw_query, variables=[]):
    cursor.execute(raw_query, variables)
    result = dictfetchall(cursor)

    return result


def get_one(result):
    try:
        return result[0]
    except:
        return None
