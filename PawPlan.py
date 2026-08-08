import streamlit as st
from google import genai

st.set_page_config(page_title="PawPlan", page_icon="🐾")

st.title("PawPlan")
st.write("Generate a quick care routine tailored to your pet's age and weight.")

# Ensure API key is configured
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API key in st.secrets['GEMINI_API_KEY']")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

with st.form("pet_form"):
    pet_type = st.text_input("Pet Species / Breed", placeholder="e.g., Golden Retriever, Bearded Dragon")
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age (Years)", min_value=0.0, max_value=50.0, value=1.0, step=0.5)
    with col2:
        weight = st.number_input("Weight (Lbs)", min_value=0.1, max_value=500.0, value=10.0, step=0.5)

    submitted = st.form_submit_button("Generate Care Plan")

if submitted:
    if not pet_type.strip():
        st.warning("Please specify the type of pet.")
    else:
        with st.spinner("Building plan..."):
            prompt = f"""
            Act as a veterinarian. Build a realistic, practical daily care guide for:
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
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            st.subheader(f"Care Guide for {pet_type}")
            st.markdown(response.text)
