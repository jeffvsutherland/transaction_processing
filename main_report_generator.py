import os
import logging
from datetime import datetime
from data_processor import DataProcessor
from expense_report_generator import ExpenseReportGenerator
from final_report_generator import FinalReportGenerator
import utils

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    try:
        # Load configuration and notes
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, 'config.json')
        notes_path = os.path.join(base_dir, 'note.json')

        config = utils.load_config(config_path)
        notes = utils.load_notes(notes_path)

        # Ensure output directory exists
        os.makedirs(config['output_dir'], exist_ok=True)

        # Process data
        logger.info("Starting data processing...")
        data_processor = DataProcessor(config)
        df = data_processor.process()
        logger.info(f"Data processing complete. DataFrame shape: {df.shape}")

        # Set date range
        start_date = datetime.strptime(config['date_range']['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(config['date_range']['end_date'], '%Y-%m-%d')

        # Generate individual expense reports
        logger.info("Generating individual expense reports...")
        expense_generator = ExpenseReportGenerator(config, notes)
        individual_reports = {}
        for employer in config['employers']:
            logger.info(f"Generating report for {employer}")
            report = expense_generator.generate_report(df, employer, start_date, end_date)
            report_path = expense_generator.save_report(report, employer, config['output_dir'])
            individual_reports[employer] = report_path
            logger.info(f"Report for {employer} saved to {report_path}")

        # Generate final report
        logger.info("Generating final report...")
        final_generator = FinalReportGenerator(config, notes)
        errors = []  # You might want to collect errors during the process
        data = {
            'merged_df': df,
            'individual_reports': individual_reports,
            'input_files': data_processor.get_input_files(),
            # Add any other relevant data here
        }
        final_report = final_generator.generate_report(data, errors, start_date, end_date)
        final_report_path = final_generator.save_report(final_report, config['output_dir'])
        logger.info(f"Final report saved to {final_report_path}")

        logger.info("Report generation process completed successfully.")

    except Exception as e:
        logger.error(f"An error occurred during report generation: {str(e)}")
        logger.error("Stack trace:", exc_info=True)


if __name__ == "__main__":
    main()