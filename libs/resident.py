from libs import db


def get_last_resident():
    cursor = db.get_vms_system_connection()
    sql = """SELECT
        LVName AS full_name,
        CASE
            WHEN LVgender = 'L' THEN 0
            WHEN LVgender = 'P' THEN 1
        END AS gender,
        LVAdd1 AS address,
        TO_BASE64 (LPhoto) as photo,
        LVNewIC AS no_id
    FROM
        mykadopendata
    ORDER BY
        RdTimeStamp DESC
    LIMIT
        1"""
    result = db.get_one(db.run_query(cursor, sql))
    cursor.close()
    return result
