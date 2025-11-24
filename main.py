import os
import cv2
import speech_recognition as sr
from deepface import DeepFace
from groq import Groq
import time
import subprocess

# ====================================================
# 1. GROQ CLIENT
# ====================================================
os.environ["GROQ_API_KEY"] = "api_key"

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages_prmt = [
    {
        "role": "system",
        "content": "You are a friendly emotional assistant. "
                   "Speak naturally like a human. No motivational lectures."
    }
]

def groq_chatbot(user_input):
    global messages_prmt
    

    messages_prmt.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        messages=messages_prmt,
        model="llama-3.3-70b-versatile",
        max_tokens=150
    )

    reply = response.choices[0].message.content
    
    # clean reply for speaking
    reply = reply.replace("\n", " ").strip()

    messages_prmt.append({"role": "assistant", "content": reply})
    return reply


# ====================================================
# 2. 100% WORKING TEXT-TO-SPEECH (POWERSHELL METHOD)
# ====================================================
def speak(text):
    print("Assistant:", text)
    
    # Clean text for PowerShell
    text = text.replace('"', "'").replace('$', '').replace('`', '')
    
    try:
        # Method 1: Direct PowerShell command (MOST RELIABLE)
        ps_command = f'''
        Add-Type -AssemblyName System.Speech
        $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer
        $speak.Speak("{text}")
        '''
        
        # Run PowerShell command
        subprocess.run(['powershell', '-Command', ps_command], 
                      capture_output=True, timeout=30)
        
    except Exception as e:
        print(f"Speech error: {e}")
        # Fallback: Try simple PowerShell
        try:
            os.system(f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\\\"{text}\\\')"')
        except:
            print("All speech methods failed")


# ====================================================
# 3. SPEECH-TO-TEXT
# ====================================================
recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        print("Listening…")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=10)
            text = recognizer.recognize_google(audio)
            print("You:", text)
            return text.lower()
        except sr.WaitTimeoutError:
            speak("I didn't hear anything. Please speak.")
            return ""
        except sr.UnknownValueError:
            speak("I didn't understand that. Can you repeat?")
            return ""
        except Exception as e:
            speak("There was a problem with the microphone.")
            return ""


# ====================================================
# 4. EMOTION DETECTION
# ====================================================
def detect_emotion():
    speak("Look at the camera. I'm checking your emotion.")

    cap = cv2.VideoCapture(0)
    emotion_detected = False
    emotion = "neutral"

    for _ in range(50):  # Check 50 frames maximum
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Emotion Detection", frame)

        try:
            result = DeepFace.analyze(
                frame,
                actions=['emotion'],
                enforce_detection=False
            )
            emotion = result[0]['dominant_emotion']
            emotion_detected = True
            break
        except:
            pass

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
    if emotion_detected:
        print(f"Detected Emotion: {emotion}")
    else:
        print("Could not detect emotion, using neutral")
        
    return emotion


# ====================================================
# 5. AUTO-EXIT FEATURE
# ====================================================
def should_exit_conversation(user_text):
    """Check if user wants to end the conversation"""
    exit_keywords = [
        # Goodbye words
        'bye', 'goodbye', 'see you', 'farewell', 'cya',
        # Exit words
        'exit', 'quit', 'stop', 'end', 'close', 'finish', 'enough',
        
    ]
    
    user_text_lower = user_text.lower()
    
    # Check if any exit keyword is in the user's text
    for keyword in exit_keywords:
        if keyword in user_text_lower:
            return True
    
    return False

def get_exit_response(user_text):
    """Get appropriate goodbye response based on what user said"""
    user_text_lower = user_text.lower()
    
    if any(word in user_text_lower for word in ['bye', 'goodbye', 'see you']):
        return "Goodbye! It was nice talking with you."
    elif any(word in user_text_lower for word in ['stop', 'exit', 'quit']):
        return "Okay, I'm stopping now. Feel free to talk anytime!"
    else:
        return "It was nice talking with you. I'm here whenever you need me!"


# ====================================================
# 6. MAIN CONVERSATION WITH AUTO-EXIT
# ====================================================
def start_conversation():
    # Test speech first
    print("Testing speech system...")
    speak("Hello! I am your emotional assistant. Can you hear me?")
    time.sleep(1)
    
    # Detect emotion
    emotion = detect_emotion()

    # Initial emotional response
    bot_reply = groq_chatbot(f"I am feeling {emotion}")
    speak(bot_reply)

    # Continuous chat with auto-exit
    while True:
        user_text = listen()

        # Check if user wants to exit
        if should_exit_conversation(user_text):
            exit_response = get_exit_response(user_text)
            speak(exit_response)
            break

        if user_text.strip() == "":
            speak("I'm here when you're ready to talk.")
            continue

        bot_reply = groq_chatbot(user_text)
        speak(bot_reply)
        
        # Also check if the AI's response suggests ending (like "you're welcome")
        if should_exit_conversation(bot_reply):
            break


# ====================================================
# START PROGRAM
# ====================================================
if __name__ == "__main__":
    try:
        start_conversation()
    except KeyboardInterrupt:
        speak("Goodbye! Take care.")
    except Exception as e:
        print(f"Error: {e}")
        speak("Something went wrong. Goodbye!")