import mysql.connector
import shortuuid
from data import exam_code_map, sub_codes_map
from env import DATABASE, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, DATABASE_USER

students_db = mysql.connector.connect(user=DATABASE_USER,
                                      password=DATABASE_PASSWORD,
                                      host=DATABASE_HOST,
                                      port=DATABASE_PORT,
                                      database=DATABASE)
cursor = students_db.cursor()


def get_students(student_class=None, name=None):
    if name:
        query = f"SELECT * FROM students WHERE name='{name}';"
    elif student_class:
        query = f"SELECT * FROM students WHERE class='{student_class}' ORDER BY class;"
    else:
        query = "SELECT * FROM students ORDER BY class;"

    cursor.reset()
    cursor.execute(query)
    result = cursor.fetchall()

    if len(result) > 0:
        return result
    else:
        return []


def register_student(name, grade,
                     father_name,
                     mother_name,
                     father_phone,
                     mother_phone,
                     roll,
                     address):
    cursor.reset()
    unique_id = shortuuid.ShortUUID(alphabet="0123456789").random(length=5)
    query = f"INSERT INTO students (`id`, `name`, `class`, `father_name`, `mother_name`, `address`, `father_no`, `mother_no`, `roll_no`)  VALUES ('{unique_id}', '{name}', '{grade}', '{father_name}', '{mother_name}', '{address}', '{father_phone}', '{mother_phone}', '{roll}')"
    cursor.execute(query)
    students_db.commit()
    for sub in sub_codes_map:
        query = f"INSERT INTO marks (`id_fk`, `sub_code`) VALUES ('{unique_id}', '{sub[0]}')"
        cursor.execute(query)
        students_db.commit()


def validate_new_student(grade, roll):
    cursor.reset()
    query = f"SELECT * FROM students WHERE class='{grade}' AND roll_no='{roll}'"
    cursor.execute(query)
    result = cursor.fetchall()

    if len(result) > 0:
        return False
    else:
        return True


def update_student_details(student_id, name, father_name, mother_name, father_phone, mother_phone, address):
    cursor.reset()
    query = f"UPDATE students SET name='{name}', father_name='{father_name}', mother_name='{mother_name}'," \
            f" address='{address}', father_no='{father_phone}', mother_no='{mother_phone}' WHERE id={student_id}"
    cursor.execute(query)
    students_db.commit()


def update_student_marks(student_id, exam_id, marks_map):
    cursor.reset()
    for subjects in marks_map:
        query = f"UPDATE marks SET {exam_id}='{subjects[1]}' WHERE id_fk={student_id} AND sub_code='{subjects[0]}'"
        cursor.execute(query)
        students_db.commit()


def get_student_details(student_id):
    cursor.reset()
    query = f"SELECT * FROM students WHERE id={student_id}"
    cursor.execute(query)
    result = cursor.fetchall()

    if len(result) > 0:
        r = {}
        for exam in exam_code_map:
            query = f"SELECT sub_code, {exam[0]} FROM marks WHERE id_fk={student_id};"
            cursor.execute(query)
            marks_result = cursor.fetchall()

            r[exam[0]] = {sub[0]: sub[1] for sub in marks_result}

        return {
            "details": result,
            "marks": r
        }
    else:
        return []


def delete_student_sql(student_id):
    cursor.reset()
    query = f"DELETE FROM marks WHERE id_fk={student_id}"
    cursor.execute(query)
    query = f"DELETE FROM students WHERE id={student_id}"
    cursor.execute(query)
    students_db.commit()
