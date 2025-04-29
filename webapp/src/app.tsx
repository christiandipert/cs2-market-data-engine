import React, { useState, useEffect } from 'react';
import axios from 'axios';
const App = () => {
  const [itemData, setItemData] = useState<itemData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [marketHashName, setMarketHashName] = useState('');

  interface itemData {
    name: string;
    price: number;
    volume: number;
    last_updated: string;
    steam?: {
      lowest_price: number;
      volume: number;
    };
    bitskins?: {
      lowest_price: number;
      volume: number;
    };
  }

  const fetchItemData = async () => {
    if (!marketHashName) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`http://localhost:8000/items/${marketHashName}`);
      setItemData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error fetching item data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">CS2 Market Data Viewer</h1>
      
      <div className="mb-4">
        <input
          type="text"
          value={marketHashName}
          onChange={(e) => setMarketHashName(e.target.value)}
          placeholder="Enter market hash name"
          className="border p-2 rounded"
        />
        <button
          onClick={fetchItemData}
          className="bg-blue-500 text-white px-4 py-2 rounded ml-2"
        >
          Search
        </button>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}
      
      {itemData && (
        <div className="border p-4 rounded">
          <h2 className="text-xl font-semibold mb-2">{itemData.name}</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold">Steam Market</h3>
              {itemData.steam ? (
                <div>
                  <p>Lowest Price: ${itemData.steam.lowest_price}</p>
                  <p>Volume: {itemData.steam.volume}</p>
                </div>
              ) : (
                <p>No data available</p>
              )}
            </div>
            <div>
              <h3 className="font-semibold">Bitskins</h3>
              {itemData.bitskins ? (
                <div>
                  <p>Lowest Price: ${itemData.bitskins.lowest_price}</p>
                  <p>Volume: {itemData.bitskins.volume}</p>
                </div>
              ) : (
                <p>No data available</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;