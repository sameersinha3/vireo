import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Edit, Save, X } from 'lucide-react';

interface Category {
  id: string;
  name: string;
  description: string;
  severity_level: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface Ingredient {
  id: string;
  name: string;
  aliases: string[];
  category_id: string;
  severity_level: string;
  health_concerns: string[];
  environmental_impact?: string;
  research_summary?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const AdminPanel: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'categories' | 'ingredients'>('categories');

  const [newCategory, setNewCategory] = useState({
    name: '',
    description: '',
    severity_level: 'moderate'
  });

  const [newIngredient, setNewIngredient] = useState({
    name: '',
    aliases: '',
    category_id: '',
    severity_level: 'moderate',
    health_concerns: '',
    environmental_impact: '',
    research_summary: ''
  });

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    loadCategories();
    loadIngredients();
  }, []);

  const loadCategories = async () => {
    try {
      const response = await fetch(`${API_BASE}/admin/categories`);
      const data = await response.json();
      setCategories(data.categories);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const loadIngredients = async () => {
    try {
      const response = await fetch(`${API_BASE}/admin/ingredients`);
      const data = await response.json();
      setIngredients(data.ingredients);
    } catch (error) {
      console.error('Error loading ingredients:', error);
    }
  };

  const createCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch(`${API_BASE}/admin/categories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newCategory)
      });
      
      if (response.ok) {
        setNewCategory({ name: '', description: '', severity_level: 'moderate' });
        loadCategories();
      }
    } catch (error) {
      console.error('Error creating category:', error);
    } finally {
      setLoading(false);
    }
  };

  const createIngredient = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const ingredientData = {
        ...newIngredient,
        aliases: newIngredient.aliases.split(',').map(a => a.trim()).filter(a => a),
        health_concerns: newIngredient.health_concerns.split(',').map(h => h.trim()).filter(h => h)
      };
      
      const response = await fetch(`${API_BASE}/admin/ingredients`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ingredientData)
      });
      
      if (response.ok) {
        setNewIngredient({
          name: '', aliases: '', category_id: '', severity_level: 'moderate',
          health_concerns: '', environmental_impact: '', research_summary: ''
        });
        loadIngredients();
      }
    } catch (error) {
      console.error('Error creating ingredient:', error);
    } finally {
      setLoading(false);
    }
  };

  const runMigration = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/admin/migrate`, {
        method: 'POST'
      });
      
      if (response.ok) {
        loadCategories();
        loadIngredients();
        alert('Migration completed successfully!');
      }
    } catch (error) {
      console.error('Error running migration:', error);
      alert('Migration failed. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h2>🔧 Ingredient Management</h2>
        <button 
          className="migration-button"
          onClick={runMigration}
          disabled={loading}
        >
          Migrate from JSON
        </button>
      </div>

      <div className="admin-tabs">
        <button 
          className={`tab-button ${activeTab === 'categories' ? 'active' : ''}`}
          onClick={() => setActiveTab('categories')}
        >
          Categories ({categories.length})
        </button>
        <button 
          className={`tab-button ${activeTab === 'ingredients' ? 'active' : ''}`}
          onClick={() => setActiveTab('ingredients')}
        >
          Ingredients ({ingredients.length})
        </button>
      </div>

      {activeTab === 'categories' && (
        <div className="admin-section">
          <h3>Create New Category</h3>
          <form onSubmit={createCategory} className="admin-form">
            <div className="form-group">
              <input
                type="text"
                placeholder="Category name"
                value={newCategory.name}
                onChange={(e) => setNewCategory({...newCategory, name: e.target.value})}
                required
              />
              <input
                type="text"
                placeholder="Description"
                value={newCategory.description}
                onChange={(e) => setNewCategory({...newCategory, description: e.target.value})}
                required
              />
              <select
                value={newCategory.severity_level}
                onChange={(e) => setNewCategory({...newCategory, severity_level: e.target.value})}
              >
                <option value="low">Low</option>
                <option value="moderate">Moderate</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
              <button type="submit" disabled={loading}>
                <Plus size={16} /> Create Category
              </button>
            </div>
          </form>

          <h3>Existing Categories</h3>
          <div className="admin-list">
            {categories.map((category) => (
              <div key={category.id} className="admin-item">
                <div className="item-content">
                  <h4>{category.name}</h4>
                  <p>{category.description}</p>
                  <span className={`severity-badge severity-${category.severity_level}`}>
                    {category.severity_level}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'ingredients' && (
        <div className="admin-section">
          <h3>Create New Ingredient</h3>
          <form onSubmit={createIngredient} className="admin-form">
            <div className="form-group">
              <input
                type="text"
                placeholder="Ingredient name"
                value={newIngredient.name}
                onChange={(e) => setNewIngredient({...newIngredient, name: e.target.value})}
                required
              />
              <input
                type="text"
                placeholder="Aliases (comma-separated)"
                value={newIngredient.aliases}
                onChange={(e) => setNewIngredient({...newIngredient, aliases: e.target.value})}
              />
              <select
                value={newIngredient.category_id}
                onChange={(e) => setNewIngredient({...newIngredient, category_id: e.target.value})}
                required
              >
                <option value="">Select category</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
              <select
                value={newIngredient.severity_level}
                onChange={(e) => setNewIngredient({...newIngredient, severity_level: e.target.value})}
              >
                <option value="low">Low</option>
                <option value="moderate">Moderate</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
              <input
                type="text"
                placeholder="Health concerns (comma-separated)"
                value={newIngredient.health_concerns}
                onChange={(e) => setNewIngredient({...newIngredient, health_concerns: e.target.value})}
              />
              <textarea
                placeholder="Research summary"
                value={newIngredient.research_summary}
                onChange={(e) => setNewIngredient({...newIngredient, research_summary: e.target.value})}
              />
              <button type="submit" disabled={loading}>
                <Plus size={16} /> Create Ingredient
              </button>
            </div>
          </form>

          <h3>Existing Ingredients</h3>
          <div className="admin-list">
            {ingredients.map((ingredient) => (
              <div key={ingredient.id} className="admin-item">
                <div className="item-content">
                  <h4>{ingredient.name}</h4>
                  <p>Category: {ingredient.category_id}</p>
                  {ingredient.aliases.length > 0 && (
                    <p>Aliases: {ingredient.aliases.join(', ')}</p>
                  )}
                  <span className={`severity-badge severity-${ingredient.severity_level}`}>
                    {ingredient.severity_level}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
