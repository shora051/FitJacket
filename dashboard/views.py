from django.shortcuts import render, redirect
import requests
import json
import http.client
import os
import logging
from django.http import JsonResponse
from .gemini_api import get_gemini_response, FALLBACK_RESPONSES, logger
from django.contrib.auth.decorators import login_required
from .models import Workout, Exercise, FavoriteExercise

# ExerciseDB API key from environment variables
EXERCISE_API_KEY = os.environ.get('EXERCISE_API_KEY', "a25fee685dmsha071584739ac939p10cfb9jsnd120e60f1348")


@login_required
def calendar_view(request):
    return render(request, 'dashboard/calendar.html')


def dashboard(request):
    return render(request, 'dashboard/dashboard.html')


def learn(request):
    context = {
        'title': 'Learn Exercises'
    }
    return render(request, 'dashboard/learn_exercises.html', context)


def fetch_exercises(request):
    """API view to fetch exercises from ExerciseDB"""
    exercise_name = request.GET.get('query', '')

    url = "https://exercisedb.p.rapidapi.com/exercises/name/" + exercise_name

    headers = {
        "X-RapidAPI-Key": EXERCISE_API_KEY,
        "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
    }

    try:
        # Set a timeout for the request
        response = requests.get(url, headers=headers, timeout=10)
        return JsonResponse(response.json(), safe=False)
    except requests.exceptions.Timeout:
        return JsonResponse({"error": "Request timed out. Please try again."}, status=504)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def chatbot_query(request):
    """API view to handle chatbot queries using Gemini API with fallback to keyword matching"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '')

            if not query:
                return JsonResponse({"error": "No query provided"}, status=400)

            logger.info(f"Received chatbot query: '{query}'")

            # Try to get response from Gemini API
            gemini_response, error = get_gemini_response(query)

            # If Gemini response was successful
            if gemini_response:
                logger.info("Successfully generated Gemini response")
                return JsonResponse({"response": gemini_response})

            # If Gemini failed, log the error and use fallback
            logger.warning(f"Falling back to predefined responses due to Gemini error: {error}")

            # Simple fallback based on keywords in the query
            query_lower = query.lower()

            # Check for greetings
            for greeting in ["hello", "hi", "hey"]:
                if query_lower == greeting or query_lower.startswith(greeting + " "):
                    return JsonResponse({"response": FALLBACK_RESPONSES["hello"]})

            # Default fallback response
            response = FALLBACK_RESPONSES["general"]
            return JsonResponse({"response": response})

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Chatbot query processing error: {error_msg}")
            return JsonResponse({
                "response": "Sorry, I encountered an error processing your request. Please try again with a different question."
            })

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')


@login_required
def create_plan_view(request):
    workouts = Workout.objects.filter(user=request.user).prefetch_related('exercises')
    return render(request, 'dashboard/createPlan.html', {'workouts': workouts})


def search_exercises_for_plan(request):
    """API view to fetch exercise names from ExerciseDB for the create plan page"""
    exercise_name = request.GET.get('query', '').lower()

    if not exercise_name:
        return JsonResponse({"error": "Please enter an exercise name"}, status=400)

    url = f"https://exercisedb.p.rapidapi.com/exercises/name/{exercise_name}"

    headers = {
        "X-RapidAPI-Key": EXERCISE_API_KEY,
        "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        exercises = response.json()
        # Only return the names of the exercises
        exercise_names = [{"id": ex["id"], "name": ex["name"]} for ex in exercises]

        return JsonResponse({
            "exercises": exercise_names
        })

    except requests.exceptions.Timeout:
        return JsonResponse({"error": "Request timed out. Please try again."}, status=504)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def workout_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        workout = Workout.objects.create(
            user=request.user,
            name=data['name']
        )

        # Add exercises
        for exercise in data['exercises']:
            Exercise.objects.create(
                workout=workout,
                name=exercise['name'],
                sets=exercise['sets'],
                reps=exercise['reps']
            )

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def save_workout(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug(f"Received data for saving workout: {data}")
            workout_name = data.get('name')
            exercises = data.get('exercises', [])

            # Create new workout
            workout = Workout.objects.create(
                user=request.user,
                name=workout_name
            )

            # Add exercises to workout
            for exercise_data in exercises:
                Exercise.objects.create(
                    workout=workout,
                    name=exercise_data['name'],
                    sets=exercise_data.get('sets', 3),
                    reps=exercise_data.get('reps', 10)
                )

            logger.debug(f"Exercises for workout {workout.id}: {list(exercises)}")

            return JsonResponse({'success': True, 'workout_id': workout.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def update_workout(request, workout_id):
    if request.method == 'POST':
        try:
            workout = Workout.objects.get(id=workout_id, user=request.user)
            data = json.loads(request.body)

            # Update workout name
            workout.name = data.get('name')
            workout.save()

            # Delete existing exercises
            workout.exercises.all().delete()

            # Add new exercises
            for exercise_data in data.get('exercises', []):
                Exercise.objects.create(
                    workout=workout,
                    name=exercise_data['name'],
                    sets=exercise_data.get('sets', 3),
                    reps=exercise_data.get('reps', 10)
                )

            return JsonResponse({'success': True})
        except Workout.DoesNotExist:
            return JsonResponse({'error': 'Workout not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def delete_workout(request, workout_id):
    if request.method == 'DELETE':
        try:
            workout = Workout.objects.get(id=workout_id, user=request.user)
            workout.delete()
            return JsonResponse({'success': True})
        except Workout.DoesNotExist:
            return JsonResponse({'error': 'Workout not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def get_workout_details(request, workout_id):
    try:
        workout = Workout.objects.get(id=workout_id, user=request.user)
        exercises = workout.exercises.all()  # Fetch related exercises

        logger.debug(f"Exercises for workout {workout_id}: {list(exercises)}")

        return JsonResponse({
            'id': workout.id,
            'name': workout.name,
            'exercises': [
                {
                    'name': exercise.name,
                    'sets': exercise.sets,
                    'reps': exercise.reps
                }
                for exercise in exercises
            ]
        })
    except Workout.DoesNotExist:
        return JsonResponse({'error': 'Workout not found'}, status=404)


@login_required
def add_exercise_to_workout(request, workout_id):
    if request.method == 'POST':
        try:
            workout = Workout.objects.get(id=workout_id, user=request.user)
            data = json.loads(request.body)
            exercise_data = data.get('exercise')

            if not exercise_data:
                return JsonResponse({'error': 'No exercise data provided'}, status=400)

            # Create the exercise
            Exercise.objects.create(
                workout=workout,
                name=exercise_data['name'],
                sets=exercise_data['sets'],
                reps=exercise_data['reps']
            )

            console.log('Exercises retrieved:', data.exercises)

            return JsonResponse({
                'success': True,
                'message': 'Exercise added successfully'
            })


        except Workout.DoesNotExist:
            return JsonResponse({'error': 'Workout not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def favorite_exercise(request):
    """Add or remove an exercise from user's favorites"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            exercise_data = data.get('exercise', {})
            action = data.get('action', 'add')  # 'add' or 'remove'

            if not exercise_data or 'name' not in exercise_data:
                return JsonResponse({"error": "Invalid exercise data"}, status=400)

            if action == 'add':
                # Add to favorites (using get_or_create to handle duplicates)
                favorite, created = FavoriteExercise.objects.get_or_create(
                    user=request.user,
                    name=exercise_data['name'],
                    defaults={
                        'body_part': exercise_data.get('bodyPart'),
                        'equipment': exercise_data.get('equipment'),
                        'target': exercise_data.get('target'),
                        'gif_url': exercise_data.get('gifUrl')
                    }
                )

                message = "Exercise added to favorites" if created else "Exercise already in favorites"
                return JsonResponse({
                    "success": True,
                    "message": message,
                    "is_favorite": True
                })

            elif action == 'remove':
                # Remove from favorites
                try:
                    favorite = FavoriteExercise.objects.get(
                        user=request.user,
                        name=exercise_data['name']
                    )
                    favorite.delete()
                    return JsonResponse({
                        "success": True,
                        "message": "Exercise removed from favorites",
                        "is_favorite": False
                    })
                except FavoriteExercise.DoesNotExist:
                    return JsonResponse({
                        "success": False,
                        "message": "Exercise not in favorites",
                        "is_favorite": False
                    })

            return JsonResponse({"error": "Invalid action"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


@login_required
def get_favorite_exercises(request):
    """Get a list of all user's favorite exercises"""
    favorites = FavoriteExercise.objects.filter(user=request.user)

    favorite_list = [{
        'id': fav.id,
        'name': fav.name,
        'bodyPart': fav.body_part,
        'equipment': fav.equipment,
        'target': fav.target,
        'gifUrl': fav.gif_url,
        'added_at': fav.added_at.isoformat()
    } for fav in favorites]

    return JsonResponse(favorite_list, safe=False)


@login_required
def is_favorite_exercise(request, exercise_name):
    """Check if an exercise is in user's favorites"""
    try:
        FavoriteExercise.objects.get(user=request.user, name=exercise_name)
        return JsonResponse({"is_favorite": True})
    except FavoriteExercise.DoesNotExist:
        return JsonResponse({"is_favorite": False})
