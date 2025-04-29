# CS2 Market Data Web App

A simple web interface for testing the CS2 Market Data API endpoints.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The app will be available at http://localhost:3000

## Usage

1. Make sure your FastAPI backend is running at http://localhost:8000
2. Use the interface to test different API endpoints:
   - Get Item Data: Enter a market hash name and click "Test"
   - Get Item History: Enter a market hash name and number of days, then click "Test"
   - Get Arbitrage Opportunities: Click "Test" to fetch current opportunities

## Features

- Test all API endpoints
- View responses in a formatted JSON display
- Error handling and loading states
- Clean, responsive UI with Tailwind CSS
