import React, { useState } from 'react';
import { Search, Barcode, Package } from 'lucide-react';

interface SearchComponentProps {
  onSearch: (query: string, type: 'barcode' | 'product') => void;
  loading: boolean;
}

export const SearchComponent: React.FC<SearchComponentProps> = ({ onSearch, loading }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState<'barcode' | 'product'>('barcode');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch(searchQuery.trim(), searchType);
    }
  };

  return (
    <div className="search-container">
      <div className="search-header">
        {searchType === 'barcode' ? (
          <Barcode className="search-icon" size={32} />
        ) : (
          <Package className="search-icon" size={32} />
        )}
        <h2>Search for a Product</h2>
        <p>
          {searchType === 'barcode' 
            ? 'Enter a barcode to analyze ingredients' 
            : 'Search for a product by name'
          }
        </p>
      </div>
      
      {/* Search Type Toggle */}
      <div className="search-type-toggle">
        <button
          type="button"
          className={`toggle-button ${searchType === 'barcode' ? 'active' : ''}`}
          onClick={() => setSearchType('barcode')}
          disabled={loading}
        >
          <Barcode size={16} />
          Barcode
        </button>
        <button
          type="button"
          className={`toggle-button ${searchType === 'product' ? 'active' : ''}`}
          onClick={() => setSearchType('product')}
          disabled={loading}
        >
          <Package size={16} />
          Product Name
        </button>
      </div>
      
      <form onSubmit={handleSubmit} className="search-form">
        <div className="input-group">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={
              searchType === 'barcode' 
                ? 'Enter barcode (e.g., 1234567890)' 
                : 'Enter product name (e.g., Nutella, Coca Cola)'
            }
            className="search-input"
            disabled={loading}
          />
          <button 
            type="submit" 
            className="search-button"
            disabled={loading || !searchQuery.trim()}
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

    </div>
  );
};
