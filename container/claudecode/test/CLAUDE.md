# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a simple web application for checking Japanese Yen (JPY) exchange rates against various currencies. The application uses the ExchangeRate-API to fetch real-time exchange rate data.

## Application Structure

- `index.html`: Main HTML file with the user interface
- `style.css`: CSS styling for the application
- `script.js`: JavaScript functionality for fetching and displaying exchange rates
- `sequence-diagram.md`: Contains a mermaid sequence diagram showing the application flow @sequence-diagram

## External APIs

- **ExchangeRate-API**: The application uses the free tier of ExchangeRate-API (`https://open.er-api.com/v6/latest/JPY`) to fetch current exchange rate data.

## Functionality

The application allows users to:
1. Select a currency from a dropdown menu (USD, EUR, GBP, AUD, CAD, CNY)
2. Click a button to fetch the current exchange rate
3. View the exchange rate as JPY per 1 unit of the selected currency
4. See when the rate was last updated

## Development Notes

### Running the Application

To run the application locally:
- Open `index.html` in a web browser

No build process, package management, or server setup is required as this is a simple client-side application.

### Adding New Currencies

To add new currencies to the dropdown:
1. Add a new option to the `select` element in `index.html`
2. Add the currency code and Japanese name to the `currencies` object in `script.js`

## Application Flow

For a detailed visual representation of the application's process flow, see the sequence diagram in @sequence-diagram.