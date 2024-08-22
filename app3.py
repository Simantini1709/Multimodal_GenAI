import streamlit as st
st.set_page_config(page_title="Snap Travel Finder by SIM",layout="wide")
from dotenv import load_dotenv
import os
from PIL import Image
import google.generativeai as genai
from googletrans import Translator
from gtts import gTTS
import hmac



# Enable wide mode


def check_password():
    """Returns `True` if the user had a correct password."""
    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets["passwords"] and hmac.compare_digest(
            st.session_state["password"], st.secrets.passwords[st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False
    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True
    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("User not known or password incorrect⚠️")
        return False
 
if not check_password():
    st.stop()




# Load environment variables
load_dotenv()

# Configure the generative AI model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize session state
if 'budget_ideas' not in st.session_state:
    st.session_state.budget_ideas = []
if 'tour_budget' not in st.session_state:
    st.session_state.tour_budget = ""
if 'tour_time_window' not in st.session_state:
    st.session_state.tour_time_window = ""
if 'tour_preferred_location' not in st.session_state:
    st.session_state.tour_preferred_location = ""
if 'tour_type' not in st.session_state:
    st.session_state.tour_type = ""
if 'explanation_response' not in st.session_state:
    st.session_state.explanation_response = ""
if 'translated_response' not in st.session_state:
    st.session_state.translated_response = ""
if 'response1' not in st.session_state:
    st.session_state.response1 = ""
if 'selected_budgets' not in st.session_state:
    st.session_state.selected_budgets = ""

image_path=r'logo2.png'
image=Image.open(image_path)

st.sidebar.image(image,width=150)
# Sidebar with navigation buttons
page = st.sidebar.radio("Select a page", ["Discovery", "Recommendations", "Translation"])

def vision_model():
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    return model

def get_gemini_response1(img_content, prompt, model):
    response = model.generate_content([prompt, img_content])
    return response.text

def get_gemini_response2(response, prompt, model):
    response = model.generate_content([prompt, response])
    return response.text

# Streamlit app
st.header("Snap Travel Finder")

if page == "Discovery":
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    input_prompt1 = """
    You are an international tour expert. You had experience of international off beat places like Sea beaches, Hilly regions,
    cave regions, Forest. You can even identify all the features from the given image.

    Instruction:

    you have to explore the given picture for all available possibilities
    You must identify the possible location of the given pictures
    You also need to identify the weather and geographical elements from the given picture
    You must identify the altitude and other natural constraints from the shared picture
    you need to explore each pixel of the picture and identify the relevant features

Example:
    Imagine we have an image of a pristine beach with vivid turquoise waters, surrounded by dramatic green cliffs, under a clear blue sky. In the foreground, there's soft, white sand and gently lapping waves. The background features a dense tropical forest cascading down the cliffs, with hints of wildlife visible.

    Expected Features:
        1. Possible Location:

            The unique combination of vibrant turquoise waters and lush green cliffs is indicative of tropical or subtropical regions renowned for their natural beauty. Possible locations include:
                Thailand: The Phi Phi Islands, known for their stunning beaches and lush cliffs.
                Hawaii: The Napali Coast, famous for its dramatic cliffs and pristine waters.
                Caribbean: The Virgin Islands, celebrated for their clear waters and tropical scenery.
        2. Weather and Geographical Elements:

            The clear, cloudless sky indicates a day of bright, sunny weather, typical of tropical climates.
            The lush, green vegetation suggests the region receives ample rainfall, supporting a diverse ecosystem.
            The vivid turquoise water implies shallow, clear seas often found in areas with coral reefs or sandy seabeds.

        3. Altitude and Natural Constraints:

            The cliffs appear to rise steeply from the beach but are of moderate height, likely ranging from 30 to 100 meters.
            The lack of visible pathways suggests that access to this beach might be limited to boats or hiking trails.
            There are no signs of high altitude or mountainous terrain, indicating a coastal region at sea level or slightly above.

        4. Other Natural Features:

            The beach is composed of fine, powdery white sand, typical of tropical island beaches.
            Vegetation includes tropical plants, such as palm trees and dense undergrowth, hinting at a rich and varied flora.
            The area is likely a haven for marine life, with clear waters supporting coral reefs, colorful fish, and possibly sea turtles.
            Wildlife sightings, such as birds or small mammals, can be inferred from the dense forest and untouched landscape.

    Example:

            "In this tropical paradise, a pristine beach meets vivid turquoise waters, framed by dramatic green cliffs and a clear blue sky. The soft, white sand invites relaxation, while gentle waves lap at the shore. This idyllic scene, reminiscent of Thailand's Phi Phi Islands, Hawaii's Napali Coast, or the Caribbean Virgin Islands, showcases a region rich in natural beauty and biodiversity. The lush tropical forest cascading down the cliffs and hints of wildlife reflect the area's high rainfall and thriving ecosystem. The moderate altitude of the cliffs and the absence of visible access paths suggest that this secluded spot is best reached by boat or an adventurous hike. A sanctuary for marine life, the clear waters likely teem with coral reefs and colorful fish, making it a dream destination for nature lovers and explorers alike."

    Expected Outcome:
            Your task is to generate a caption related to the qualitative features of the image given below.
            Generate a comprehensive headings based upon the image. Use individuals lines with bullet points
            describing key features of the image.
            
    """

    model = vision_model()

    if uploaded_file is not None:
        st.write("Image Uploaded Successfully")
        if st.button("Submit"):
            image = Image.open(uploaded_file)
            response1 = get_gemini_response1(image, input_prompt1, model)
            st.session_state.response1 = response1
            st.session_state.budget_ideas = response1.split("\n")

            st.image(image, caption="Uploaded Image", use_column_width=True)

            # Display the generated Travel Packages
            for i in st.session_state.budget_ideas:
                st.write(i)

elif page == "Recommendations":
    if not st.session_state.response1:
        st.warning("Please upload an image and proceed with the next page options.")
    else:
        if st.session_state.response1:
            st.session_state.tour_budget = st.text_input("Enter Tour Budget:", st.session_state.tour_budget)
            st.session_state.tour_time_window = st.text_input("Enter Tour Time Window:", st.session_state.tour_time_window)
            st.session_state.tour_preferred_location = st.text_input("Enter Tour Preferred Location:", st.session_state.tour_preferred_location)
            st.session_state.tour_type = st.selectbox("Select Tour Type:", ["Adventure", "Relaxation", "Cultural", "Nature", "City Tour"], index=["Adventure", "Relaxation", "Cultural", "Nature", "City Tour"].index(st.session_state.tour_type) if st.session_state.tour_type else 0)
        
            model = vision_model()
            st.write("Information loaded Successfully")
            if st.button("Submit"):
                input_prompt2 = f"""
                                    You are a comprehensive Trip Advisor for travelers. Your task is to create detailed and personalized travel packages based on the specified parameters,
                                    Generate only top 5 travel packages {st.session_state.response1} by using {st.session_state.tour_budget} using {st.session_state.tour_time_window} and {st.session_state.tour_preferred_location} with a focus on {st.session_state.tour_type}.
                                    Generate response2 suitable for splitting.

                                    Write only each package in maximum 10 words; don't exceed the limit.

                                    The output will be only the travel packages in this format:

                                    Example output:

                                    1.Island Hopping by Speedboat: Snorkel reefs, hidden beaches, local life.
                                    2.Dive into Adventure: PADI Course, manta rays, bioluminescent plankton tour.
                                    3.Surf's Up Maldives: Private lessons, secret breaks, luxury surf camp vibes.
                                    4.Robinson Crusoe Escape: Remote eco-lodge, kayaking, stargazing, pure nature.
                                    5.Thrill-Seeker's Paradise: Flyboarding, parasailing, jet ski safaris, underwater scooter.
                                """

                response2 = get_gemini_response2(st.session_state.response1, input_prompt2, model)
                st.session_state.budget_ideas = response2.split("\n")

                # Display the generated Travel Packages
                for i in st.session_state.budget_ideas:
                    st.write(i)

        selected_budgets = st.selectbox("Select a Package Option for detailed plan:", [""] + st.session_state.budget_ideas, key="selected_budgets")
        if st.button("Generate Detailed Plan"):
            if selected_budgets:
                # Generate detailed explanation for the selected travel package
                explanation_prompt = f"""You are a comprehensive Trip Advisor for travelers. 
                Your task is to create a detailed itinerary for the selected budget package
                and personalized travel plan based on the specified parameters.
                Generate a full detailed itinerary plan for the
                selected package {selected_budgets} 
                by using {st.session_state.tour_budget}, the time window of {st.session_state.tour_time_window}, and {st.session_state.tour_preferred_location} 
                with a focus on {st.session_state.tour_type}. You must not mention any headings in Bold. And also don't 
                use asterix anywhere
                You must mention top five accomodation hotels along with there key features
                Also mention most conveinient transport routes from nearby railway or bus stand
                along with approximate distance."""

                explanation_response = model.generate_content(explanation_prompt)
                st.session_state.explanation_response = explanation_response.text
                # Display the detailed explanation
                st.write(explanation_response.text)
        else:
            st.warning("Please select a travel package first.")


            

elif page == "Translation":
    if not st.session_state.response1:
        st.warning("Please upload an image and proceed with the next page options.")
    else:
        st.header("Translate the Output in your preferred langugae ")

        target_language = st.text_input("Enter target language (e.g., 'fr' for French, 'es' for Spanish):")

        if st.button("Translate"):
            translator = Translator()
            if st.session_state.explanation_response:
                try:
                    translation = translator.translate(st.session_state.explanation_response, dest=target_language)
                    cleaned_translation = translation.text.replace("*", "").strip()
                    st.session_state.translated_response = cleaned_translation
                    st.write("Translated Output:")
                    st.write(st.session_state.translated_response)
                except Exception as e:
                    st.error(f"Translation failed: {e}")
            else:
                st.warning("Please generate a detailed plan first.")

        st.header("Text-to-Speech")

        if st.button("Generate Voice"):
            if st.session_state.translated_response:
                tts = gTTS(st.session_state.translated_response, lang=target_language)
                tts.save('output.mp3')
                st.audio('output.mp3', format='audio/mp3')

                with open('output.mp3', 'rb') as file:
                    btn = st.download_button(
                        label="Download audio",
                        data=file,
                        file_name='output.mp3',
                        mime='audio/mp3'
                    )
            else:
                st.warning("Please translate the text first.")
