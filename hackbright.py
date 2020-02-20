"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a GitHub account name, print info about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM students
        WHERE github = :github
        """

    db_cursor = db.session.execute(QUERY, {'github': github})

    row = db_cursor.fetchone()

    print("Student: {} {}\nGitHub account: {}".format(row[0], row[1], row[2]))


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """
    QUERY = """
        INSERT INTO students(first_name, last_name, github)
        VALUES (:first_name, :last_name, :github)
        """
    db.session.execute(QUERY, {'first_name': first_name,
                               'last_name': last_name, 'github': github})

    db.session.commit()

    print(f"Successfully added student: {first_name} {last_name}")

    pass


def get_project_by_title(title):
    """Given a project title, print information about the project."""

    QUERY = """
        SELECT description, max_grade
        FROM projects
        WHERE title = :title
        """

    db_cursor = db.session.execute(QUERY, {'title': title})

    row = db_cursor.fetchone()

    print(f"Project description: {row[0]}\nMax grade: {row[1]}")


def get_grade_by_github_title(github, title):
    """Print grade student received for a project."""

    QUERY = """
        SELECT grade
        FROM grades
        INNER JOIN projects on grades.project_title = projects.title
        WHERE projects.title = :title
            and grades.student_github = :github
        """

    db_cursor = db.session.execute(QUERY, {'title': title, 'github': github})

    row = db_cursor.fetchone()

    print(f"Grade: {row[0]}")


def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation."""

    QUERY = """
    INSERT INTO grades(student_github, project_title, grade)
    VALUES (:github, :title, :grade)
    """

    db.session.execute(QUERY, {'github': github,
                               'title': title, 'grade': grade})

    db.session.commit()

    print(f"Successfully added grade for: {github} on project {title}")


def add_project(title, description, max_grade):
    """ Add a project """

    QUERY = """
    INSERT INTO projects(title, description, max_grade)
    VALUES (:title, :description, :max_grade)
    """

    db.session.execute(QUERY, {'title': title, 'description': description,
                               'max_grade': max_grade})

    db.session.commit()

    print(f"Successfully added project: {title}")


def get_all_grades_for_student(github):
    """ Get all grades for student """

    QUERY = """
        SELECT grades.grade, grades.project_title
        FROM grades
        WHERE grades.student_github = :github
        """

    results = db.session.execute(QUERY, {'github': github})

    for row in results:
        print(f"Project title: {row[1]}, Grade: {row[0]}")


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received
    as a command.
    """

    command = None

    while command != "quit":
        input_string = input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)
        elif command == "new_student":
            first_name, last_name, github = args  # unpack!
            make_new_student(first_name, last_name, github)
        elif command == "project":
            title = args[0]
            get_project_by_title(title)
        elif command == "grade":
            github, title = args
            get_grade_by_github_title(github, title)
        elif command == "add_grade":
            github, title, grade = args
            assign_grade(github, title, grade)
        elif command == "get_all_grades_for_student":
            github = args[0]
            get_all_grades_for_student(github)
        elif command == "add_project":
            index = 0
            title_string = [args[index].replace('"', '')]
            for index in range(1, len(args)):
                if args[index].find('"') > -1:
                    title_string.append(args[index].replace('"', ''))
                    break
                else:
                    title_string.append(args[index])
            title = " ".join(title_string)

            description_string = []
            j_double = 0
            for j in range(index+1, len(args)):
                index += 1
                if args[j].find('"') > -1:
                    j_double += 1
                    description_string.append(args[j].replace('"', ''))
                    if j_double == 2:
                        break
                else:
                    description_string.append(args[j])

            description = " ".join(description_string)
            max_grade = args[index+1]
            add_project(title, description, max_grade)
        else:
            if command != "quit":
                print("Invalid Entry. Try again.")


if __name__ == "__main__":
    connect_to_db(app)

    handle_input()

    # To be tidy, we close our database connection -- though,
    # since this is where our program ends, we'd quit anyway.

    db.session.close()
