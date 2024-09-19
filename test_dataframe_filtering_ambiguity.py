import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_dataframe_filtering():
    # Create a sample DataFrame that more closely resembles your actual data
    data = {
        'Date': pd.date_range(start='2022-12-01', end='2022-12-10'),
        'Description': ['Food purchase', 'Travel expense', 'Food purchase', 'Office supplies', 'Food purchase',
                        'Food purchase', 'Travel expense', 'Food purchase', 'Office supplies', 'Food purchase'],
        'Amount': [100, 200, 150, 300, 120, 180, 250, 140, 280, 190],
        'Bank': ['Bank A'] * 10,
        'Card': ['1234'] * 10,
        'category': ['Food', 'Travel', 'Food', 'Office', 'Food', 'Food', 'Travel', 'Food', 'Office', 'Food'],
        'employer': ['Employer A', 'Employer B', 'Employer A', 'Employer C', 'Employer B',
                     'Employer A', 'Employer C', 'Employer B', 'Employer A', 'Employer C'],
        'Vendor': ['Vendor X'] * 10,
        'note': [''] * 10
    }
    df = pd.DataFrame(data)

    logger.debug(f"Original DataFrame:\n{df}")

    # Define travel days and employer
    travel_days = pd.to_datetime(['2022-12-05', '2022-12-06'])
    employer = 'Employer A'
    travel_employer = 'Employer A'

    # Filter for the specific employer
    df_employer = df[df['employer'] == employer].copy()
    logger.debug(f"Employer-specific DataFrame:\n{df_employer}")

    # Attempt to filter for travel day food expenses
    try:
        travel_food_df = df[
            (df['Date'].isin(travel_days)) &
            (df['category'] == 'Food') &
            (df['employer'] != employer)
            ]
        logger.debug(f"Travel food expenses:\n{travel_food_df}")

        if not travel_food_df.empty:
            df_employer = pd.concat([df_employer, travel_food_df])
            logger.debug(f"Combined DataFrame:\n{df_employer}")
        else:
            logger.debug("No travel food expenses found.")

        # Sort the DataFrame
        df_employer = df_employer.sort_values(['category', 'Date'])

        # Convert 'Amount' to string with two decimal places
        df_employer['Amount'] = df_employer['Amount'].apply(lambda x: f"{x:.2f}")

        logger.debug(f"Final DataFrame:\n{df_employer}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

    logger.debug("Test completed.")


if __name__ == "__main__":
    test_dataframe_filtering()