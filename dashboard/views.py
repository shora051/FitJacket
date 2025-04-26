from django.shortcuts import render, redirect, get_object_or_404
import requests
import json
import http.client
import os
import logging
from django.http import JsonResponse
from .gemini_api import get_gemini_response, FALLBACK_RESPONSES, logger
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from datetime import datetime
from .models import Workout, Exercise, FavoriteExercise, WorkoutLog, HealthLog

# ExerciseDB API key from environment variables
EXERCISE_API_KEY = os.environ.get(
    "EXERCISE_API_KEY",
    "a25fee685dmsha071584739ac939p10cfb9jsnd120e60f1348"
)

@login_required
def calendar_view(request):
    user_workouts = Workout.objects.filter(user=request.user)
    workout_logs  = WorkoutLog.objects.filter(user=request.user)
    health_logs   = HealthLog.objects.filter(user=request.user)

    events = []

    # Workout events
    for log in workout_logs:
        events.append({
            "id":    log.id,
            "title": log.workout.name if log.workout else "Rest",
            "start": log.date.isoformat(),
            "color": "#3498db" if log.workout else "#95a5a6"
        })

    # HealthLog events
    for health in health_logs:
        events.append({
            "title": "Tracked Health",
            "start": health.date.isoformat(),
            "color": "#2ecc71",
            "extendedProps": {
                "isHealth": True,
                "calories": health.calories,
                "cardio":   health.cardio_minutes,
                "notes":    health.notes,
                "date":     health.date.isoformat()
            }
        })

    return render(request, 'dashboard/calendar.html', {
        'workouts': user_workouts,
        'events':   json.dumps(events)
    })

