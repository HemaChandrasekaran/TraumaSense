import sqlite3
import json
from datetime import datetime


DATABASE_NAME = "trauma_assessment.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    connection = get_connection()

    cursor = connection.cursor()


    # --------------------------------------------------------
    # ASSESSMENT CASES
    # --------------------------------------------------------

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS cases (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            stress REAL,

            fear REAL,

            anxiety REAL,

            trauma_distress REAL,

            vulnerability REAL,

            svi REAL,

            risk TEXT,

            safety_flag INTEGER,

            safety_indicators TEXT,

            svi_contributions TEXT,

            svi_explanation TEXT,

            original_text TEXT,

            recommendations TEXT,

            status TEXT DEFAULT
                'Awaiting Human Review',

            created_at TEXT

        )

    """)


    # --------------------------------------------------------
    # ANONYMOUS SESSIONS
    # --------------------------------------------------------

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS anonymous_sessions (

            session_id TEXT PRIMARY KEY,

            risk TEXT DEFAULT 'UNKNOWN',

            safety_flag INTEGER DEFAULT 0,

            svi REAL DEFAULT 0,

            human_review INTEGER DEFAULT 0,

            created_at TEXT

        )

    """)


    # --------------------------------------------------------
    # ANONYMOUS CHAT MESSAGES
    # --------------------------------------------------------

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS anonymous_messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_id TEXT,

            sender TEXT,

            message TEXT,

            created_at TEXT,

            FOREIGN KEY(session_id)
                REFERENCES anonymous_sessions(session_id)

        )

    """)


    connection.commit()

    connection.close()


# ============================================================
# SAVE ASSESSMENT CASE
# ============================================================

def save_case(

    result,

    original_text,

    recommendations

):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""

        INSERT INTO cases (

            stress,

            fear,

            anxiety,

            trauma_distress,

            vulnerability,

            svi,

            risk,

            safety_flag,

            safety_indicators,

            svi_contributions,

            svi_explanation,

            original_text,

            recommendations,

            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        result.get("stress", 0),

        result.get("fear", 0),

        result.get("anxiety", 0),

        result.get(
            "trauma_distress",
            0
        ),

        result.get(
            "vulnerability",
            0
        ),

        result.get("svi", 0),

        result.get(
            "risk",
            "UNKNOWN"
        ),

        int(
            result.get(
                "safety_flag",
                False
            )
        ),

        json.dumps(
            result.get(
                "safety_indicators",
                []
            )
        ),

        json.dumps(
            result.get(
                "svi_contributions",
                {}
            )
        ),

        result.get(
            "svi_explanation",
            ""
        ),

        original_text,

        json.dumps(
            recommendations
        ),

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    ))


    case_id = cursor.lastrowid


    connection.commit()

    connection.close()


    return case_id


# ============================================================
# GET CASES
# ============================================================

def get_cases():

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""

        SELECT *

        FROM cases

        ORDER BY id DESC

    """)


    cases = cursor.fetchall()


    connection.close()


    return cases


# ============================================================
# GET STATISTICS
# ============================================================

def get_statistics():

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""

        SELECT COUNT(*) AS total

        FROM cases

    """)

    total = cursor.fetchone()["total"]


    cursor.execute("""

        SELECT COUNT(*) AS high

        FROM cases

        WHERE risk = 'HIGH'

    """)

    high = cursor.fetchone()["high"]


    cursor.execute("""

        SELECT COUNT(*) AS medium

        FROM cases

        WHERE risk = 'MEDIUM'

    """)

    medium = cursor.fetchone()["medium"]


    cursor.execute("""

        SELECT COUNT(*) AS low

        FROM cases

        WHERE risk = 'LOW'

    """)

    low = cursor.fetchone()["low"]


    connection.close()


    return {

        "total":
            total,

        "high":
            high,

        "medium":
            medium,

        "low":
            low

    }


# ============================================================
# UPDATE CASE STATUS
# ============================================================

def update_status(

    case_id,

    status

):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""

        UPDATE cases

        SET status = ?

        WHERE id = ?

    """, (

        status,

        case_id

    ))


    connection.commit()

    connection.close()


# ============================================================
# CREATE ANONYMOUS SESSION
# ============================================================

def create_anonymous_session(

    session_id

):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""

        INSERT OR IGNORE INTO
        anonymous_sessions (

            session_id,

            created_at

        )

        VALUES (?, ?)

    """, (

        session_id,

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    ))


    connection.commit()

    connection.close()


# ============================================================
# UPDATE ANONYMOUS SESSION
# ============================================================

def update_anonymous_session(

    session_id,

    risk="UNKNOWN",

    safety_flag=False,

    svi=0,

    human_review=False

):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""

        UPDATE anonymous_sessions

        SET

            risk = ?,

            safety_flag = ?,

            svi = ?,

            human_review = ?

        WHERE session_id = ?

    """, (

        risk,

        int(safety_flag),

        svi,

        int(human_review),

        session_id

    ))


    connection.commit()

    connection.close()


# ============================================================
# SAVE ANONYMOUS MESSAGE
# ============================================================

def save_anonymous_message(

    session_id,

    sender,

    message

):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""

        INSERT INTO anonymous_messages (

            session_id,

            sender,

            message,

            created_at

        )

        VALUES (?, ?, ?, ?)

    """, (

        session_id,

        sender,

        message,

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    ))


    message_id = cursor.lastrowid


    connection.commit()

    connection.close()


    return message_id


# ============================================================
# GET ANONYMOUS MESSAGES
# ============================================================

def get_anonymous_messages(

    session_id

):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""

        SELECT *

        FROM anonymous_messages

        WHERE session_id = ?

        ORDER BY id ASC

    """, (

        session_id,

    ))


    messages = cursor.fetchall()


    connection.close()


    return messages


# ============================================================
# GET ANONYMOUS SESSIONS
# ============================================================

def get_anonymous_sessions():

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""

        SELECT *

        FROM anonymous_sessions

        ORDER BY created_at DESC

    """)


    sessions = cursor.fetchall()


    connection.close()


    return sessions