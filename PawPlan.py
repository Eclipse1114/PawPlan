import streamlit as st
from google import genai
from PIL import Image

# Page configuration
st.set_page_config(page_title="PawPlan", page_icon="🐾", layout="centered")

st.title("🐾 PawPlan")
st.write("Get a custom, expert care guide for your pet in seconds!")

# Initialize session state for conversation history and keeping the plan visible
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "plan_generated" not in st.session_state:
    st.session_state.plan_generated = False

# Create a form for user inputs
with st.form("pet_form"):
    pet_type = st.text_input("What kind of pet do you have?", placeholder="e.g., Golden Retriever, Ball Python, Tabby Cat")
    age = st.number_input("How old are they in years?", min_value=0.0, max_value=50.0, value=1.0, step=0.5)
    weight = st.number_input("How much do they weigh (in lbs)?", min_value=0.1, max_value=500.0, value=10.0)
    
    # Added image upload option
    pet_image = st.file_uploader("Upload a photo (optional)", type=["jpg", "jpeg", "png"])
    
    submitted = st.form_submit_button("Generate Care Plan")

if submitted:
    if not pet_type.strip():
        st.warning("Please enter a valid pet type!")
    else:
        with st.spinner("Generating your custom PawPlan... 🐾"):
            # Initialize the Gemini client using the secret key hosted safely on the cloud
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            
            prompt = f"""
            You are an expert Veterinarian. Give a clear, concise, and structured plan for taking care of a pet using the following details.

            Pet weight: {weight} lbs
            Animal type: {pet_type}
            Age: {age} years old

            Give as many details as possible on:
            - Daily food and water portions.
            - Recommended daily exercise and playtime.
            - Suggested stores to buy supplies (e.g., local pet stores, Petco, Chewy, Walmart).
            
            Keep the tone warm, helpful, and professional. Add a brief medical disclaimer at the end.
            """
            
            # Bundle prompt and optional image for multimodal input
            contents = [prompt]
            if pet_image is not None:
                contents.append(Image.open(pet_image))
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
            )
            
            # Store initial response in session state
            st.session_state.chat_history = [{"role": "model", "text": response.text}]
            st.session_state.plan_generated = True

# Display plan and allow follow-up chat if generated
if st.session_state.plan_generated:
    st.success("Here is your custom plan!")
    
    # Render chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["text"])

    # Follow-up question input
    if user_question := st.chat_input("Ask a follow-up question about the plan..."):
        st.session_state.chat_history.append({"role": "user", "text": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)
            
        with st.spinner("Thinking..."):
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            
            # Build simple context from past messages
            context = "\n".join([f"{m['role']}: {m['text']}" for m in st.session_state.chat_history])
            followup_prompt = f"You are an expert Veterinarian continuing this consultation:\n{context}\n\nAnswer the user's latest question concisely."
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=followup_prompt,
            )
            
            reply = response.text
            st.session_state.chat_history.append({"role": "model", "text": reply})
            with st.chat_message("model"):
                st.markdown(reply)        )
    with col2:
        weight = st.number_input(
            "Weight (Lbs)", min_value=0.1, max_value=500.0, value=10.0, step=0.5
        )

    submitted = st.form_submit_button("Generate Care Plan")

# Reset memory and start a fresh plan when form is submitted
if submitted:
    if not pet_type.strip():
        st.warning("Please specify the type of pet.")
    else:
        # Clear previous session data automatically when searching a new plan
        st.session_state.messages = []
        
        # Start a fresh chat session with instructions
        st.session_state.chat_session = client.chats.create(
            model="gemini-3.5-flash",
            config={
                "system_instruction": "Act as a veterinarian providing practical pet care advice. Keep answers helpful and concise."
            }
        )

        prompt = f"""
        Build a realistic, practical daily care guide for:
        - Pet: {pet_type}
        - Weight: {weight} lbs
        - Age: {age} years

        Cover these areas briefly using markdown headers:
        1. Daily Food & Water Portions
        2. Recommended Exercise / Activity
        3. Essential Supplies
        4. Common Breed / Species Health Considerations

        End with a short medical disclaimer.
        """

        with st.spinner("Building plan..."):
            try:
                response = st.session_state.chat_session.send_message(prompt)
                
                # Save initial plan as first message
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            except errors.APIError as e:
                st.error(f"Gemini API Error: {e.message}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

            for message in st.session_state.messages:
                st.markdown(message["content"])
