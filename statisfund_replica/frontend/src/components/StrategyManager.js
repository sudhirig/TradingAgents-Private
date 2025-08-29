import React, { useState, useEffect } from 'react';

const StrategyManager = ({ generatedCode, backtestResults }) => {
  const [strategies, setStrategies] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [saveData, setSaveData] = useState({
    name: '',
    description: '',
    tags: ''
  });

  useEffect(() => {
    loadStrategies();
    loadTemplates();
  }, []);

  const loadStrategies = async () => {
    try {
      const response = await fetch('/api/strategies');
      const data = await response.json();
      if (data.success) {
        setStrategies(data.strategies);
      }
    } catch (error) {
      console.error('Error loading strategies:', error);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await fetch('/api/templates');
      const data = await response.json();
      if (data.success) {
        setTemplates(data.templates);
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const saveStrategy = async () => {
    if (!generatedCode) {
      alert('No strategy code to save');
      return;
    }

    try {
      const strategyData = {
        name: saveData.name || `Strategy_${Date.now()}`,
        description: saveData.description,
        code: generatedCode,
        tags: saveData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        performance_metrics: backtestResults || {},
        symbols: ['SPY'], // Default symbol
        parameters: {}
      };

      const response = await fetch('/api/strategy/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(strategyData)
      });

      const result = await response.json();
      if (result.success) {
        alert(`Strategy saved with ID: ${result.strategy_id}`);
        setShowSaveDialog(false);
        setSaveData({ name: '', description: '', tags: '' });
        loadStrategies();
      }
    } catch (error) {
      console.error('Error saving strategy:', error);
      alert('Failed to save strategy');
    }
  };

  const loadStrategy = async (strategyId) => {
    try {
      const response = await fetch(`/api/strategy/${strategyId}`);
      const data = await response.json();
      if (data.success) {
        // You could emit this to parent component or handle loading
        console.log('Loaded strategy:', data.strategy);
        alert('Strategy loaded! Check console for details.');
      }
    } catch (error) {
      console.error('Error loading strategy:', error);
    }
  };

  const validateStrategy = async () => {
    if (!generatedCode) {
      alert('No strategy code to validate');
      return;
    }

    try {
      const response = await fetch('/api/strategy/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: generatedCode })
      });

      const result = await response.json();
      if (result.success) {
        alert(`Validation Result:\n${result.summary}`);
      }
    } catch (error) {
      console.error('Error validating strategy:', error);
      alert('Validation failed');
    }
  };

  return (
    <div className="strategy-manager">
      <h3>Strategy Management</h3>
      
      {/* Action Buttons */}
      <div className="manager-actions">
        {generatedCode && (
          <>
            <button 
              className="btn btn-success"
              onClick={() => setShowSaveDialog(true)}
            >
              💾 Save Strategy
            </button>
            <button 
              className="btn btn-info"
              onClick={validateStrategy}
            >
              ✅ Validate Code
            </button>
          </>
        )}
      </div>

      {/* Save Dialog */}
      {showSaveDialog && (
        <div className="save-dialog">
          <h4>Save Strategy</h4>
          <div className="form-group">
            <label>Strategy Name:</label>
            <input
              type="text"
              value={saveData.name}
              onChange={(e) => setSaveData({...saveData, name: e.target.value})}
              placeholder="My Trading Strategy"
            />
          </div>
          <div className="form-group">
            <label>Description:</label>
            <textarea
              value={saveData.description}
              onChange={(e) => setSaveData({...saveData, description: e.target.value})}
              placeholder="Strategy description..."
              rows="3"
            />
          </div>
          <div className="form-group">
            <label>Tags (comma-separated):</label>
            <input
              type="text"
              value={saveData.tags}
              onChange={(e) => setSaveData({...saveData, tags: e.target.value})}
              placeholder="momentum, trend-following, SPY"
            />
          </div>
          <div className="dialog-actions">
            <button className="btn btn-primary" onClick={saveStrategy}>
              Save
            </button>
            <button 
              className="btn btn-secondary" 
              onClick={() => setShowSaveDialog(false)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Saved Strategies */}
      <div className="saved-strategies">
        <h4>Your Strategies ({strategies.length})</h4>
        {strategies.length > 0 ? (
          <div className="strategies-grid">
            {strategies.slice(0, 5).map(strategy => (
              <div key={strategy.id} className="strategy-card">
                <h5>{strategy.name}</h5>
                <p className="strategy-description">
                  {strategy.description || 'No description'}
                </p>
                <div className="strategy-meta">
                  <span className="strategy-date">
                    {new Date(strategy.created_at).toLocaleDateString()}
                  </span>
                  <span className="strategy-version">v{strategy.version}</span>
                </div>
                <div className="strategy-tags">
                  {strategy.tags?.slice(0, 3).map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
                <button 
                  className="btn btn-sm btn-outline"
                  onClick={() => loadStrategy(strategy.id)}
                >
                  Load
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-strategies">No saved strategies yet.</p>
        )}
      </div>

      {/* Templates */}
      <div className="strategy-templates">
        <h4>Strategy Templates ({templates.length})</h4>
        {templates.length > 0 ? (
          <div className="templates-grid">
            {templates.slice(0, 3).map(template => (
              <div key={template.id} className="template-card">
                <h5>{template.name}</h5>
                <p>{template.description}</p>
                <span className="usage-count">Used {template.usage_count} times</span>
                <button className="btn btn-sm btn-primary">
                  Use Template
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-templates">No templates available.</p>
        )}
      </div>
    </div>
  );
};

export default StrategyManager;
