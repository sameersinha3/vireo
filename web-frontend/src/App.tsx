import React, { useState } from 'react';
import './App.css';
import { SearchComponent } from './components/SearchComponent';
import { ResultsComponent } from './components/ResultsComponent';
import { IngredientBriefModal } from './components/IngredientBriefModal';
import { AdminPanel } from './components/AdminPanel';
import { ScanResponse, IngredientBriefResponse } from './types';

function App() {
  const [scanResult, setScanResult] = useState<ScanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedIngredient, setSelectedIngredient] = useState<IngredientBriefResponse | null>(null);
  const [showAdmin, setShowAdmin] = useState(false);

  const handleSearch = async (barcode: string) => {
    setLoading(true);
    setError(null);
    setScanResult(null);

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://192.168.10.107:8000'}/scan`, {
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
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleIngredientClick = async (ingredient: string) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://192.168.10.107:8000'}/ingredient-brief`, {
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