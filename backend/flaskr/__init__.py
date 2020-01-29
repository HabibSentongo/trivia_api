import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/v1/*": {"origins": "*"} })
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
    return response  


  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''


  @app.route('/api/v1/categories')
  def get_all_categories():
    """
    Get all categories.
    """
    try:
      categories = Category.query.all()
      if not categories:
          abort(404)
      return jsonify({
          'success': True,
          'categories': [category.type for category in categories]
      }), 200
    except Exception as error:
        raise error
    finally:
        db.session.close()  
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  def paginate_quetions(request, selection):
    """ 
    Get available questions and return a paginated result 
    """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

  @app.route('/api/v1/questions')
  def get_all_questions():
    """
    Get all available questions paginated 
    by a maximum number of 10 questions per page.
    """
    try:
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_quetions(request, selection)
      categories = {
          category.id: category.type for category in Category.query.all()
      }

      if len(current_questions) == 0:
        abort(404)

      return jsonify({
          'success': True,
          'questions': current_questions,
          'categories': categories,
          'total_questions': len(selection),
          'current_category': None
      }), 200
    except Exception as error:
      raise error
    finally:
      db.session.close()
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route("/api/v1/questions/<int:question_id>", methods=['DELETE'])
  def delete_a_question(question_id):
    """
    Delete the question of a given id specified in the request url
    """
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if not question:
        abort(404)

      question.delete()

      return jsonify({
        'success': True,
        'message': 'Question successfully deleted'
      }), 200
    except Exception as error:
        raise error      
    finally:
      db.session.close()    
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route("/api/v1/questions", methods=['POST'])
  def add_a_question():
    """
    Create a new question given question body, 
    answer, category_id, and difficult_id.  
    """
    try:
      body = request.get_json()
      
      new_question = Question(
        question = body.get('question', None),
        answer = body.get('answer', None),
        category = body.get('category', None),
        difficulty = body.get('difficulty', None)
      )

      if not (new_question.question and new_question.answer and \
        new_question.category and new_question.difficulty):
        abort(400)

      new_question.insert()

      return jsonify({
        'success': True,
        'message': 'Question successfully added'
      }), 201
    except Exception as error:
        raise error      
    finally:
      db.session.close()   
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/api/v1/questions/search', methods=['POST'])
  def get_all_questions_by_search_term():
    """
    Get all questions based on a search term given it's a substring of the question
    """
    try:
      search_term = request.get_json().get('searchTerm', None)
      all_questions = Question.query.filter(
        Question.question.ilike("%" + search_term + "%")
      ).all()
      current_questions = paginate_quetions(request, all_questions)

      if not current_questions:
        abort(404)

      return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(all_questions),
          'current_category': None
      })
    except Exception as error:
        raise error      
    finally:
      db.session.close()  
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/api/v1/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    """
    Get all available questions of a given category
    """
    try:
      category = Category.query.get(category_id)
      selection = Question.query.filter_by(category=category_id).all()
      current_questions = paginate_quetions(request, selection)
      if not current_questions:
          abort(404)
      return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(selection),
          'current_category': category_id
      }), 200
    except Exception as error:
        raise error
    finally:
      db.session.close()  
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route("/api/v1/quizzes", methods=["POST"])
  def play_quiz_game():
    """
    Play a quiz by returning random questions within 
    a given category if provided and that is not one of the
    previous questions.
    """
    try:
      data = request.get_json()
      previous_questions = data.get("previous_questions")
      quiz_category = data.get("quiz_category")
      quiz_category_id = int(quiz_category["id"])

      question = Question.query.filter(
          Question.id.notin_(previous_questions)
      )

      if quiz_category_id:
          question = question.filter_by(category=quiz_category_id)

      question = question.first().format()

      return jsonify({"success": True, "question": question,}), 200
    except Exception as error:
        raise error      
    finally:
      db.session.close()  
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(400)
  def error400(error):
      response = jsonify({
          'success': False,
          'message': 'Bad Request'
      })
      return response, 400
  
  @app.errorhandler(404)
  def error404(error):
      response = jsonify({
          'success': False,
          'message': 'Resource not found'
      })
      return response, 404

  @app.errorhandler(405)
  def error405(error):
      response = jsonify({
          'success': False,
          'message': 'Method not allowed'
      })
      return response, 405

  @app.errorhandler(422)
  def error422(error):
      response = jsonify({
          'message': 'Unable to process request'
      })
      return response, 422

  @app.errorhandler(500)
  def error500(error):
      response = jsonify({
          'success': False,
          'message': 'Internal server error'
      })
      return response, 500

  return app
