import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path


def get_yahoo_file(file_name):
    # read file and create a graph of the data
    file_path = Path.cwd() / 'data' / file_name
    df = pd.read_csv(file_path)
    prices = df['Close'].tolist()

    # drop all nan values
    prices = [x for x in prices if str(x) != 'nan']

    return prices


def get_USD_to_ILS(spy_prices, starting_year):

    usd_ils_conversion_rates = get_yahoo_file('ILS=X.csv')

    # drop all values before starting year
    usd_ils_conversion_rates = usd_ils_conversion_rates[1 + 12 * (starting_year - 2004):]

    # Assume the conversion rate list starts in 12/2003, and we need to add 4.4 before that
    missing_months = len(spy_prices) - len(usd_ils_conversion_rates)

    assert missing_months >= 0, "Conversion rates must start before SPY prices"

    # Add 4.4 for the missing months at the start
    usd_ils_conversion_rates = [4.4] * missing_months + usd_ils_conversion_rates

    # Now usd_ils_conversion_rates matches the length of spy_prices
    assert len(usd_ils_conversion_rates) == len(spy_prices), "Conversion rates and SPY prices must have the same length"

    return usd_ils_conversion_rates


def read_housing_data():
    file_name = 'housing_prices.csv'
    file_path = Path.cwd() / 'data' / file_name
    df = pd.read_csv(file_path)
    housing_prices = []
    df = df.drop(columns='year')

    for index, row in df.iterrows():
        housing_prices.append(row['Jan'])
        housing_prices.append(row['Feb'])
        housing_prices.append(row['Mar'])
        housing_prices.append(row['Apr'])
        housing_prices.append(row['May'])
        housing_prices.append(row['Jun'])
        housing_prices.append(row['Jul'])
        housing_prices.append(row['Aug'])
        housing_prices.append(row['Sep'])
        housing_prices.append(row['Oct'])
        housing_prices.append(row['Nov'])
        housing_prices.append(row['Dec'])

    # drop all nan values
    housing_prices = [x for x in housing_prices if str(x) != 'nan']

    return housing_prices


def invest_in_house(investment, starting_year):
    housing_prices = read_housing_data()

    # drop all values before starting year
    housing_prices = housing_prices[12*(starting_year - 1994):]
    calculate_average_yearly_yield(housing_prices, 'housing')

    # normalize series as if I invested in starting_year
    housing_prices = [x / housing_prices[0] * investment for x in housing_prices]

    return housing_prices


def invest_in_spy(initial_investment_ils, starting_year, monthly_payment_ils, years_for_mortgage):
    spy_prices = get_yahoo_file('SPY.csv')

    # drop all values before starting year
    spy_prices = spy_prices[12*(starting_year - 1994):]
    calculate_average_yearly_yield(spy_prices, 'SPY')

    investment_values_ils = []
    # Example USD/ILS conversion rates (assume 4.4 ILS/USD for months before 12/2003)
    usd_ils_conversion_rates = get_USD_to_ILS(spy_prices, starting_year)

    # Convert initial investment to USD using the first exchange rate
    initial_investment_usd = initial_investment_ils / usd_ils_conversion_rates[0]

    shares_owned = initial_investment_usd / spy_prices[0]
    for i, price in enumerate(spy_prices):

        # Add monthly contribution in USD only for the time you are paying mortgage
        if i < years_for_mortgage * 12:
            monthly_contribution_usd = monthly_payment_ils / usd_ils_conversion_rates[i]
            shares_owned += monthly_contribution_usd / price

        investment_value_usd = shares_owned * price
        # Convert the investment value back to ILS using the current exchange rate
        investment_value_ils = investment_value_usd * usd_ils_conversion_rates[i]
        investment_values_ils.append(investment_value_ils)

    return investment_values_ils


