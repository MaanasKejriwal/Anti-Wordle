import streamlit as st
import random

# Function to read the words from a text file
def get_valid_words():
    """Retrieve a list of valid 5-letter words from a file."""
    with open("words.txt", "r") as file:
        all_words = file.read().splitlines()  # Read all words and split by lines
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
    st.session_state.gave_up = False  # Track if the player gave up
    st.session_state.keyboard_colors = {chr(i): 'green' for i in range(97, 123)}  # Initialize keyboard colors

# Initialize session state variables if not already set
if 'hidden_word' not in st.session_state:
    initialize_game()

# Function to check the guess and provide feedback
def check_guess(guess):
    feedback = []
    hidden_word = st.session_state.hidden_word
    print(hidden_word)
    
    # Convert hidden_word to a list to mark letters as used
    hidden_word_list = list(hidden_word)
    
    # First pass: Check for red letters (correct position)
    for i, letter in enumerate(guess):
        if letter == hidden_word_list[i]:
            feedback.append(('#ad0e19', letter))  # Correct position (red)
            hidden_word_list[i] = None  # Mark this position as used
            st.session_state.red_positions[i] = letter  # Track the position of red letters
            st.session_state.keyboard_colors[letter] = '#ad0e19'  # Update keyboard color to red
        else:
            feedback.append(('gray', letter))  # Placeholder for other colors
            
    # Second pass: Check for yellow letters (correct letter, wrong position)
    for i, (color, letter) in enumerate(feedback):
        if color != '#ad0e19':  # Only check non-red letters
            if letter in hidden_word_list:
                feedback[i] = ('#f0b51f', letter)  # Correct letter, wrong position (yellow)
                hidden_word_list[hidden_word_list.index(letter)] = None  # Mark this letter as used
                st.session_state.yellow_letters.add(letter)  # Add yellow letters to the set
                st.session_state.keyboard_colors[letter] = '#f0b51f'  # Update keyboard color to yellow
            elif letter not in hidden_word:
                st.session_state.grey_letters.add(letter)  # Add grey letters to the set
                st.session_state.keyboard_colors[letter] = 'gray'  # Update keyboard color to grey
    
    return feedback

# Function to validate the guess based on the rules
def is_valid_guess(guess):
    """Check if the guess contains all required yellow letters, no grey letters, and red letters are in the correct position."""
    contains_yellow_letters = all(letter in guess for letter in st.session_state.yellow_letters)
    does_not_contain_grey_letters = all(letter not in guess for letter in st.session_state.grey_letters)
    red_positions_correct = all(guess[i] == letter for i, letter in st.session_state.red_positions.items())
    
    return contains_yellow_letters and does_not_contain_grey_letters and red_positions_correct

# Function to display the guess with colored boxes
def display_guess(feedback):
    """Display the guess with colored boxes, ensuring that the order of letters is preserved."""
    guess_html = "<div style='display: flex; justify-content: center;'>"
    for color, letter in feedback:
        guess_html += f"<div style='width: 60px; height: 60px; background-color: {color}; color: white; display: flex; justify-content: center; align-items: center; margin: 5px; font-size: 32px;'>{letter.upper()}</div>"
    guess_html += "</div>"
    st.markdown(guess_html, unsafe_allow_html=True)

# Sidebar for instructions
with st.sidebar:
    st.header("How to Play")
    st.write("""
        **Objective:** Avoid guessing the hidden 5-letter word, maximizing the valid words you can guess.

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
        - You have 5 guesses to avoid finding the hidden word.
    """)

st.markdown("<h1 style='text-align: center; color: white; font-family: 'EB Garamond', serif; font-size: 24px;'>Anti-Wordle</h1>", unsafe_allow_html=True)

# Form for input
if not st.session_state.game_over:  # Disable form if the game is over
    with st.form(key='guess_form'):
        st.markdown("<h4 style='text-align: center; color: white; font-family: 'EB Garamond', serif; font-size: 24px;'>Enter your guess:</h4>", unsafe_allow_html=True)
        guess_input = st.text_input('', value=st.session_state.temp_guess_input).lower()
        submit_button = st.form_submit_button(label='Submit Guess')

        if submit_button:
            if len(guess_input) != 5:
                st.warning("Your guess must be a 5-letter word.")
            elif guess_input not in get_valid_words():
                st.warning("The word you entered is not in the list of valid words.")
            else:
                guess = guess_input
                
                if is_valid_guess(guess):
                    st.session_state.guesses.append(guess)
                    st.session_state.used_letters.update(guess)
                    feedback = check_guess(guess)

                    # Check if the guess is the hidden word
                    if guess == st.session_state.hidden_word:
                        st.session_state.game_over = True  # Set game over flag to True
                        st.session_state.temp_guess_input = ''  # Clear the input field
                    elif len(st.session_state.guesses) >= 5:
                        st.session_state.game_over = True  # End the game after 5 guesses
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

# Display on-screen keyboard with clickable buttons in QWERTY layout
st.markdown("<h4 style='text-align: center; color: white;'>Available Letters (Word Map):</h4>", unsafe_allow_html=True)
st.markdown("<h6 style='text-align: center; color: white;'>Please use this only as an indication, it is not a keyboard.</h6>", unsafe_allow_html=True)
keyboard_layout = [
    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
    ['z', 'x', 'c', 'v', 'b', 'n', 'm']
]

# Function to display the on-screen keyboard with a responsive layout
def display_keyboard():
    keyboard_layout = [
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
        ['z', 'x', 'c', 'v', 'b', 'n', 'm']
    ]
    keyboard_html = "<div style='display: flex; flex-direction: column; align-items: center;'>"
    for row in keyboard_layout:
        keyboard_html += "<div style='display: flex;'>"
        for letter in row:
            color = st.session_state.keyboard_colors.get(letter, 'green')  # Get the color for the letter
            keyboard_html += f"<div style='width: 40px; height: 40px; background-color: {color}; color: white; display: flex; justify-content: center; align-items: center; margin: 5px; border-radius: 5px;'>{letter.upper()}</div>"
        keyboard_html += "</div>"
    keyboard_html += "</div>"
    st.markdown(keyboard_html, unsafe_allow_html=True)

display_keyboard()

# Display a "Give Up" button if the game is not over
if not st.session_state.game_over:
    if st.button("Give Up"):
        st.session_state.gave_up = True  # Track that the player gave up
        st.session_state.game_over = True  # End the game

# Display the game over screen if the game is over
if st.session_state.game_over:
    if st.session_state.gave_up:
        st.markdown(f"<h3 style='text-align: center; color: white;'>You gave up after {len(st.session_state.guesses)} guesses!</h3>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: white;'>The hidden word was: {st.session_state.hidden_word.upper()}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center; color: white;'>Game Over</h3>", unsafe_allow_html=True)
        if st.session_state.guesses[-1] == st.session_state.hidden_word:
            st.markdown(f"<h3 style='text-align: center; color: white;'>Score: {len(st.session_state.guesses)}</h5>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; color: white;'>You found the hidden word after {len(st.session_state.guesses)} guesses!</h3>", unsafe_allow_html=True)
        else:
            st.balloons()
            st.markdown(f"<h3 style='text-align: center; color: white;'>Score: {len(st.session_state.guesses)}</h5>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: center; color: white;'>Congratulations! You successfully avoided the hidden word.</h5>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center; color: white;'>The hidden word was: {st.session_state.hidden_word.upper()}</h4>", unsafe_allow_html=True)


    if st.button("Restart Game"):
        initialize_game()
