from django.shortcuts import render
import requests
import json
import http.client
import os
import logging
from django.http import JsonResponse
from .gemini_api import get_gemini_response, FALLBACK_RESPONSES, logger

# ExerciseDB API key from environment variables
EXERCISE_API_KEY = os.environ.get('EXERCISE_API_KEY', "a25fee685dmsha071584739ac939p10cfb9jsnd120e60f1348")

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