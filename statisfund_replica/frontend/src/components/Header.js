import React from 'react';
import './Header.css';

const Header = ({ ideasRemaining }) => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo-section">
          <h1 className="logo">Statis Fund</h1>
          <span className="logo-subtitle">Replica</span>
        </div>
        
        <nav className="nav-links">
          <button className="nav-link" style={{background: 'none', border: 'none', color: 'inherit', textDecoration: 'underline', cursor: 'pointer'}}>Login / Register</button>
          <button className="nav-link" style={{background: 'none', border: 'none', color: 'inherit', textDecoration: 'underline', cursor: 'pointer'}}>Submit Feedback</button>
        </nav>
      </div>
      
      <div className="ideas-banner">
        <span className="ideas-text">
          💡 <strong>{ideasRemaining}</strong> ideas remaining
        </span>
        <span className="register-prompt">
          Real market data via yfinance + Alpha Vantage • Register for free to get 100 free ideas per month (only during Alpha).
        </span>
      </div>
    </header>
  );
};

export default Header;
