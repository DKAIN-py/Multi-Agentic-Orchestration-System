from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import warnings

from .flow import FileGenerationFlow

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    flow = FileGenerationFlow()
    
    content = r""" Q1 Sales Report

            Here is the data you requested.

            | Region | Sales | Growth |
            | :--- | :--- | :--- |
            | North | $50,000 | +5% |
            | South | $12,000 | -2% |
            | West | $80,000 | +12% |

            Growth is steady.
            
            create a docx of content
            """

    # Test 1: Excel
    print("\n--- TEST 1 ---")
    flow.kickoff(inputs={"raw_data": content})
    
    # Test 2: PDF
    # print("\n--- TEST 2 ---")
    # flow.kickoff(inputs={"raw_data": "Create a formal docx report about the project."})


if __name__ == "__main__":
    run()
