import os
import pandas as pd
from django.apps import AppConfig
from nselib import capital_market


class StockChartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stock_chart'

    def ready(self):
        # Path to save the equity list
        equity_file_path = os.path.join('stock_chart', 'static', 'data', 'equity_list.csv')

        # Save the equity list to file
        self.save_equity_list_to_file(equity_file_path)

    @staticmethod
    def save_equity_list_to_file(equity_file_path):
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(equity_file_path), exist_ok=True)

            # Fetch equity list using nselib
            data = capital_market.equity_list()

            # Check if data is iterable
            if not hasattr(data, '__iter__'):
                raise TypeError("Data fetched is not iterable.")

            # Convert to DataFrame and save as CSV
            df = pd.DataFrame(data)
            df.to_csv(equity_file_path, sep='|', index=False)

            print(f"Equity list successfully saved to {equity_file_path}")
        
        except (FileNotFoundError, PermissionError) as e:
            print(f"File error occurred: {e}")
        except TypeError as e:
            print(f"Data error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
