import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'habib1234','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            self.category = Category(type='Math')
            self.db.session.add(self.category)
            self.db.session.flush()
            self.question = Question(
                question='What is four by four?',
                answer='Sixteen',
                category=self.category.id, 
                difficulty=2
            )
            self.db.session.add(self.question)
            self.db.session.commit()


    def tearDown(self):
        """Executed after reach test"""
        with self.app.app_context():
            self.db.session.query(Question).delete()
            self.db.session.query(Category).delete()
            self.db.session.commit()
            self.db.session.close()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_success_response_for_get_categories(self):
        """
            Test success response for getting all categories
        """
        response = self.client().get("/api/v1/categories")
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(data['success'], True)

    def test_success_response_for_get_questions(self):
        """
            Test success response for getting all questions 
        """
        response = self.client().get('/api/v1/questions')
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(data['success'], True)

    def test_failure_response_for_get_questions(self):
        """
            Test retrieving questions from empty database
        """
        question = Question.query.first()
        question.delete()
        response = self.client().get('/api/v1/questions')
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_success_response_for_deleting_a_question(self):
        """
            Test deleting a question that exists in the database
        """
        question_id = Question.query.first().id
        response = self.client().delete(f"/api/v1/questions/{question_id}")
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully deleted')

    def test_failure_response_for_deleting_a_question(self):
        """
            Test deleting a question that doesnot exist in the database
        """
        question_id = Question.query.first().id
        response = self.client().delete(f"/api/v1/questions/{question_id + 1}")
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_success_response_for_getting_questions_of_given_category(self):
        """
            Test getting all questions of a given category
        """
        category_id = Category.query.first().id
        response = self.client().get(f"/api/v1/categories/{category_id}/questions")
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 1)

    def test_failure_response_for_getting_questions_of_given_category(self):
        """
            Test getting all questions of a category that doesnot exist
        """
        category_id = Category.query.first().id
        response = self.client().get(f"/api/v1/categories/{category_id + 1}/questions")
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_successfully_adding_a_question_to_database(self):
        """
            Test creating a valid question in the database
        """
        response = self.client().post('/api/v1/questions',
            content_type='application/json',
            data=json.dumps(
            {
                'question': 'Is computer Science good?',
                'answer': 'Yes its good',
                'difficulty': 2,
                'category': 2
            }
            )
        )
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully added')

    def test_adding_a_question_with_invalid_url(self):
        """
            Test creating a question with a wrong request url
        """
        response = self.client().post('/api/v1/questions/2',
            content_type='application/json',
            data=json.dumps(
            {
                'question': 'Is computer Science good?',
                'answer': 'Yes its good',
                'difficulty': 2,
                'category': 2
            }
            )
        )
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')

    def test_success_response_for_searching_a_question_in_the_database(self):
        """
            Test searching a question using a correct search term.
        """
        search_term = 'four'
        response = self.client().post('/api/v1/questions/search',
            content_type='application/json',
            data=json.dumps({'searchTerm': search_term})
        )
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 1)

    def test_failure_response_for_searching_a_question_not_in_the_database(self):
        """
            Test searching a question using a wrong search term.
        """
        search_term = 'fred'
        response = self.client().post('/api/v1/questions/search',
            content_type='application/json',
            data=json.dumps({'searchTerm': search_term})
        )
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_success_response_for_playing_quiz_game(self):
        """
            Test playing a quiz category and previous question parameters.
        """
        response = self.client().post('/api/v1/quizzes',
            content_type='application/json',
            data=json.dumps(
                {'previous_questions': [], 'quiz_category': {'id': 0, 'type': 'all'}}
            )
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_failure_response_for_playing_quiz_game(self):
        """
            Test playing a quiz category a wrong request method.
        """
        response = self.client().get('/api/v1/quizzes')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
