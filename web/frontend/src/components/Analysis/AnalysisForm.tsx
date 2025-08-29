import React, { useState, useEffect } from 'react';
import { Play } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { apiService } from '../../services/api';
import type { AnalystConfig, LLMProvider, AnalysisSession } from '../../types';

interface AnalysisFormData {
  company: string;
  trade_date: string;
  selected_analysts: string[];
  research_depth: string;
  llm_provider: string;
  llm_model: string;
}

export const AnalysisForm: React.FC = () => {
  const { setCurrentSession, setLoading, setError } = useAppStore();
  const [analysts, setAnalysts] = useState<AnalystConfig[]>([]);
  const [llmProviders, setLLMProviders] = useState<LLMProvider[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [formData, setFormData] = useState<AnalysisFormData>({
    company: 'TSLA',
    trade_date: new Date().toISOString().split('T')[0],
    selected_analysts: ['market', 'social', 'news', 'fundamentals'],
    research_depth: '3',
    llm_provider: 'openai',
    llm_model: 'gpt-4o-mini'
  });

  const selectedProvider = llmProviders.find(p => p.id === formData.llm_provider);
  const availableModels = selectedProvider?.models?.map(m => m.id) || [];

  const handleAnalystToggle = (analystId: string) => {
    setFormData(prev => ({
      ...prev,
      selected_analysts: prev.selected_analysts.includes(analystId)
        ? prev.selected_analysts.filter(id => id !== analystId)
        : [...prev.selected_analysts, analystId]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.selected_analysts.length === 0) {
      setError?.('Please select at least one analyst');
      return;
    }
    
    setIsSubmitting(true);
    setLoading?.('analysis', true);
    setError?.(null);

    try {
      const response = await apiService.startAnalysis(formData);
      
      // Create a minimal AnalysisSession object
      const session: AnalysisSession = {
        session_id: response.session_id,
        company: formData.company,
        trade_date: formData.trade_date,
        status: 'running',
        selected_analysts: formData.selected_analysts,
        llm_provider: formData.llm_provider,
        model: formData.llm_model,
        research_depth: parseInt(formData.research_depth),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      setCurrentSession?.(session);
    } catch (error) {
      setError?.(error instanceof Error ? error.message : 'Failed to start analysis');
    } finally {
      setIsSubmitting(false);
      setLoading?.('analysis', false);
    }
  };

  const getResearchDepthLabel = (depth: number) => {
    if (depth <= 2) return 'Quick';
    if (depth <= 5) return 'Standard';
    if (depth <= 7) return 'Deep';
    return 'Comprehensive';
  };

  // Group analysts by team
  const analystsByTeam = analysts.reduce((acc, analyst) => {
    if (!acc[analyst.team]) {
      acc[analyst.team] = [];
    }
    acc[analyst.team].push(analyst);
    return acc;
  }, {} as Record<string, AnalystConfig[]>);

  useEffect(() => {
    const loadConfig = async () => {
      try {
        const [analystsData, providersData] = await Promise.all([
          apiService.getAnalysts(),
          apiService.getLLMProviders()
        ]);
        
        setAnalysts(analystsData);
        setLLMProviders(providersData);
      } catch (error) {
        console.error('Failed to load configuration:', error);
      }
    };
    
    loadConfig();
  }, []);

  return (
    <div className="bg-white rounded-lg shadow-lg p-8 max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">TradingAgents Analysis</h1>
        <p className="text-gray-600">Multi-Agent LLM Financial Trading Framework</p>
        <div className="mt-4 text-sm text-gray-500">
          <span className="font-medium">Workflow:</span> Analyst Team → Research Team → Trader → Risk Management → Portfolio Management
        </div>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Step 1: Ticker Symbol */}
        <div className="border border-blue-200 rounded-lg p-6 bg-blue-50">
          <h3 className="text-lg font-semibold text-blue-800 mb-4">Step 1: Ticker Symbol</h3>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter the ticker symbol to analyze
            </label>
            <input
              type="text"
              value={formData.company}
              onChange={(e) => setFormData(prev => ({ ...prev, company: e.target.value.toUpperCase() }))}
              className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg font-mono"
              placeholder="e.g., TSLA, AAPL, SPY"
              required
            />
            <p className="text-sm text-gray-500 mt-1">Default: TSLA</p>
          </div>
        </div>

        {/* Step 2: Analysis Date */}
        <div className="border border-blue-200 rounded-lg p-6 bg-blue-50">
          <h3 className="text-lg font-semibold text-blue-800 mb-4">Step 2: Analysis Date</h3>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter the analysis date (YYYY-MM-DD)
            </label>
            <input
              type="date"
              value={formData.trade_date}
              onChange={(e) => setFormData(prev => ({ ...prev, trade_date: e.target.value }))}
              className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <p className="text-sm text-gray-500 mt-1">Default: {new Date().toISOString().split('T')[0]}</p>
          </div>
        </div>

        {/* Step 3: Analysts Team */}
        <div className="border border-blue-200 rounded-lg p-6 bg-blue-50">
          <h3 className="text-lg font-semibold text-blue-800 mb-4">Step 3: Analysts Team</h3>
          <p className="text-sm text-gray-600 mb-4">Select which analysts to include in your analysis team</p>
          
          {Object.entries(analystsByTeam).map(([team, teamAnalysts]) => (
            <div key={team} className="mb-6">
              <h4 className="font-medium text-gray-800 mb-3 capitalize">{team} Team</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {teamAnalysts.map((analyst) => (
                  <label key={analyst.id} className="flex items-start space-x-3 p-3 border border-gray-200 rounded-md hover:bg-gray-50 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.selected_analysts.includes(analyst.id)}
                      onChange={() => handleAnalystToggle(analyst.id)}
                      className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <div>
                      <div className="font-medium text-gray-800">{analyst.name}</div>
                      <div className="text-sm text-gray-600">{analyst.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          ))}
          
          {analysts.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <p>Loading analysts...</p>
            </div>
          )}
          
          {formData.selected_analysts.length > 0 && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
              <p className="text-green-800 font-medium">
                Selected analysts: {formData.selected_analysts.map(id => 
                  analysts.find(a => a.id === id)?.name
                ).filter(Boolean).join(', ')}
              </p>
            </div>
          )}
        </div>

        {/* Step 4: Research Depth */}
        <div className="border border-blue-200 rounded-lg p-6 bg-blue-50">
          <h3 className="text-lg font-semibold text-blue-800 mb-4">Step 4: Research Depth</h3>
          <p className="text-sm text-gray-600 mb-4">Select your research depth level</p>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Research Depth: {formData.research_depth} ({getResearchDepthLabel(parseInt(formData.research_depth))})
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={formData.research_depth}
              onChange={(e) => setFormData(prev => ({ ...prev, research_depth: e.target.value }))}
              className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-2">
              <span>Quick (1)</span>
              <span>Standard (3-5)</span>
              <span>Deep (6-7)</span>
              <span>Comprehensive (8-10)</span>
            </div>
          </div>
        </div>

        {/* Step 5: LLM Provider */}
        <div className="border border-blue-200 rounded-lg p-6 bg-blue-50">
          <h3 className="text-lg font-semibold text-blue-800 mb-4">Step 5: LLM Provider</h3>
          <p className="text-sm text-gray-600 mb-4">Select which service to use</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {llmProviders.map((provider) => (
              <label key={provider.id} className="flex items-center space-x-3 p-4 border border-gray-200 rounded-md hover:bg-gray-50 cursor-pointer">
                <input
                  type="radio"
                  name="llmProvider"
                  value={provider.id}
                  checked={formData.llm_provider === provider.id}
                  onChange={(e) => setFormData(prev => ({ ...prev, llm_provider: e.target.value }))}
                  className="text-blue-600 focus:ring-blue-500"
                />
                <div>
                  <div className="font-medium text-gray-800">{provider.display_name}</div>
                  <div className="text-sm text-gray-600">{provider.models?.length || 0} models available</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Step 6: Model Selection */}
        <div className="border border-blue-200 rounded-lg p-6 bg-blue-50">
          <h3 className="text-lg font-semibold text-blue-800 mb-4">Step 6: Model Selection</h3>
          <p className="text-sm text-gray-600 mb-4">Select the LLM model for analysis</p>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Analysis Model
            </label>
            <select
              value={formData.llm_model}
              onChange={(e) => setFormData(prev => ({ ...prev, llm_model: e.target.value }))}
              className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {availableModels.map((model) => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>
            <p className="text-sm text-gray-500 mt-1">LLM model used for analysis</p>
          </div>
        </div>

        {/* Submit Button */}
        <div className="text-center">
          <button
            type="submit"
            disabled={isSubmitting}
            className="bg-green-600 text-white py-4 px-8 rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors text-lg font-semibold shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mx-auto"
          >
            {isSubmitting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Starting Analysis...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                🚀 Start TradingAgents Analysis
              </>
            )}
          </button>
          <p className="text-sm text-gray-500 mt-2">
            This will start a real-time multi-agent analysis session
          </p>
        </div>
      </form>
    </div>
  );
};
