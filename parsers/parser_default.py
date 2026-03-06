import pandas as pd
import parsers.gen_dataset as gds


class ParserDefault(gds.SleepLogsParserStrategy):
    def __extract__(self, path, **kwargs):
        return pd.read_csv(
            path, 
            parse_dates=['Date', 'Sleep Time', 'Wake Time'], 
            date_format={
                'Date': '%Y-%m-%d', 
                'Sleep Time': '%I:%M %p', 
                'Wake Time': '%I:%M %p'
            },
        )
    
    def __prepare__(self, /, path = None, **kwargs):
        df = super().__prepare__(path, **kwargs)
        df['Duration'] = pd.to_timedelta(df['Duration'])
        return df


if __name__ == '__main__':
    df = ParserDefault().__prepare__('clean_data/sleep_logs.csv')
    print(df)
    df.info()