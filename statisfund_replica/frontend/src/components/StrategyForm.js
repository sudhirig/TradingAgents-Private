import React, { useState } from 'react';

const StrategyForm = ({ onGenerate, isGenerating, ideasRemaining }) => {
  const [formData, setFormData] = useState({
    description: 'if the 20D MA of SPY is increasing, buy UPRO, else sell to cash',
    start_date: '2024-08-22',
    end_date: '2024-08-29',
    mode: 'Interday',
    ai_model: 'GPT-4.1-mini'
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (ideasRemaining <= 0) {
      alert('Ideas limit reached. Register for free to get 100 free ideas per month.');
      return;
    }
    onGenerate(formData);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <form className="strategy-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="description">Define Strategy:</label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Describe your trading strategy..."
          required
        />
      </div>

      <div className="date-inputs">
        <div className="form-group">
          <label htmlFor="start_date">Start Date:</label>
          <input
            type="date"
            id="start_date"
            name="start_date"
            value={formData.start_date}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="end_date">End Date:</label>
          <input
            type="date"
            id="end_date"
            name="end_date"
            value={formData.end_date}
            onChange={handleChange}
            required
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="mode">Mode:</label>
        <select
          id="mode"
          name="mode"
          value={formData.mode}
          onChange={handleChange}
        >
          <option value="Interday">Interday</option>
          <option value="Intraday">Intraday</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="ai_model">Select AI Model:</label>
        <select
          id="ai_model"
          name="ai_model"
          value={formData.ai_model}
          onChange={handleChange}
        >
          <option value="GPT-4.1-mini">GPT-4.1-mini (fast)</option>
          <option value="GPT-4o">GPT-4o</option>
        </select>
        <small style={{ color: '#6c757d', fontSize: '0.85rem' }}>
          Real market data only - No synthetic fallbacks. Register for free to access more AI models.
        </small>
      </div>

      <button 
        type="submit" 
        className="btn btn-primary"
        disabled={isGenerating || ideasRemaining <= 0}
      >
        {isGenerating ? 'Generating Strategy...' : 'Run Backtest'}
      </button>

      <div className="ideas-counter">
        💡 <span className="highlight">{ideasRemaining}</span> ideas remaining
        <br />
        <small>Register for free to get 100 free ideas per month (only during Alpha).</small>
      </div>
    </form>
  );
};

export default StrategyForm;
