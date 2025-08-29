import React from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const ChartComponent = ({ type = 'line', data, title, height = 300 }) => {
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          color: 'rgba(255, 255, 255, 0.8)',
          font: {
            size: 12
          }
        }
      },
      title: {
        display: title ? true : false,
        text: title,
        color: 'rgba(255, 255, 255, 0.9)',
        font: {
          size: 16,
          weight: 'bold'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: 'rgba(102, 126, 234, 0.5)',
        borderWidth: 1
      }
    },
    scales: type !== 'doughnut' ? {
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.05)',
          borderColor: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.6)'
        }
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.05)',
          borderColor: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.6)'
        }
      }
    } : undefined
  };

  const defaultData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Returns',
        data: [12, 19, 3, 5, 2, 3],
        borderColor: 'rgba(102, 126, 234, 1)',
        backgroundColor: type === 'line' 
          ? 'rgba(102, 126, 234, 0.1)' 
          : 'rgba(102, 126, 234, 0.5)',
        borderWidth: 2,
        tension: 0.4,
        fill: type === 'line'
      }
    ]
  };

  const chartData = data || defaultData;

  return (
    <div className="chart-container" style={{ height: `${height}px` }}>
      {type === 'line' && <Line options={chartOptions} data={chartData} />}
      {type === 'bar' && <Bar options={chartOptions} data={chartData} />}
      {type === 'doughnut' && <Doughnut options={chartOptions} data={chartData} />}
    </div>
  );
};

export default ChartComponent;
