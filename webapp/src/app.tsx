import React, { useState } from 'react';
import axios from 'axios';

interface MarketSearchProps {
  endpoint: string;
  method: 'get' | 'post';
  placeholder?: string;
  buttonText?: string;
  onSearch: (data: any) => void;
  onError?: (error: string) => void;
}

const MarketSearch = ({
  endpoint,
  method,
  placeholder = 'Enter search term',
  buttonText = 'Search',
  onSearch,
  onError
}: MarketSearchProps) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const encodedSearchTerm = encodeURIComponent(searchTerm.trim());
      const response = await axios[method](`http://localhost:8000${endpoint}`, {
        params: { query: encodedSearchTerm }
      });
      onSearch(response.data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      onError?.(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mb-4">
      <div className="flex">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder={placeholder}
          className="border p-2 rounded flex-grow"
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="bg-blue-500 text-white px-4 py-2 rounded ml-2 hover:bg-blue-600 disabled:bg-blue-300"
        >
          {loading ? 'Loading...' : buttonText}
        </button>
      </div>
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </div>
  );
};

interface ItemData {
  name: string;
  steam?: {
    lowest_price: number;
    volume: number;
  };
  bitskins?: {
    lowest_price: number;
    volume: number;
  };
}

const App: React.FC = () => {
  const [itemData, setItemData] = useState<ItemData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = (data: ItemData) => {
    setItemData(data);
    setError(null);
  };

  const handleError = (error: string) => {
    setError(error);
    setItemData(null);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">CS2 Market Data Viewer</h1>
      
      <MarketSearch
        endpoint="/items"
        method="get"
        placeholder="Get all items"
        buttonText="Search"
        onSearch={handleSearch}
        onError={handleError}
      />

      <MarketSearch
        endpoint="/popular"
        method="get"
        placeholder="Get Popular Items. Example search"
        buttonText="Search"
        onSearch={handleSearch}
        onError={handleError}
      />

      <MarketSearch
        endpoint="/priceoverview"
        method="get"
        placeholder="Get Price Overview. Example search: Operation Breakout Weapon Case"
        buttonText="Search"
        onSearch={handleSearch}
        onError={handleError}
      />
      
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