"""
Legal Case Predictor

This script loads legal cases from from a text file and finds the top N most similar cases
to a given input case based on word matching. It then generates a prompt for OpenAI's 
language model to suggest next steps and possible verdict for the given case.

"""

# --------- Configuration ----------
import openai
import sys

OPENAI_API_KEY = "YOUR_API_KEY_HERE" # OpenAI API key 

CASES_FILENAME = "cases.txt" # Path to the text file containing legal cases

TOP_N = 3 # Number of top top similar cases to retrieve

# Weights for calculating similarity score
SUBJECT_WEIGHT = 5
DESCRIPTION_WEIGHT = 1
PARAGRAPH_WEIGHT = 3

# Words or symbols to ignore in similarity calculations
RESTRICTED_WORDS = ["a", "i", "s", "v", "na", "se", "do", "je", "pro", "z", "u", "o", "§", ".",
                    ",", "?", "!", ":", ";", "-"]


# ---------- Functions ----------

def load_cases(filename):
    """
    Load legal cases from a text file into a list of dictionaries.

    Each case in the text file is separated by an empty line. Each line contains
    a key-value pair separated by colon.

    Parameters:
        filename (str): Path to the text file containing cases.
    
    Returns:
        list: A list of dictionaries, each representing a case.

    """
    try:
        cases = []
        current_case = {}

        with open(filename, "r", encoding = "utf-8") as file:
            for line in file:
                line = line.strip()

                # End of a case if line is empty
                if not line:
                    if current_case:
                        cases.append(current_case)

                        # Reset the dictionary for current case
                        current_case = {}
                    continue
                
                # Split key and value by first colon
                if ":" in line:
                    key, value = line.split(":", 1)
                    current_case[key.strip()] = value.strip()

            # Add last case if file dind't end with empty line
            if current_case:
                cases.append(current_case)
            
        return cases
    
    except FileNotFoundError:
        print(f"Chyba: Soubor '{filename}' nebyl nalezen.")
        sys.exit(1)
    except IOError:
        print(f"Chyba: Soubor '{filename}' sa nedá otvorit.")
        sys.exit(1)



def find_similar_cases(cases, scenario, top_n = TOP_N):
    """
    Find the top N most similar cases to the input scenario

    Parameters:
        cases (list): List of existing case dictionaries
        scenario (dict): Dictionary representing the new case
        top_n (int): Number of top similar cases to return

    Returns:
        list: List of dictionaries representing the top N similar cases
    """

    def calculate_score(case, scenario):
        """
        Calculate similarity score between one case and the scenario

        Scoring is based on number of words matched in both the case and the scenario,
        weighted by predefined constants. Words and symbols from restricted words list are ignored.

        Parameters:
            case (dict): Existing case dictionary.
            scenario (dict): New case dictionary.

        Returns:
            int: Similarity score.
        """
        # Extract words from case fields, ignoring restricted words
        subject_words = set(case.get("Předmět","").lower().split()) - set(RESTRICTED_WORDS)
        description_words = set(case.get("Popis","").lower().split()) - set(RESTRICTED_WORDS)
        paragraph_words = set(case.get("Paragrafy","").lower().split()) - set(RESTRICTED_WORDS)

        # Extract words from the new scenario
        scenario_words = set((scenario.get("Předmět","") + " " + 
                              scenario.get("Popis","")).lower().split()) - set(RESTRICTED_WORDS)

        # Weighted sum of matches
        score = (len(subject_words & scenario_words) * SUBJECT_WEIGHT + 
                 len(description_words & scenario_words) * DESCRIPTION_WEIGHT + 
                 len(paragraph_words & scenario_words) * PARAGRAPH_WEIGHT)
        
        return score
        
    # Calculate scores for all cases
    scored_cases = [(c, calculate_score(c, scenario)) for c in cases]
    scored_cases.sort(key=lambda x: x[1], reverse = True) # Sort by score descending
    sorted_cases = [c for c, s in scored_cases]

    return sorted_cases[:top_n]

    

def create_prompt_for_ai(new_case, similar_cases):
    """
    Create propmt string for AI based on the new case and similar cases.

    Parameters:
        new_case (dict): The new case dictionary
        similar_cases (list): List of top N similar case dictionaries
    
    Returns:
        str: Prompt string for AI   
    """

    prompt = f"Máme nový právní případ:\n\"{new_case['Popis']}\"\n\n"
    prompt += "Z minulých případů: \n"

    # Add details of each similar case
    for i, case in enumerate(similar_cases, 1):
        prompt += (f"{i}. ID {case.get('ID', 'neuvedeno')}: {case.get('Popis', 'neuvedeno')}. "
                   f"Paragrafy: {case.get('Paragrafy', 'neuvedeno')}, "
                   f"Rozhodnutí: {case.get('Rozhodnutí', 'neuvedeno')}, "
                   f"Trest: {case.get('Trest', 'neuvedeno')}.\n")

    # Instructions for AI to suggest next steps, predict the court decision and output used case IDs
    prompt += ("\nNa základe těchto informací navrhni možné další kroky a predikci rozhodnutí soudu."
               "Na závěr vypiš pouze ID případů, které jsi použil při analýze, oddělené čárkou.")

    return prompt



def get_ai_response(prompt, model = "gpt-3.5-turbo"):
    """
    Get AI response from OpenAI API using chat completion.

    Parameters:
        prompt (str): Prompt string to send to the model
        model (str): OpenAI model to use.

    Returns:
        str: AI's response text.
    """

    response = openai.chat.completions.create(
        model = model,
        messages = [{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ---------- Main Script ----------

def main():

    # Set you OpenAI key
    openai.api_key = OPENAI_API_KEY

    # Load cases from file
    cases = load_cases(CASES_FILENAME)


    # Combine command-line arguments into one string for the new case
    input_case = " ".join(sys.argv[1:])

    # Create dictionary for the new case
    new_case = {
        "Předmět": "Neurčený", # Placeholder
        "Popis": input_case
    }

    # Find the top N similar cases
    similar_cases = find_similar_cases(cases, new_case, top_n = TOP_N)

    # Create prompt for AI
    prompt = create_prompt_for_ai(new_case, similar_cases)

    # Get AI response
    ai_response = get_ai_response(prompt)

    # Print AI response
    print(ai_response)


if __name__=="__main__":
    main()