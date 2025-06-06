import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import pandas as pd

# --- Funktion: Jahresdaten abrufen ---
def get_yearly_data(symbol, since="max"):
    stock = yf.Ticker(symbol)
    historical_data = stock.history(period=since)
    # Resampling: Verwende das letzte Datum jedes Jahres
    annual_data = historical_data.resample("YE").last()
    # Entferne nicht benötigte Spalten; benutze errors='ignore' falls Spalten fehlen
    annual_data = annual_data.drop(columns=['Open', 'High', 'Low', 'Stock Splits', 'Dividends', 'Volume'], errors='ignore')
    annual_data['ROI'] = annual_data['Close'].pct_change()
    return annual_data

# --- Funktion: YTD Daten abrufen ---
def get_ytd_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="ytd")
    # Entferne nicht benötigte Spalten
    data = data.drop(columns=['Open', 'High', 'Low', 'Stock Splits', 'Dividends', 'Volume'], errors='ignore')
    data["ROI"] = data["Close"].pct_change()
    return data

# --- Funktion: Portfolio Analyse ---
def analyze_portfolio(stocks, weights, since="max", show=True):
    if len(stocks) != len(weights):
        raise ValueError("Die anzahl der Aktien und der Gewichtungen stimmen nicht überein")
        
    stock_dataframes = {}
    avg_roi_values = {}
    avg_portfolio_roi = 0
    
    for i, stock in enumerate(stocks):
        if since == "ytd":
            stock_dataframes[stock] = get_ytd_data(stock)
            # ROI wird hier als Summe der einzelnen prozentualen Änderungen berechnet
            avg_roi_values[stock] = stock_dataframes[stock]['ROI'].sum()
        else:
            stock_dataframes[stock] = get_yearly_data(stock, since)
            avg_roi_values[stock] = stock_dataframes[stock]['ROI'].mean()
        avg_portfolio_roi += weights[i] * (avg_roi_values[stock] * 100)
    
    if show and since == "max":
        msg = f'Die durchschnittliche jährliche Rendite deines Portfolios beträgt {round(avg_portfolio_roi, 2)}%'
    elif show and since == "ytd":
        msg = f'Die Rendite deines Portfolios beträgt dieses Jahr {round(avg_portfolio_roi, 2)}%'
    else:
        msg = f'Die durchschnittliche jährliche Rendite deines Portfolios seit {since} beträgt {round(avg_portfolio_roi, 2)}%'
    
    print(msg)
    return stock_dataframes, avg_portfolio_roi

# --- Funktion: Gewinnberechnung ---
def calc_profit(capital, roi, years):
    if years < 1:
        raise ValueError("Funktion funktioniert erst ab mind. einem Jahr")
    total_roi = ((roi / 100) + 1) ** years
    profit = capital * total_roi
    portfolio_wert = capital + profit
    msg = (f"Portfolio Wert: {round(portfolio_wert, 1)}\n"
           f"Profit: {round(profit, 1)}\n"
           f"Prozentualer Gewinn: {round(total_roi * 100, 2)}%")
    print(msg)
    return msg

# --- GUI-Setup ---
root = tk.Tk()
root.title("Aktien & Portfolio Analyse")

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Tab 1: Einzelne Aktie
tab_single = ttk.Frame(notebook)
notebook.add(tab_single, text="Einzelne Aktie")

ttk.Label(tab_single, text="Aktien Symbol (z.B. AAPL):").pack(pady=5)
entry_symbol = ttk.Entry(tab_single, width=30)
entry_symbol.pack(pady=5)

ttk.Label(tab_single, text="Zeitraum (max, ytd, 1y, etc.):").pack(pady=5)
entry_since = ttk.Entry(tab_single, width=30)
entry_since.insert(0, "max")
entry_since.pack(pady=5)

