import chainlit as cl
from itertools import zip_longest
from groq import Groq
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
import os
import toml
import asyncio
import time
import random
import re

# Load secrets from secrets.toml (for local development)
def load_secrets():
    secrets_path = ".streamlit/secrets.toml"
    if os.path.exists(secrets_path):
        with open(secrets_path, "r") as f:
            return toml.load(f)
    return {}

# Get Groq API key from secrets.toml or environment
secrets = load_secrets()
groq_api_key = secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in secrets.toml or environment variables")

client = Groq(api_key=groq_api_key)

# System prompt with important words bolded
SYSTEM_PROMPT = """System:
Tum "Punjab College Nowshera Virkan Reception Bot" ho. 
Tumhara role ek **professional receptionist** ka hai jo hamesha visitor ya student ko **roman urdu** mein friendly, clear aur informative jawab deta hai. 
Tum kabhi "mujhe nahi pata" nahi bologe. Agar specific info na mile to tum general Punjab College ki authentic aur helpful information provide karoge.  

───────────────────────────────
🔹 **Punjab Group of Colleges (PGC) – Overview**  
- PGC Pakistan ka sabse bara private educational network hai (established 1985).  
- **Programs Offered**:  
  – Intermediate: **F.Sc Pre-Medical**, **F.Sc Pre-Engineering**, **ICS**, **I.Com**, **F.A (IT)**  
  – Graduate: **BA**, **B.Sc**, **B.Com**  
  – BS Programs  
- **Scholarships**: Merit-based, need-based, kinship aur orphan students ke liye (up to 100%).  
- **Facilities**: Modern labs, library, auditorium, transport, hostel, sports grounds.  
- **Head Office Contact**:  
  – Toll-free: 0800-78608  
  – WhatsApp: 0311-1786522  
  – Website: https://pgc.edu  

───────────────────────────────
🔹 **Punjab College Nowshera Virkan Campus**  
- **Location**: Nokhar Road, Nowshera Virkan.  
- **Admissions (2025–26)**:  
  – F.Sc (Pre-Medical / Pre-Engineering)  
  – ICS (Computer Science)  
  – I.Com (Commerce)  
  – F.A (General Group / IT)  
- **Scholarships**: Merit-based (up to 100% waiver), kinship discount, orphan support, need-based aid.  
- **Special Offer**: 50% discount on 2nd shift admissions (limited dates).  
- **Pre-1st Year Classes**: Started from 28 April 2025.  
- **Extracurriculars**: Tours, seminars, competitions, sports, student festivals.  
- **Campus Contact**: 0303-419-2000 | 0303-419-3000  

───────────────────────────────
🔹 **Campus Authority**  
- **Principal**: Sir **Ali Toor**  
- **Vice Principal**: Miss **Andleeb** (Statistics faculty for ICS students)  

───────────────────────────────
🔹 **Leave Policy**  
- Agar student chutti lena chahta hai to usay **college ki shop se Leave Performa** lena hoga.  
- Form par student ka **name, phone number, father ka name** likhna hoga.  
- Leave valid hone ke liye student ko apne **incharge ka signature** bhi lena zaroori hai.  

───────────────────────────────
🔹 **Chatbot Development Credit**  
Ye Reception Bot develop kiya gaya hai **Musab Bhai** aur **Sohail Bhai** ke zariye.  

───────────────────────────────
🔹 **Frequently Asked Questions (FAQs)**  

1) **Fee Structure**  
   – Program par depend karti hai (F.Sc, ICS, I.Com, F.A).  
   – General estimate: **6,000 – 10,000 PKR per month** (scholarship/discount ke baad kam ho sakti hai).  

2) **Scholarship Criteria**  
   – Matric me A+ aur A grade walon ke liye high merit scholarships.  
   – **Kinship**, **need-based** aur **orphan** support available.  

3) **Campus Timings**  
   – Morning Shift: 8:00 AM – 1:00 PM  
   – 2nd Shift: 1:30 PM – 5:30 PM  

4) **Hostel Facility**  
   – Boys aur girls ke liye safe aur secure hostel accommodation.  

5) **Transport Facility**  
   – College ki buses aur vans Nowshera Virkan aur nearby towns cover karti hain.  

───────────────────────────────
🔹 **Response Guidelines**  
- Har visitor ke question ka relevant jawab do.  
- Har baat par contact number repeat mat karo, sirf zarurat ho tab.  
- Agar user short info chahta ho to concise jawab do, agar detail chahta ho to detailed explanation do.  
- Tone hamesha **professional, respectful aur friendly** honi chahiye.  
- Kabhi "mujhe nahi pata" na bolo – hamesha **helpful aur positive** jawab dena hai.  

🎯 **Objective**: Har visitor ko aisa feel ho ke woh asli Punjab College Nowshera Virkan ke receptionist se baat kar raha hai.  

 """


@cl.on_chat_start
async def on_chat_start():
    # Initialize session history
    cl.user_session.set("history", [])
    
    # Welcome message with typing effect
    welcome_msg = "😊 Hello! I'm PGC Reception Bot. How can I help you today?"
    await type_effect(welcome_msg)


async def type_effect(text, delay=0.02):
    """
    Function to create typing effect for messages
    """
    # Add header to every response
    header = "🤖 PGC Reception Bot Nowshera Virkan Campus\n\n"
    full_message = header + text
    
    message = cl.Message(content="")
    await message.send()
    
    # Type out the header quickly
    for char in header:
        message.content += char
        await message.update()
        time.sleep(0.01)  # Faster typing for header
    
    # Type out the main content with normal speed
    for char in text:
        message.content += char
        await message.update()
        time.sleep(delay)
    
    return message


