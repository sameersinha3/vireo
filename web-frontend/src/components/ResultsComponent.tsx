import React from 'react';
import { Package, AlertTriangle, CheckCircle, ExternalLink } from 'lucide-react';
import { ScanResponse } from '../types';

interface ResultsComponentProps {
  scanResult: ScanResponse;
  onIngredientClick: (ingredient: string) => void;
}

export const ResultsComponent: React.FC<ResultsComponentProps> = ({ 
  scanResult, 
  onIngredientClick 
}) => {
  const { product, flagged_ingredients } = scanResult;

  return (
    <div className="results-container">
      <div className="product-info">
        <div className="product-header">
          <Package className="product-icon" size={24} />
          <div className="product-details">
            <h2>{product.name || 'Unknown Product'}</h2>
            <p className="product-brand">{product.brand || 'Unknown Brand'}</p>
            <p className="product-barcode">Barcode: {product.barcode}</p>
          </div>
        </div>


        <div className="product-meta">
          {product.nutriscore && (
            <div className="meta-item">
              <span className="meta-label">Nutri-Score:</span>
              <span className={`nutriscore nutriscore-${product.nutriscore.toLowerCase()}`}>
                {product.nutriscore.toUpperCase()}
              </span>
            </div>
          )}
          
          {product.packaging_material && (
            <div className="meta-item">
              <span className="meta-label">Packaging:</span>
              <span>{product.packaging_material}</span>
            </div>
          )}
        </div>
      </div>

      <div className="ingredients-section">
        <h3>
          {flagged_ingredients.length > 0 ? (
            <>
              <AlertTriangle className="warning-icon" size={20} />
              Flagged Ingredients ({flagged_ingredients.length})
            </>
          ) : (
            <>
              <CheckCircle className="success-icon" size={20} />
              All Clear!
            </>
          )}
        </h3>

        {flagged_ingredients.length > 0 ? (
          <div className="ingredients-list">
            <p className="ingredients-description">
              These ingredients have been flagged for potential health or environmental concerns. 
              Click on any ingredient to view detailed research briefs.
            </p>
            
            <div className="flagged-ingredients">
              {flagged_ingredients.map((ingredient, index) => {
                const metadata = scanResult.flagged_ingredients_metadata?.[ingredient];
                return (
                  <button
                    key={index}
                    className={`ingredient-button flagged severity-${metadata?.severity || 'moderate'}`}
                    onClick={() => onIngredientClick(ingredient)}
                  >
                    <div className="ingredient-info">
                      <span className="ingredient-name">{ingredient}</span>
                      {metadata && (
                        <div className="ingredient-meta">
                          <span className="ingredient-category">{metadata.category}</span>
                          <span className={`severity-badge severity-${metadata.severity}`}>
                            {metadata.severity}
                          </span>
                        </div>
                      )}
                    </div>
                    <ExternalLink size={16} />
                  </button>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="no-flagged">
            <p>No flagged ingredients found in this product! 🎉</p>
          </div>
        )}

        {product.ingredients_text && (
          <details className="all-ingredients">
            <summary>View All Ingredients</summary>
            <div className="ingredients-text">
              {product.ingredients_text}
            </div>
          </details>
        )}
      </div>
    </div>
  );
};
