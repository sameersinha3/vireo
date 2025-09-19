import React from 'react';
import { X, FileText, Loader } from 'lucide-react';
import { IngredientBriefResponse } from '../types';

interface IngredientBriefModalProps {
  brief: IngredientBriefResponse;
  onClose: () => void;
}

export const IngredientBriefModal: React.FC<IngredientBriefModalProps> = ({ 
  brief, 
  onClose 
}) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">
            <FileText className="modal-icon" size={24} />
            <h2>{brief.ingredient}</h2>
          </div>
          <button className="close-button" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="modal-body">
          <div className="brief-content">
            <h3>Research Brief</h3>
            <div className="brief-text">
              {brief.summary}
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="close-modal-button" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
