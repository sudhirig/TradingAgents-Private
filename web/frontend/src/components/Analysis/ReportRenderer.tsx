import React from 'react';
import ReactMarkdown from 'react-markdown';
import { FileText, Clock, User, Download } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';

export const ReportRenderer: React.FC = () => {
  const { reports, currentSession } = useAppStore();

  if (!currentSession || reports.length === 0) {
    return (
      <div className="card">
        <div className="flex items-center justify-center h-64 text-gray-500">
          <div className="text-center">
            <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Reports Available</h3>
            <p className="text-gray-600">Reports will appear here as agents complete their analysis</p>
          </div>
        </div>
      </div>
    );
  }

  const groupedReports = reports.reduce((acc, report) => {
    if (!acc[report.agent]) {
      acc[report.agent] = [];
    }
    acc[report.agent].push(report);
    return acc;
  }, {} as Record<string, typeof reports>);

  const downloadReport = (report: typeof reports[0]) => {
    const blob = new Blob([report.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${report.agent}_${report.section_name}_${report.timestamp}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <FileText className="h-6 w-6 text-gray-600" />
          <h2 className="text-2xl font-semibold text-gray-900">Analysis Reports</h2>
          <span className="badge badge-info">{reports.length}</span>
        </div>
      </div>

      {Object.entries(groupedReports).map(([agent, agentReports]) => (
        <div key={agent} className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <User className="h-5 w-5 text-gray-600" />
              <h3 className="text-xl font-semibold text-gray-900">{agent}</h3>
              <span className="badge badge-success">{agentReports.length} reports</span>
            </div>
          </div>

          <div className="space-y-4">
            {agentReports.map((report, index) => (
              <div key={index} className="border rounded-lg p-4 bg-gray-50">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <h4 className="text-lg font-medium text-gray-900 capitalize">
                      {report.section_name.replace(/_/g, ' ')}
                    </h4>
                    <div className="flex items-center space-x-1 text-sm text-gray-500">
                      <Clock className="h-3 w-3" />
                      <span>{new Date(report.timestamp).toLocaleString()}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => downloadReport(report)}
                    className="btn-outline px-3 py-1 text-sm"
                    title="Download report"
                  >
                    <Download className="h-3 w-3 mr-1" />
                    Download
                  </button>
                </div>

                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown
                    components={{
                      h1: ({ children }) => (
                        <h1 className="text-xl font-bold text-gray-900 mb-3">{children}</h1>
                      ),
                      h2: ({ children }) => (
                        <h2 className="text-lg font-semibold text-gray-800 mb-2">{children}</h2>
                      ),
                      h3: ({ children }) => (
                        <h3 className="text-base font-medium text-gray-700 mb-2">{children}</h3>
                      ),
                      p: ({ children }) => (
                        <p className="text-gray-700 mb-3 leading-relaxed">{children}</p>
                      ),
                      ul: ({ children }) => (
                        <ul className="list-disc list-inside text-gray-700 mb-3 space-y-1">{children}</ul>
                      ),
                      ol: ({ children }) => (
                        <ol className="list-decimal list-inside text-gray-700 mb-3 space-y-1">{children}</ol>
                      ),
                      li: ({ children }) => (
                        <li className="text-gray-700">{children}</li>
                      ),
                      strong: ({ children }) => (
                        <strong className="font-semibold text-gray-900">{children}</strong>
                      ),
                      em: ({ children }) => (
                        <em className="italic text-gray-800">{children}</em>
                      ),
                      code: ({ children }) => (
                        <code className="bg-gray-200 text-gray-800 px-1 py-0.5 rounded text-sm font-mono">
                          {children}
                        </code>
                      ),
                      pre: ({ children }) => (
                        <pre className="bg-gray-800 text-gray-100 p-3 rounded-lg overflow-x-auto text-sm font-mono mb-3">
                          {children}
                        </pre>
                      ),
                      blockquote: ({ children }) => (
                        <blockquote className="border-l-4 border-blue-500 pl-4 py-2 mb-3 bg-blue-50 text-gray-700 italic">
                          {children}
                        </blockquote>
                      ),
                      table: ({ children }) => (
                        <div className="overflow-x-auto mb-3">
                          <table className="min-w-full border border-gray-300">{children}</table>
                        </div>
                      ),
                      th: ({ children }) => (
                        <th className="border border-gray-300 px-3 py-2 bg-gray-100 text-left font-semibold text-gray-900">
                          {children}
                        </th>
                      ),
                      td: ({ children }) => (
                        <td className="border border-gray-300 px-3 py-2 text-gray-700">{children}</td>
                      ),
                    }}
                  >
                    {report.content}
                  </ReactMarkdown>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};
