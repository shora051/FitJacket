from django.shortcuts import render
import requests
import json
import http.client
import os
from django.http import JsonResponse

# ExerciseDB API key
EXERCISE_API_KEY = "a25fee685dmsha071584739ac939p10cfb9jsnd120e60f1348"

def dashboard(request):
    return render(request, 'dashboard/dashboard.html')

def exercises(request):
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

# Dictionary of predefined fitness responses for common queries
PREDEFINED_RESPONSES = {
    "hello": "Hello! I'm your FitJacket assistant. How can I help with your fitness journey today?",
    "hi": "Hi there! Ready to talk about fitness and workouts? Ask me anything!",
    "hey": "Hey! What fitness topics can I help you with today?",
    
    "workout": "A good balanced workout routine includes strength training 2-3 times per week, cardio 3-5 times per week, and flexibility exercises daily. Remember to give muscle groups 48 hours to recover between strength sessions.",
    "exercise": "Regular exercise has amazing benefits: improved mood, better sleep, increased energy, reduced disease risk, and weight management. Aim for 150 minutes of moderate activity weekly.",
    "cardio": "Cardio exercises like running, cycling, and swimming improve heart health, build endurance, and burn calories. Start with 20-30 minutes, 3 times weekly, and gradually increase.",
    
    "strength": "Strength training builds muscle, boosts metabolism, and improves bone density. Include exercises for all major muscle groups: chest, back, arms, shoulders, legs, and core.",
    "weights": "When lifting weights, focus on proper form over heavy weight. Start light, master the movement, then gradually increase. Breathe out during exertion and in during the return.",
    "muscles": "To build muscle effectively: lift progressively heavier weights, eat sufficient protein (0.7-1g per pound of bodyweight), and ensure adequate recovery with 7-9 hours of sleep.",
    
    "diet": "A balanced diet should include: protein (lean meats, eggs, legumes), complex carbs (whole grains, fruits, vegetables), and healthy fats (avocados, nuts, olive oil). Stay hydrated and limit processed foods.",
    "nutrition": "Good nutrition fuels your workouts and supports recovery. Time your meals around workouts: carbs before for energy, protein after for muscle repair.",
    "protein": "Protein is essential for muscle repair and growth. Good sources include chicken, fish, eggs, dairy, tofu, legumes, and protein supplements if needed. Aim to include some in every meal.",
    
    "weight loss": "Successful weight loss combines a modest calorie deficit (300-500 calories/day), regular exercise (both cardio and strength training), adequate protein, and consistency over time.",
    "fat burn": "To maximize fat burning: incorporate high-intensity interval training (HIIT), strength train to build metabolism-boosting muscle, stay active throughout the day, and maintain a slight calorie deficit.",
    "calories": "Your calorie needs depend on age, gender, weight, height, and activity level. Many fitness apps can help calculate this. Adjust based on your goals - slight deficit for weight loss, surplus for muscle gain.",
    
    "warm up": "Always warm up for 5-10 minutes before exercising. Include light cardio to raise heart rate and dynamic stretches for the muscles you'll be using. This improves performance and reduces injury risk.",
    "stretching": "Stretch when your muscles are warm (after exercise is ideal). Hold static stretches for 15-30 seconds, breathing deeply. Never stretch to the point of pain - mild tension is the goal.",
    "cool down": "Cooling down with light activity and stretching helps return your heart rate to normal, prevent blood pooling in extremities, and may reduce muscle soreness.",
    
    "rest": "Rest days are crucial for recovery, muscle growth, and preventing burnout. Active recovery (like light walking or yoga) can be beneficial, but ensure you're giving your body time to repair.",
    "recovery": "Enhance recovery with proper nutrition, hydration, 7-9 hours of quality sleep, foam rolling/massage, contrast therapy (alternating hot/cold), and stress management techniques.",
    "sleep": "Sleep is when your body repairs muscle tissue and consolidates fitness gains. Aim for 7-9 hours nightly. Improve sleep quality by maintaining a regular schedule and creating a restful environment.",
    
    "beginner": "As a beginner, focus on consistency over intensity. Start with 2-3 workouts weekly, gradually increasing duration and frequency. Learn proper form before adding weight or complexity.",
    "motivation": "Stay motivated by setting specific goals, tracking progress, finding workout buddies, mixing up your routine, rewarding achievements, and remembering your 'why' - your deeper reason for pursuing fitness.",
    "injury": "For minor injuries, remember RICE: Rest, Ice, Compression, Elevation. Stop activity if you experience pain, not just soreness. Consult a healthcare professional for persistent or severe pain.",
    
    "routine": "A well-rounded weekly routine might include: 2-3 days of strength training, 2-3 days of cardio (mix of high and low intensity), 1-2 days of flexibility/mobility work, and at least 1 full rest day.",
    "progress": "Track progress using multiple metrics: weight/reps lifted, workout duration/intensity, body measurements, progress photos, how clothes fit, energy levels, and mood improvements - not just scale weight.",
}

def get_fitness_response(query):
    """Get a predefined response based on keywords in the query"""
    query = query.lower()
    
    # Special case for greetings - directly match
    for greeting in ["hello", "hi", "hey"]:
        if query == greeting or query.startswith(greeting + " "):
            return PREDEFINED_RESPONSES[greeting]
    
    # For other queries, check if keywords are contained in the question
    for keyword, response in PREDEFINED_RESPONSES.items():
        if keyword in query:
            return response
    
    # Default response if no keywords match
    return "I'm your FitJacket fitness assistant! You can ask me about workouts, specific exercises, nutrition, recovery, or fitness tips. For example, try asking about 'strength training' or 'cardio exercises'."

def chatbot_query(request):
    """API view to handle chatbot queries using simple keyword matching"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
            
            if not query:
                return JsonResponse({"error": "No query provided"}, status=400)
            
            # Get the response based on keywords
            response = get_fitness_response(query)
            return JsonResponse({"response": response})
                
        except Exception as e:
            print(f"Chatbot query error: {str(e)}")
            return JsonResponse({
                "response": "Sorry, I encountered an error processing your request. Please try again with a different question."
            })
    
    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)