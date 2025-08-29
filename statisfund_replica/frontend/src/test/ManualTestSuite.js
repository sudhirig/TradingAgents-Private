import React, { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import { Button, Card, Input, Badge, LoadingSkeleton } from '../components/design-system';

const ManualTestSuite = () => {
  const { isDarkMode } = useTheme();
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);

  const testLoadingSkeleton = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 3000);
  };

  return (
    <div className="manual-test-suite" style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>🧪 Manual Test Suite - Frontend UI/UX Enhancement</h1>
      
      {/* Theme Status Display */}
      <Card variant="elevated" className="mb-6">
        <h2>🎨 Theme System Test</h2>
        <p><strong>Current Theme:</strong> {isDarkMode ? 'Dark Mode 🌙' : 'Light Mode ☀️'}</p>
        <p><strong>CSS Variables:</strong> Theme-dependent colors should change automatically</p>
        <div className="grid-2">
          <div style={{ 
            background: 'var(--bg-primary)', 
            padding: '1rem', 
            border: '1px solid var(--border-primary)',
            borderRadius: 'var(--radius-md)'
          }}>
            <strong>Primary Background</strong>
            <p style={{ color: 'var(--text-secondary)' }}>Secondary text color</p>
          </div>
          <div style={{ 
            background: 'var(--bg-surface)', 
            padding: '1rem', 
            border: '1px solid var(--border-accent)',
            borderRadius: 'var(--radius-md)'
          }}>
            <strong>Surface Background</strong>
            <p style={{ color: 'var(--text-muted)' }}>Muted text color</p>
          </div>
        </div>
      </Card>

      {/* Button Component Testing */}
      <Card variant="glass" className="mb-6">
        <h2>🔘 Button Component System</h2>
        <div className="grid-3" style={{ gap: '1rem' }}>
          <div>
            <h3>Variants</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <Button variant="primary">Primary</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="gradient">Gradient</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
            </div>
          </div>
          <div>
            <h3>Sizes</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <Button size="sm">Small</Button>
              <Button size="md">Medium</Button>
              <Button size="lg">Large</Button>
            </div>
          </div>
          <div>
            <h3>States</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <Button loading>Loading Button</Button>
              <Button disabled>Disabled Button</Button>
              <Button onClick={() => alert('Click works!')}>Click Test</Button>
            </div>
          </div>
        </div>
      </Card>

      {/* Input Component Testing */}
      <Card variant="outline" className="mb-6">
        <h2>📝 Input Component System</h2>
        <div className="grid-2" style={{ gap: '2rem' }}>
          <div>
            <h3>Variants & States</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <Input 
                label="Default Input" 
                placeholder="Enter text here..." 
                id="input-1"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
              />
              <Input 
                label="Filled Input" 
                variant="filled" 
                placeholder="Filled variant" 
                id="input-2"
              />
              <Input 
                label="Outline Input" 
                variant="outline" 
                placeholder="Outline variant" 
                id="input-3"
              />
              <Input 
                label="Error State" 
                error 
                helperText="This field has an error" 
                id="input-4"
              />
              <Input 
                label="Success State" 
                success 
                helperText="This field is valid" 
                id="input-5"
              />
            </div>
          </div>
          <div>
            <h3>Sizes</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <Input label="Small Input" size="sm" placeholder="Small size" id="input-6" />
              <Input label="Medium Input" size="md" placeholder="Medium size" id="input-7" />
              <Input label="Large Input" size="lg" placeholder="Large size" id="input-8" />
            </div>
          </div>
        </div>
      </Card>

      {/* Badge Component Testing */}
      <Card variant="default" className="mb-6">
        <h2>🏷️ Badge Component System</h2>
        <div className="grid-2" style={{ gap: '2rem' }}>
          <div>
            <h3>Variants</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              <Badge variant="default">Default</Badge>
              <Badge variant="primary">Primary</Badge>
              <Badge variant="success">Success</Badge>
              <Badge variant="warning">Warning</Badge>
              <Badge variant="error">Error</Badge>
              <Badge variant="outline">Outline</Badge>
            </div>
          </div>
          <div>
            <h3>Sizes</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center' }}>
              <Badge size="sm">Small</Badge>
              <Badge size="md">Medium</Badge>
              <Badge size="lg">Large</Badge>
            </div>
          </div>
        </div>
      </Card>

      {/* Card Component Testing */}
      <div className="grid-2 mb-6" style={{ gap: '1rem' }}>
        <Card variant="default" hover>
          <h3>Default Card (Hover Effect)</h3>
          <p>This card has hover effects enabled. Hover over it to see the transformation.</p>
        </Card>
        <Card variant="glass">
          <h3>Glass Card</h3>
          <p>This card uses backdrop blur and glass morphism effects.</p>
        </Card>
      </div>

      {/* Loading Skeleton Testing */}
      <Card variant="elevated" className="mb-6">
        <h2>⚡ Loading Skeleton System</h2>
        <Button onClick={testLoadingSkeleton} className="mb-4">
          Test Loading Skeletons (3 seconds)
        </Button>
        
        {loading ? (
          <div className="grid-3" style={{ gap: '1rem' }}>
            <LoadingSkeleton type="card" />
            <LoadingSkeleton type="text" lines={4} />
            <LoadingSkeleton type="chart" />
          </div>
        ) : (
          <div className="grid-3" style={{ gap: '1rem' }}>
            <Card>
              <h4>Actual Card Content</h4>
              <p>This is what shows after loading completes</p>
            </Card>
            <div>
              <h4>Text Content</h4>
              <p>Line 1 of actual content</p>
              <p>Line 2 of actual content</p>
              <p>Line 3 of actual content</p>
              <p>Line 4 of actual content</p>
            </div>
            <div style={{ 
              height: '200px', 
              background: 'var(--gradient-primary)', 
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white'
            }}>
              📊 Chart Content
            </div>
          </div>
        )}
      </Card>

      {/* Responsive Grid Testing */}
      <Card variant="outline" className="mb-6">
        <h2>📱 Responsive Grid System</h2>
        <p>Resize your browser window to test responsive behavior</p>
        
        <h3>Grid-2 (2 columns on large screens)</h3>
        <div className="grid-2 mb-4">
          {[1, 2, 3, 4].map(i => (
            <Card key={i} variant="default">
              <strong>Grid Item {i}</strong>
              <p>Responsive grid item that stacks on mobile</p>
            </Card>
          ))}
        </div>
        
        <h3>Grid-4 (4 columns on large screens)</h3>
        <div className="grid-4">
          {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
            <Card key={i} variant="glass">
              <strong>Item {i}</strong>
              <p>Auto-fit grid</p>
            </Card>
          ))}
        </div>
      </Card>

      {/* Accessibility Testing */}
      <Card variant="elevated">
        <h2>♿ Accessibility Testing</h2>
        <p><strong>Keyboard Navigation Test:</strong> Use Tab key to navigate through interactive elements</p>
        <p><strong>Screen Reader Test:</strong> All elements should have proper ARIA labels</p>
        <p><strong>Focus Indicators:</strong> Interactive elements should show focus outlines</p>
        
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginTop: '1rem' }}>
          <Button tabIndex="0">Focusable Button 1</Button>
          <Button variant="outline" tabIndex="0">Focusable Button 2</Button>
          <Input placeholder="Focusable Input" id="accessibility-input" />
        </div>
      </Card>
    </div>
  );
};

export default ManualTestSuite;
