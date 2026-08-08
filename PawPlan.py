import streamlit as st
from google import genai
from google.genai import errors

st.set_page_config(page_title="PawPlan", page_icon="🐾")

st.title("PawPlan 🐾")
st.write("Generate a quick care routine tailored to your pet's age and weight, and ask follow-up questions.")

# Ensure API key is present in st.secrets
if "GEMINI_API_KEY" not in st.secrets:
    st.error(
        "Missing API key in st.secrets['GEMINI_API_KEY']. Please add it in Streamlit Cloud Settings -> Secrets."
    )
    st.stop()

# Initialize API Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# Form to input pet details
with st.form("pet_form"):
    pet_type = st.text_input(
        "Pet Species / Breed", placeholder="e.g., Golden Retriever, Bearded Dragon"
    )

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input(
            "Age (Years)", min_value=0.0, max_value=50.0, value=1.0, step=0.5
        )
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