def add_emojis_to_response(response):
    """
    Add relevant emojis to the response based on content and length
    """
    # Define emoji categories with more specific emojis
    education_emojis = ["📚", "🎓", "🏫", "📝", "✏️", "🔬", "🧪", "🧮", "📊", "📖", "🎒"]
    positive_emojis = ["😊", "👍", "🌟", "✅", "🎉", "👏", "🙌", "🤝", "💯", "🥇"]
    contact_emojis = ["📞", "📱", "📧", "🌐", "📍", "🗺️", "👤", "📠"]
    time_emojis = ["⏰", "🕐", "🕒", "📅", "🗓️", "⌛", "⏳"]
    money_emojis = ["💵", "💰", "💲", "🎁", "🪙", "💸", "🏦"]  # Added 💸 for fees
    subject_emojis = {
        "physics": "⚛️", "chemistry": "🧪", "biology": "🧬", "math": "🧮", 
        "computer": "💻", "english": "🔤", "urdu": "📜", "islamiyat": "☪️",
        "pak studies": "🇵🇰", "accounting": "📊", "commerce": "📈"
    }
    
    # Count words to determine how many emojis to add
    word_count = len(response.split())
    emoji_count = min(6, max(1, word_count // 20))  # 1 emoji per 20 words, max 6
    
    # Find relevant emojis based on content
    relevant_emojis = []
    
    # Check for specific topics in the response
    response_lower = response.lower()
    
    # Education-related topics
    if any(word in response_lower for word in ["admission", "apply", "enroll", "course", "program", "study", "learn"]):
        relevant_emojis.extend(education_emojis)
    
    # Contact information
    if any(word in response_lower for word in ["contact", "call", "phone", "number", "email", "address", "location"]):
        relevant_emojis.extend(contact_emojis)
    
    # Timing information
    if any(word in response_lower for word in ["time", "schedule", "hour", "shift", "morning", "evening", "class timing"]):
        relevant_emojis.extend(time_emojis)
    
    # Financial topics
    if any(word in response_lower for word in ["fee", "price", "cost", "payment", "scholarship", "discount", "money", "paid"]):
        relevant_emojis.extend(money_emojis)
    
    # Subject-specific emojis
    for subject, emoji in subject_emojis.items():
        if subject in response_lower:
            relevant_emojis.append(emoji)
    
    # Always add some positive emojis
    relevant_emojis.extend(positive_emojis)
    
    # Remove duplicates
    relevant_emojis = list(set(relevant_emojis))
    
    # If no relevant emojis found, use a default set
    if not relevant_emojis:
        relevant_emojis = education_emojis + positive_emojis
    
    # Select random emojis from the relevant list
    selected_emojis = random.sample(relevant_emojis, min(emoji_count, len(relevant_emojis)))
    
    # Add emojis to the response (at the beginning and end)
    if selected_emojis:
        # Add first emoji at the beginning
        response = selected_emojis[0] + " " + response
        
        # Add remaining emojis at the end
        if len(selected_emojis) > 1:
            response += " " + " ".join(selected_emojis[1:])
    
    return response


def format_important_words(response):
    """
    Format important words in the response to make them bold
    """
    # List of important words to bold (case insensitive)
    important_words = [
        "admission", "scholarship", "fee", "contact", "program", "course",
        "facility", "hostel", "transport", "timing", "schedule", "discount",
        "location", "website", "whatsapp", "toll-free", "number", "price",
        "cost", "payment", "financial aid", "merit-based", "need-based",
        "extracurricular", "tour", "competition", "seminar", "sport", "event",
        "F.Sc", "ICS", "I.Com", "F.A", "Pre-Medical", "Pre-Engineering",
        "Computer Science", "Commerce", "General Group", "BS Programs",
        "Intermediate", "Graduate", "lab", "library", "auditorium", "ground"
    ]
    
    # Create a regex pattern to match these words (case insensitive)
    pattern = re.compile(r'\b(' + '|'.join(important_words) + r')\b', re.IGNORECASE)
    
    # Replace matches with bold version
    formatted_response = pattern.sub(r'**\1**', response)
    
    return formatted_response


def build_message_list(user_input):
    history = cl.user_session.get("history")
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    for human, ai in zip_longest(history[::2], history[1::2]):
        if human:
            messages.append(HumanMessage(content=human))
        if ai:
            messages.append(AIMessage(content=ai))

    messages.append(HumanMessage(content=user_input))
    return messages


def generate_response(messages):
    groq_messages = []
    for msg in messages:
        if isinstance(msg, SystemMessage):
            groq_messages.append({"role": "system", "content": msg.content})
        elif isinstance(msg, HumanMessage):
            groq_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            groq_messages.append({"role": "assistant", "content": msg.content})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=groq_messages,
        max_tokens=20000,
        temperature=0.5
    )
    return response.choices[0].message.content


@cl.on_message
async def main(message: cl.Message):
    user_input = message.content
    messages = build_message_list(user_input)
    bot_response = generate_response(messages)

    # Format important words to make them bold
    formatted_response = format_important_words(bot_response)
    
    # Add relevant emojis to the response
    bot_response_with_emojis = add_emojis_to_response(formatted_response)

    # Save to history
    history = cl.user_session.get("history")
    history.append(user_input)
    history.append(bot_response)  # Save original response without formatting
    cl.user_session.set("history", history)

    # Send response with typing effect and header
    await type_effect(bot_response_with_emojis)
    if __name__ == "__main__":
        PORT = int(os.environ.get("PORT", 8000))
    cl.run(app, host="0.0.0.0", port=PORT)
        
    
      
