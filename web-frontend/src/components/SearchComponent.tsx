import React, { useState } from 'react';
import { Search, Barcode } from 'lucide-react';

interface SearchComponentProps {
  onSearch: (barcode: string) => void;
  loading: boolean;
}

export const SearchComponent: React.FC<SearchComponentProps> = ({ onSearch, loading }) => {
  const [barcode, setBarcode] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (barcode.trim()) {
      onSearch(barcode.trim());
    }
  };

  return (
    <div className="search-container">
      <div className="search-header">
        <Barcode className="search-icon" size={32} />
        <h2>Search for a Product</h2>
        <p>Enter a barcode to analyze ingredients</p>
      </div>
      
      <form onSubmit={handleSubmit} className="search-form">
        <div className="input-group">
          <input
            type="text"
            value={barcode}
            onChange={(e) => setBarcode(e.target.value)}
            placeholder="Enter barcode (e.g., 1234567890)"
            className="barcode-input"
            disabled={loading}
          />
          <button 
            type="submit" 
            className="search-button"
            disabled={loading || !barcode.trim()}
          >
            {loading ? (
              <div className="spinner" />
            ) : (
              <>
                <Search size={20} />
                Search
              </>
            )}
          </button>
        </div>
      </form>

      <div className="search-examples">
        <p>Try these example barcodes:</p>
        <div className="example-barcodes">
          <button 
            className="example-button"
            onClick={() => setBarcode('3017620422003')}
            disabled={loading}
          >
            Nutella (3017620422003)
          </button>
          <button 
            className="example-button"
            onClick={() => setBarcode('7622210939672')}
            disabled={loading}
          >
            Oreo (7622210939672)
          </button>
          <button 
            className="example-button"
            onClick={() => setBarcode('1234567890')}
            disabled={loading}
          >
            Test (1234567890)
          </button>
        </div>
      </div>
    </div>
  );
};
