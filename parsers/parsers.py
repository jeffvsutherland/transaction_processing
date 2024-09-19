import pandas as pd
import logging

logger = logging.getLogger('parsers')

def get_parser(bank_name):
    if bank_name == 'crypto_com':
        return CryptoComParser()
    elif bank_name == 'chase':
        return ChaseParser()
    elif bank_name == 'bank_of_america':
        return BankOfAmericaParser()
    elif bank_name == 'capital_one':
        return CapitalOneParser()
    else:
        return None

class CryptoComParser:
    def parse(self, file_path):
        try:
            df = pd.read_csv(file_path)
            df['Bank'] = 'Crypto.com'
            df['Card'] = 'Crypto.com Card'
            logger.info(f"Parsed Crypto.com file: {file_path}, DataFrame shape: {df.shape}")
            return df, 'Crypto.com', 'Crypto.com Card'
        except Exception as e:
            logger.error(f"Error parsing Crypto.com file: {str(e)}")
            raise ValueError(f"Error parsing Crypto.com file: {str(e)}")

class ChaseParser:
    def parse(self, file_path):
        try:
            df = pd.read_csv(file_path)
            df['Bank'] = 'Chase'
            df['Card'] = 'Chase Card'
            logger.info(f"Parsed Chase file: {file_path}, DataFrame shape: {df.shape}")
            return df, 'Chase', 'Chase Card'
        except Exception as e:
            logger.error(f"Error parsing Chase file: {str(e)}")
            raise ValueError(f"Error parsing Chase file: {str(e)}")

class BankOfAmericaParser:
    def parse(self, file_path):
        try:
            df = pd.read_csv(file_path)
            df['Bank'] = 'Bank of America'
            df['Card'] = 'Bank of America Card'
            logger.info(f"Parsed Bank of America file: {file_path}, DataFrame shape: {df.shape}")
            return df, 'Bank of America', 'Bank of America Card'
        except Exception as e:
            logger.error(f"Error parsing Bank of America file: {str(e)}")
            raise ValueError(f"Error parsing Bank of America file: {str(e)}")

class CapitalOneParser:
    def parse(self, file_path):
        try:
            df = pd.read_csv(file_path)
            df['Bank'] = 'Capital One'
            df['Card'] = 'Capital One Card'
            logger.info(f"Parsed Capital One file: {file_path}, DataFrame shape: {df.shape}")
            return df, 'Capital One', 'Capital One Card'
        except Exception as e:
            logger.error(f"Error parsing Capital One file: {str(e)}")
            raise ValueError(f"Error parsing Capital One file: {str(e)}")