@require_POST
@login_required
def log_health_ajax(request):
    try:
        data           = json.loads(request.body)
        date_str       = data.get('date')
        calories       = data.get('calories')
        cardio_minutes = data.get('cardio_minutes')
        notes          = data.get('notes', '')

        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        HealthLog.objects.update_or_create(
            user=request.user,
            date=date,
            defaults={
                'calories':       calories if calories else 0,
                'cardio_minutes': cardio_minutes if cardio_minutes else 0,
                'notes':          notes or ''
            }
        )

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def log_workout(request):
    if request.method == 'POST':
        try:
            data       = json.loads(request.body)
            workout_id = data.get('workout_id')
            date       = data.get('date')

            if workout_id == "rest":
                new_log = WorkoutLog.objects.create(
                    user=request.user,
                    workout=None,
                    date=date
                )
                return JsonResponse({
                    'success': True,
                    'event': {
                        'id':    new_log.id,
                        'title': 'Rest',
                        'start': date,
                        'color': '#95a5a6'
                    }
                })

            workout = Workout.objects.get(id=workout_id, user=request.user)
            new_log = WorkoutLog.objects.create(
                user=request.user,
                workout=workout,
                date=date
            )
            return JsonResponse({
                'success': True,
                'event': {
                    'id':    new_log.id,
                    'title': workout.name,
                    'start': date,
                    'color': '#3498db'
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@require_http_methods(["DELETE"])
@login_required
def delete_workout_log(request):
    try:
        data   = json.loads(request.body)
        log_id = data.get('id')
        log    = WorkoutLog.objects.get(id=log_id, user=request.user)
        log.delete()
        return JsonResponse({'success': True})
    except WorkoutLog.DoesNotExist:
        return JsonResponse({'error': 'Log not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def dashboard(request):
    return render(request, 'dashboard/dashboard.html')

def learn(request):
    return render(request, 'dashboard/learn_exercises.html', {'title': 'Learn Exercises'})

def fetch_exercises(request):
    exercise_name = request.GET.get('query', '')
    url           = f"https://exercisedb.p.rapidapi.com/exercises/name/{exercise_name}"
    headers       = {
        "X-RapidAPI-Key":  EXERCISE_API_KEY,
        "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return JsonResponse(response.json(), safe=False)
    except requests.exceptions.Timeout:
        return JsonResponse({"error": "Request timed out."}, status=504)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def chatbot_query(request):
    if request.method == 'POST':
        try:
            data          = json.loads(request.body)
            query         = data.get('query', '')
            if not query:
                return JsonResponse({"error": "No query provided"}, status=400)

            gemini_resp, err = get_gemini_response(query)
            if gemini_resp:
                return JsonResponse({"response": gemini_resp})

            # fallback
            ql = query.lower()
            for g in ["hello", "hi", "hey"]:
                if ql == g or ql.startswith(g + " "):
                    return JsonResponse({"response": FALLBACK_RESPONSES["hello"]})
            return JsonResponse({"response": FALLBACK_RESPONSES["general"]})
        except Exception:
            return JsonResponse({"response": "Error processing request."})
    return JsonResponse({"error": "Only POST allowed"}, status=405)

def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')

@login_required
def create_plan_view(request):
    workouts = Workout.objects.filter(user=request.user).prefetch_related('exercises')
    return render(request, 'dashboard/createPlan.html', {'workouts': workouts})

def search_exercises_for_plan(request):
    exercise_name = request.GET.get('query', '').lower()
    if not exercise_name:
        return JsonResponse({"error": "Please enter a name"}, status=400)
    url     = f"https://exercisedb.p.rapidapi.com/exercises/name/{exercise_name}"
    headers = {
        "X-RapidAPI-Key":  EXERCISE_API_KEY,
        "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
    }
    try:
        resp      = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        exercises = resp.json()
        names     = [{"id": ex["id"], "name": ex["name"]} for ex in exercises]
        return JsonResponse({"exercises": names})
    except requests.exceptions.Timeout:
        return JsonResponse({"error": "Request timed out."}, status=504)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def workout_api(request):
    if request.method == 'POST':
        data    = json.loads(request.body)
        workout = Workout.objects.create(user=request.user, name=data['name'])
        for ex in data['exercises']:
            Exercise.objects.create(
                workout=workout,
                name=ex['name'],
                sets=ex['sets'],
                reps=ex['reps']
            )
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def save_workout(request):
    if request.method == 'POST':
        try:
            data         = json.loads(request.body)
            workout_name = data.get('name')
            exercises    = data.get('exercises', [])
            workout      = Workout.objects.create(user=request.user, name=workout_name)
            for ex in exercises:
                Exercise.objects.create(
                    workout=workout,
                    name=ex['name'],
                    sets=ex.get('sets', 3),
                    reps=ex.get('reps', 10)
                )
            return JsonResponse({'success': True, 'workout_id': workout.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def update_workout(request, workout_id):
    if request.method == 'POST':
        try:
            workout      = Workout.objects.get(id=workout_id, user=request.user)
            data         = json.loads(request.body)
            workout.name = data.get('name')
            workout.save()
            workout.exercises.all().delete()
            for ex in data.get('exercises', []):
                Exercise.objects.create(
                    workout=workout,
                    name=ex['name'],
                    sets=ex.get('sets', 3),
                    reps=ex.get('reps', 10)
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
        workout   = Workout.objects.get(id=workout_id, user=request.user)
        exercises = workout.exercises.all()
        return JsonResponse({
            'id': workout.id,
            'name': workout.name,
            'exercises': [
                {'name': e.name, 'sets': e.sets, 'reps': e.reps}
                for e in exercises
            ]
        })
    except Workout.DoesNotExist:
        return JsonResponse({'error': 'Workout not found'}, status=404)

@login_required
def add_exercise_to_workout(request, workout_id):
    if request.method == 'POST':
        try:
            workout       = Workout.objects.get(id=workout_id, user=request.user)
            data          = json.loads(request.body)
            exercise_data = data.get('exercise')
            if not exercise_data:
                return JsonResponse({'error': 'No exercise data provided'}, status=400)
            Exercise.objects.create(
                workout=workout,
                name=exercise_data['name'],
                sets=exercise_data['sets'],
                reps=exercise_data['reps']
            )
            return JsonResponse({'success': True, 'message': 'Exercise added successfully'})
        except Workout.DoesNotExist:
            return JsonResponse({'error': 'Workout not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def favorite_exercise(request):
    if request.method == 'POST':
        try:
            data          = json.loads(request.body)
            exercise_data = data.get('exercise', {})
            action        = data.get('action', 'add')
            if not exercise_data.get('name'):
                return JsonResponse({"error": "Invalid exercise data"}, status=400)

            if action == 'add':
                fav, created = FavoriteExercise.objects.get_or_create(
                    user=request.user,
                    name=exercise_data['name'],
                    defaults={
                        'body_part': exercise_data.get('bodyPart'),
                        'equipment': exercise_data.get('equipment'),
                        'target':    exercise_data.get('target'),
                        'gif_url':   exercise_data.get('gifUrl')
                    }
                )
                msg = "Exercise added to favorites" if created else "Exercise already in favorites"
                return JsonResponse({"success": True, "message": msg, "is_favorite": True})

            elif action == 'remove':
                try:
                    fav = FavoriteExercise.objects.get(user=request.user, name=exercise_data['name'])
                    fav.delete()
                    return JsonResponse({"success": True, "message": "Exercise removed", "is_favorite": False})
                except FavoriteExercise.DoesNotExist:
                    return JsonResponse({"success": False, "message": "Not in favorites", "is_favorite": False})

            return JsonResponse({"error": "Invalid action"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only POST allowed"}, status=405)

@login_required
def get_favorite_exercises(request):
    favs = FavoriteExercise.objects.filter(user=request.user)
    return JsonResponse([
        {
            'id':       f.id,
            'name':     f.name,
            'bodyPart': f.body_part,
            'equipment': f.equipment,
            'target':   f.target,
            'gifUrl':   f.gif_url,
            'added_at': f.added_at.isoformat()
        } for f in favs
    ], safe=False)

@login_required
def is_favorite_exercise(request, exercise_name):
    from django.http import JsonResponse
    try:
        FavoriteExercise.objects.get(user=request.user, name=exercise_name)
        return JsonResponse({"is_favorite": True})
    except FavoriteExercise.DoesNotExist:
        return JsonResponse({"is_favorite": False})

# --- New Views for Health History & Editing ---

@login_required
def health_history_view(request):
    logs = HealthLog.objects.filter(user=request.user).order_by('-date')
    return render(request, 'dashboard/health_history.html', {'logs': logs})

@login_required
def edit_health_log(request, log_id):
    hl = get_object_or_404(HealthLog, id=log_id, user=request.user)
    if request.method == 'POST':
        hl.calories       = request.POST.get('calories') or 0
        hl.cardio_minutes = request.POST.get('cardio_minutes') or 0
        hl.notes          = request.POST.get('notes', '')
        hl.save()
        return redirect('dashboard.health_history')
    return render(request, 'dashboard/edit_health_log.html', {'health_log': hl})


