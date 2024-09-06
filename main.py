import streamlit as st
import random
import nltk
from nltk.corpus import words
from PyDictionary import PyDictionary

# Download the words corpus
nltk.download('words')

# Initialize PyDictionary
dictionary = PyDictionary()

# Get a list of valid 5-letter words
def get_valid_words():
    """Retrieve a list of valid 5-letter words."""
    all_words = words.words()
    return [word.lower() for word in all_words if len(word) == 5]

# Function to initialize or reset the game
def initialize_game():
    """Initialize or reset all session state variables for a new game."""
    st.session_state.hidden_word = random.choice(get_valid_words())
    st.session_state.guesses = []
    st.session_state.used_letters = set()
    st.session_state.yellow_letters = set()
    st.session_state.grey_letters = set()
    st.session_state.red_positions = {}
    st.session_state.game_over = False  # Flag to indicate if the game is over
    st.session_state.temp_guess_input = ''  # Clear the guess input

# Initialize session state variables if not already set
if 'hidden_word' not in st.session_state:
    initialize_game()

# Game mechanics
def check_guess(guess):
    feedback = []
    hidden_word = st.session_state.hidden_word
    print(hidden_word)
    
    for i, letter in enumerate(guess):
        if letter == hidden_word[i]:
            feedback.append(('#ad0e19', letter))  # Correct position (red)
            st.session_state.red_positions[i] = letter  # Track the position of red letters
        elif letter in hidden_word:
            feedback.append(('#f0b51f', letter))  # Correct letter, wrong position (yellow)
            st.session_state.yellow_letters.add(letter)  # Add yellow letters to the set
        else:
            feedback.append(('gray', letter))  # Incorrect letter (grey)
            st.session_state.grey_letters.add(letter)  # Add grey letters to the set
    
    return feedback

def is_valid_guess(guess):
    """Check if the guess contains all required yellow letters, no grey letters, and red letters are in the correct position."""
    contains_yellow_letters = all(letter in guess for letter in st.session_state.yellow_letters)
    does_not_contain_grey_letters = all(letter not in guess for letter in st.session_state.grey_letters)
    red_positions_correct = all(guess[i] == letter for i, letter in st.session_state.red_positions.items())
    
    return contains_yellow_letters and does_not_contain_grey_letters and red_positions_correct

def display_guess(feedback):
    """Display the guess with colored boxes like Wordle, but with larger boxes."""
    guess_html = "<div style='display: flex; justify-content: center;'>"
    for color, letter in feedback:
        guess_html += f"<div style='width: 60px; height: 60px; background-color: {color}; color: white; display: flex; justify-content: center; align-items: center; margin: 5px; font-size: 32px;'>{letter.upper()}</div>"
    guess_html += "</div>"
    st.markdown(guess_html, unsafe_allow_html=True)

# Sidebar for instructions
with st.sidebar:
    st.header("How to Play")
    st.write("""
        **Objective:** Avoid guessing the hidden 5-letter word, maxmising the valid words you can guess.

        **Instructions:**
        1. Enter your 5-letter guess in the text box.
        2. Click 'Submit Guess' to check your guess.
        3. Letters in the correct position will be highlighted in red.
        4. Letters that are correct but in the wrong position will be highlighted in yellow.
        5. Incorrect letters will be highlighted in grey.
        6. You cannot use a greyed letter once it has been identified.

        **Rules:**
        - You must use all required yellow letters in each guess.
        - You cannot use greyed letters once they have been discovered.
        - Once you have discovered a red letter, it must remain in the correct position.
    """)

st.markdown("<h1 style='text-align: center; color: white; font-family: 'EB Garamond', serif; font-size: 24px;'>Anti-Wordle</h1>", unsafe_allow_html=True)


# Form for input
with st.form(key='guess_form'):
    st.markdown("<h4 style='text-align: center; color: white; font-family: 'EB Garamond', serif; font-size: 24px;'>Enter your guess:</h4>", unsafe_allow_html=True)
    guess_input = st.text_input('', value=st.session_state.temp_guess_input).lower()
    submit_button = st.form_submit_button(label='Submit Guess')

    if submit_button:
        if guess_input:
            guess = guess_input
            
            if len(guess) == 5 and guess in get_valid_words():
                if is_valid_guess(guess):
                    st.session_state.guesses.append(guess)
                    st.session_state.used_letters.update(guess)
                    feedback = check_guess(guess)

                    # Check if the guess is the hidden word
                    if guess == st.session_state.hidden_word:
                        st.session_state.game_over = True  # Set game over flag to True
                        st.session_state.temp_guess_input = ''  # Clear the input field
                        st.balloons()  # Optional: Display balloons as a celebration
                    else:
                        # Clear the input field
                        st.session_state.temp_guess_input = ''
                else:
                    missing_yellow = [letter for letter in st.session_state.yellow_letters if letter not in guess]
                    used_grey = [letter for letter in guess if letter in st.session_state.grey_letters]
                    incorrect_red_positions = [i for i, letter in st.session_state.red_positions.items() if guess[i] != letter]
                    
                    warning_message = ""
                    if missing_yellow:
                        warning_message += f"You must include these letters: {', '.join(missing_yellow)}. "
                    if used_grey:
                        warning_message += f"You cannot use these letters: {', '.join(used_grey)}. "
                    if incorrect_red_positions:
                        warning_message += f"The red letters must be in the correct positions: {', '.join([str(i + 1) for i in incorrect_red_positions])}."
                    
                    st.warning(warning_message)

# Display previous guesses
if st.session_state.guesses:
    for guess in st.session_state.guesses:
        feedback = check_guess(guess)
        display_guess(feedback)

# Display available letters
available_letters = [chr(i) for i in range(97, 123) if chr(i) not in st.session_state.used_letters and chr(i) not in st.session_state.grey_letters]

# Button to restart the game if the game is over
if st.session_state.game_over:
    if st.button("Restart Game"):
        initialize_game()
        st.experimental_rerun()  # Trigger a rerun to clear previous guesses and input

    # Display "Game Over" message
    st.markdown("<h2 style='text-align: center; color: white;'>Game Over!</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: white;'>You were able to maximize your guesses to: {}</h4>".format(len(st.session_state.guesses)), unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: white;'>The word was: '{}' </h4>".format(st.session_state.hidden_word), unsafe_allow_html=True)

    # Fetch and display the word definition
    # definition = dictionary.meaning(st.session_state.hidden_word)
    # if definition:
    #     phonetic = dictionary.get_phonetic(st.session_state.hidden_word)
    #     st.markdown(f"<h3 style='text-align: center; color: white;'>Definition:</h3>", unsafe_allow_html=True)
    #     st.markdown(f"<p style='text-align: center; color: white; font-style: italic;'>{phonetic}</p>", unsafe_allow_html=True)
    #     for part_of_speech, meanings in definition.items():
    #         st.markdown(f"<h4 style='text-align: center; color: white;'>{part_of_speech.capitalize()}:</h4>", unsafe_allow_html=True)
    #         for meaning in meanings:
    #             st.markdown(f"<p style='text-align: center; color: white;'>{meaning}</p>", unsafe_allow_html=True)
    # else:
    #     st.markdown("<p style='text-align: center; color: white;'>No definition found.</p>", unsafe_allow_html=True)
