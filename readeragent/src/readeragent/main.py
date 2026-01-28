from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import warnings

from datetime import datetime

from crew import Readeragent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """
    custom_input = input("Enter what message u want to do: ")

    inputs = {
        'input_text': custom_input,
        'current_year': str(datetime.now().year)
    }

    try:
        Readeragent().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


run()