def fetch_single():
    symbol = entry_symbol.get().strip().upper()
    since = entry_since.get().strip().lower()
    if not symbol:
        messagebox.showerror("Fehler", "Bitte Aktien Symbol eingeben.")
        return
    try:
        if since == "ytd":
            df = get_ytd_data(symbol)
        else:
            df = get_yearly_data(symbol, since)
        text_single.delete("1.0", tk.END)
        text_single.insert(tk.END, df.tail().to_string())
    except Exception as e:
        messagebox.showerror("Fehler", str(e))

ttk.Button(tab_single, text="Daten abrufen", command=fetch_single).pack(pady=10)
text_single = tk.Text(tab_single, height=15, width=80)
text_single.pack(pady=5)

# Tab 2: Portfolio Analyse
tab_portfolio = ttk.Frame(notebook)
notebook.add(tab_portfolio, text="Portfolio Analyse")

ttk.Label(tab_portfolio, text="Aktien-Symbole (kommagetrennt, z.B. AAPL,MSFT,AMZN):").pack(pady=5)
entry_stocks = ttk.Entry(tab_portfolio, width=50)
entry_stocks.pack(pady=5)

ttk.Label(tab_portfolio, text="Gewichtungen (kommagetrennt, z.B. 0.1,0.15,0.1):").pack(pady=5)
entry_weights = ttk.Entry(tab_portfolio, width=50)
entry_weights.pack(pady=5)

ttk.Label(tab_portfolio, text="Zeitraum (max, ytd, 1y, etc.):").pack(pady=5)
entry_port_since = ttk.Entry(tab_portfolio, width=30)
entry_port_since.insert(0, "max")
entry_port_since.pack(pady=5)

def analyze_portfolio_action():
    stocks_str = entry_stocks.get().strip()
    weights_str = entry_weights.get().strip()
    since = entry_port_since.get().strip().lower()
    if not stocks_str or not weights_str:
        messagebox.showerror("Fehler", "Bitte fülle Aktien und Gewichtungen aus.")
        return
    try:
        stocks = [s.strip().upper() for s in stocks_str.split(",")]
        weights = [float(w.strip()) for w in weights_str.split(",")]
        _, avg_portfolio_roi = analyze_portfolio(stocks, weights, since)
        text_portfolio.delete("1.0", tk.END)
        text_portfolio.insert(tk.END, f"Ergebnis:\n{avg_portfolio_roi}%")
    except Exception as e:
        messagebox.showerror("Fehler", str(e))

ttk.Button(tab_portfolio, text="Portfolio analysieren", command=analyze_portfolio_action).pack(pady=10)
text_portfolio = tk.Text(tab_portfolio, height=10, width=80)
text_portfolio.pack(pady=5)

# Tab 3: Profitberechnung
tab_profit = ttk.Frame(notebook)
notebook.add(tab_profit, text="Profitberechnung")

ttk.Label(tab_profit, text="Investitionskapital (z.B. 10000):").pack(pady=5)
entry_capital = ttk.Entry(tab_profit, width=30)
entry_capital.pack(pady=5)

ttk.Label(tab_profit, text="ROI in Prozent (z.B. 5):").pack(pady=5)
entry_roi = ttk.Entry(tab_profit, width=30)
entry_roi.pack(pady=5)

ttk.Label(tab_profit, text="Laufzeit in Jahren (z.B. 5):").pack(pady=5)
entry_years = ttk.Entry(tab_profit, width=30)
entry_years.pack(pady=5)

def calculate_profit_action():
    try:
        capital = float(entry_capital.get().strip())
        roi = float(entry_roi.get().strip())
        years = int(entry_years.get().strip())
        result = calc_profit(capital, roi, years)
        text_profit.delete("1.0", tk.END)
        text_profit.insert(tk.END, result)
    except Exception as e:
        messagebox.showerror("Fehler", str(e))

ttk.Button(tab_profit, text="Profit berechnen", command=calculate_profit_action).pack(pady=10)
text_profit = tk.Text(tab_profit, height=10, width=80)
text_profit.pack(pady=5)

root.mainloop()
