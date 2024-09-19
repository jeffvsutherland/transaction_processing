# car_expense_calculator.py

from datetime import datetime

class CarExpenseCalculator:
    def __init__(self):
        self.mileage_rates = self.get_mileage_rates()

    def get_mileage_rates(self):
        # This method now returns a dictionary of dictionaries to handle mid-year rate changes
        rates = {
            2022: {'first_half': 0.585, 'second_half': 0.625},
            2023: {'full_year': 0.655},
            2024: {'full_year': 0.67}
        }
        return rates

    def calculate_car_expense(self, miles, date):
        year = datetime.strptime(date, "%Y-%m-%d").year
        month = datetime.strptime(date, "%Y-%m-%d").month

        if year in self.mileage_rates:
            if 'full_year' in self.mileage_rates[year]:
                rate = self.mileage_rates[year]['full_year']
            elif month <= 6:
                rate = self.mileage_rates[year]['first_half']
            else:
                rate = self.mileage_rates[year]['second_half']
        else:
            # If we don't have the rate for the specific year, use the most recent rate
            latest_year = max(self.mileage_rates.keys())
            rate = list(self.mileage_rates[latest_year].values())[-1]

        expense = miles * rate
        return round(expense, 2)

# Example usage
if __name__ == "__main__":
    calculator = CarExpenseCalculator()
    expense = calculator.calculate_car_expense(100, "2022-12-06")
    print(f"Car expense for 100 miles on 2022-12-06: ${expense}")