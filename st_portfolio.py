import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

#streamlit run filepath

def get_yearly_data(symbol, since="max"):
    stock = yf.Ticker(symbol)
    historical_data = stock.history(period=since)
    # Resampling: Verwende das letzte Datum jedes Jahres
    annual_data = historical_data.resample("YE").last()
    # Entferne nicht benötigte Spalten
    annual_data = annual_data.drop(columns=['Open', 'High', 'Low', 'Stock Splits', 'Dividends', 'Volume'], errors='ignore')
    annual_data['ROI'] = annual_data['Close'].pct_change()
    return annual_data

def get_ytd_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="ytd")
    data = data.drop(columns=['Open', 'High', 'Low', 'Stock Splits', 'Dividends', 'Volume'], errors='ignore')
    data["ROI"] = data["Close"].pct_change()
    return data

def analyze_portfolio(stocks, weights, since="max"):
    if len(stocks) != len(weights):
        st.error("Die Anzahl der Aktien und der Gewichtungen stimmen nicht überein")
        return None, None
    stock_dataframes = {}
    avg_roi_values = {}
    avg_portfolio_roi = 0

    for i, stock in enumerate(stocks):
        if since == "ytd":
            stock_dataframes[stock] = get_ytd_data(stock)
            avg_roi_values[stock] = stock_dataframes[stock]['ROI'].sum()
        else:
            stock_dataframes[stock] = get_yearly_data(stock, since)
            avg_roi_values[stock] = stock_dataframes[stock]['ROI'].mean()
        avg_portfolio_roi += weights[i] * (avg_roi_values[stock] * 100)

    if since == "max":
        result = f'Die durchschnittliche jährliche Rendite deines Portfolios beträgt {round(avg_portfolio_roi, 2)}%'
    elif since == "ytd":
        result = f'Die Rendite deines Portfolios beträgt dieses Jahr {round(avg_portfolio_roi, 2)}%'
    else:
        result = f'Die durchschnittliche jährliche Rendite deines Portfolios seit {since} beträgt {round(avg_portfolio_roi, 2)}%'

    roi_str = ''
    for stock, roi in avg_roi_values.items():
      roi_str += f'{stock}: {round(roi * 100, 2)}%\n\n'

    return roi_str, result

def calc_profit(capital, roi, years):
    if years < 1:
        st.error("Funktion funktioniert erst ab mind. einem Jahr")
        return None
    total_roi = ((roi / 100) + 1) ** years
    profit = capital * (total_roi  - 1)                                            
    portfolio_wert = capital + profit
    result = (f"Portfolio Wert: {round(portfolio_wert, 1)}\n\n"
              f"Profit: {round(profit, 1)}\n\n"
              f"Prozentualer Gewinn: {round(total_roi * 100, 2)}%")
    return result

# --- Streamlit-Applikation ---
st.set_page_config(page_title="Aktien & Portfolio Analyse", layout="wide")
st.title("Aktien & Portfolio Analyse mit Streamlit")

# Auswahl einer Funktion über Sidebar
selection = st.sidebar.radio("Wähle die Funktion:", ("Einzelne Aktie", "Portfolio Analyse", "Profitberechnung"))

if selection == "Einzelne Aktie":
    st.header("Einzelne Aktie analysieren")
    symbol = st.text_input("Aktien-Symbol (z.B. AAPL):", value="AAPL")
    since = st.text_input("Zeitraum (max, ytd, 1y, etc.):", value="max").lower()
    if st.button("Daten abrufen"):
        try:
            if since == "ytd":
                df = get_ytd_data(symbol)
            else:
                df = get_yearly_data(symbol, since)
            st.write(f"**Letzte Zeilen für {symbol}**")
            st.dataframe(df.tail())
        except Exception as e:
            st.error(f"Fehler: {e}")

elif selection == "Portfolio Analyse":
    st.header("Portfolio Analyse")
    stocks_input = st.text_input("Aktien-Symbole (kommagetrennt, z. B. AAPL,MSFT,AMZN):", value="AAPL,MSFT,AMZN")
    weights_input = st.text_input("Gewichtungen (kommagetrennt, z. B. 0.33,0.33,0.34):", value="0.33,0.33,0.34")
    since = st.text_input("Zeitraum (max, ytd, 1y, etc.):", value="max").lower()
    
    if st.button("Portfolio analysieren"):
        try:
            stocks = [s.strip().upper() for s in stocks_input.split(",")]
            weights = [float(w.strip()) for w in weights_input.split(",")]
            avg_roi, result = analyze_portfolio(stocks, weights, since)
            if result:
                st.success(result)
                st.markdown(avg_roi)
        except Exception as e:
            st.error(f"Fehler: {e}")

elif selection == "Profitberechnung":
    st.header("Profitberechnung")
    capital = st.number_input("Investitionskapital:", value=10000, step=100)
    roi = st.number_input("ROI in Prozent:", value=5.0, step=0.1)
    years = st.number_input("Laufzeit in Jahren:", value=5, step=1)
    
    if st.button("Profit berechnen"):
        result = calc_profit(capital, roi, years)
        if result:
            st.markdown(result)
