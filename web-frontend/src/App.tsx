import React, { useState } from 'react';
import './App.css';
import { SearchComponent } from './components/SearchComponent';
import { ResultsComponent } from './components/ResultsComponent';
import { IngredientBriefModal } from './components/IngredientBriefModal';
import { AdminPanel } from './components/AdminPanel';
import { ScanResponse, IngredientBriefResponse, ProductSearchResponse, ProductSearchResult } from './types';

function App() {
  const [scanResult, setScanResult] = useState<ScanResponse | null>(null);
  const [searchResults, setSearchResults] = useState<ProductSearchResult[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedIngredient, setSelectedIngredient] = useState<IngredientBriefResponse | null>(null);
  const [showAdmin, setShowAdmin] = useState(false);

  const handleSearch = async (query: string, type: 'barcode' | 'product') => {
    setLoading(true);
    setError(null);
    setScanResult(null);
    setSearchResults(null);

    try {
      if (type === 'barcode') {
        // Barcode search - get specific product
        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://10.193.196.8:8000'}/scan`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ barcode: query }),
        });

        if (!response.ok) {
          throw new Error('Product not found or server error');
        }

        const result = await response.json();
        setScanResult(result);
      } else {
        // Product name search - get list of products
        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://10.193.196.8:8000'}/search-products`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query, limit: 10 }),
        });

        if (!response.ok) {
          throw new Error('Search failed or server error');
        }

        const result: ProductSearchResponse = await response.json();
        setSearchResults(result.products);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleProductSelect = async (barcode: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://10.193.196.8:8000'}/scan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ barcode }),
      });

      if (!response.ok) {
        throw new Error('Product not found or server error');
      }

      const result = await response.json();
      setScanResult(result);
      setSearchResults(null); // Clear search results
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleIngredientClick = async (ingredient: string) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://10.193.196.8:8000'}/ingredient-brief`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ingredient }),
      });

      if (!response.ok) {
        throw new Error('Failed to get ingredient brief');
      }

      const briefData = await response.json();
      setSelectedIngredient(briefData);
    } catch (err) {
      console.error('Brief error:', err);
      alert(`Could not retrieve brief for ${ingredient}: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  const closeModal = () => {
    setSelectedIngredient(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <div>
            <h1>Vireo Web</h1>
          </div>
          <button 
            className="admin-toggle"
            onClick={() => setShowAdmin(!showAdmin)}
          >
            {showAdmin ? '🔍 User Mode' : '⚙️ Admin'}
          </button>
        </div>
      </header>

      <main className="App-main">
        {showAdmin ? (
          <AdminPanel />
        ) : (
          <>
            <SearchComponent onSearch={handleSearch} loading={loading} />
            
            {error && (
              <div className="error-message">
                <p>❌ {error}</p>
              </div>
            )}

            {searchResults && searchResults.length > 0 && (
              <div className="search-results-container">
                <h3>Search Results</h3>
                <div className="product-list">
                  {searchResults.map((product, index) => (
                    <div key={index} className="product-card" onClick={() => handleProductSelect(product.barcode)}>
                      {product.image_url && (
                        <img src={product.image_url} alt={product.name} className="product-image" />
                      )}
                      <div className="product-info">
                        <h4>{product.name}</h4>
                        {product.brand && <p className="product-brand">{product.brand}</p>}
                        <p className="product-barcode">Barcode: {product.barcode}</p>
                        {product.nutriscore && (
                          <span className={`nutriscore nutriscore-${product.nutriscore.toLowerCase()}`}>
                            {product.nutriscore.toUpperCase()}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {searchResults && searchResults.length === 0 && !loading && (
              <div className="no-results">
                <p>No products found. Try a different search term.</p>
              </div>
            )}

            {scanResult && (
              <ResultsComponent 
                scanResult={scanResult} 
                onIngredientClick={handleIngredientClick}
              />
            )}

            {selectedIngredient && (
              <IngredientBriefModal 
                brief={selectedIngredient} 
                onClose={closeModal}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;