def graph_better_investment(housing_prices, spy_ticker, starting_year):
    # create a graph that has a zero line, graph the difference between investing in housing and the spy
    # plot the housing prices
    plt.plot(housing_prices)
    # plot the spy prices
    plt.plot(spy_ticker)

    # change colors of the lines
    plt.gca().get_lines()[0].set_color('blue')
    plt.gca().get_lines()[1].set_color('orange')

    # make x-axis show every 5 years from 1994 to 2024
    plt.xticks(range(0, len(housing_prices), 60), range(starting_year, 2025, 5))
    # add a legend
    plt.legend(['Housing', 'SPY'])

    # add labels
    plt.xlabel('Year')
    plt.ylabel('Investment Value')
    plt.title('Housing vs SPY Investment')

    plt.show()


def graph_difference_in_value(housing_prices, spy_ticker, starting_year):
    # create a graph that has a zero line, graph the difference between investing in housing and the spy
    # plot the housing prices
    plt.plot([x - y for x, y in zip(spy_ticker, housing_prices)])
    # plot the zero line
    plt.plot([0] * len(housing_prices))

    # make x-axis show every 5 years from 1994 to 2024
    plt.xticks(range(0, len(housing_prices), 60), range(starting_year, 2025, 5))

    # change color of zero line to red
    plt.gca().get_lines()[1].set_color('red')
    # change colors of the lines
    plt.gca().get_lines()[0].set_color('blue')

    # add a legend
    plt.legend(['SPY - Housing'])

    # add labels
    plt.xlabel('Year')
    plt.ylabel('Investment Value')
    plt.title('Housing vs SPY Investment')
    plt.show()


def get_mortgage(loan_amount: int, years: int) -> tuple[float, float]:
    assert years in [10, 15, 20, 25, 30], 'years must be 10, 15, 20, 25 or 30'

    times_to_return = {10: 1.318644, 15: 1.492216, 20: 1.701439, 25: 1.918203, 30: 2.147630}

    debt = loan_amount * times_to_return[years]
    monthly_payment = debt / (years * 12)

    return debt, monthly_payment


def calculate_average_yearly_yield(monthly_prices, investment_type: str):
    yearly_prices = [monthly_prices[i] for i in range(0, len(monthly_prices), 12)]
    yearly_yield = [(yearly_prices[i] - yearly_prices[i - 1]) / yearly_prices[i - 1]
                    for i in range(1, len(yearly_prices))]
    # calculate average yearly yield in percentage
    average_yearly_yield = sum(yearly_yield) / len(yearly_yield) * 100

    print(f'Average yearly yield for {investment_type}: {average_yearly_yield:.2f}%')


def graph_net_worth(starting_year=2004, initial_investment=100, borrowed_amount=200, years_for_mortgage=20, rent=4000):
    """contains data from 1994 to 2023"""
    # TODO: adjust for rent prices and dividend yield

    print(f'Starting year: {starting_year}, '
          f'{years_for_mortgage} year mortgage, '
          f'initial investment: {initial_investment}, '
          f'borrowed amount: {borrowed_amount}')

    # calculate down payment percentage
    house_price = initial_investment + borrowed_amount
    down_payment = (initial_investment / house_price) * 100
    print(f'Down payment: {down_payment:.2f}%')

    debt, monthly_payment = get_mortgage(borrowed_amount, years_for_mortgage)

    housing = invest_in_house(initial_investment + borrowed_amount, starting_year)

    # monthly mortgage payment can go towards investing in SPY
    spy = invest_in_spy(initial_investment, starting_year, monthly_payment-rent, years_for_mortgage)

    # adjust housing investment for debt
    housing = [x - debt for x in housing]

    graph_better_investment(housing, spy, starting_year)
    graph_difference_in_value(housing, spy, starting_year)


def main():
    initial_investment = 2_000_000
    borrowed_amount = 2_000_000
    years_for_mortgage = 20
    starting_year = 2004
    rent = 7000

    graph_net_worth(
        starting_year=starting_year,
        years_for_mortgage=years_for_mortgage,
        initial_investment=initial_investment,
        borrowed_amount=borrowed_amount,
        rent=rent
    )


if __name__ == '__main__':
    main()
