import React from 'react';
import { useChatStore } from '../store/chatStore';
import VegaChart from './VegaChart';

export default function VizPanel() {
  const { currentVegaSpec, isLoading } = useChatStore();

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <div className="bg-gray-800 text-white p-4">
        <h1 className="text-xl font-bold">Visualization</h1>
        <p className="text-sm opacity-90">Interactive charts and graphs</p>
      </div>

      <div className="flex-1 overflow-y-auto p-1 flex items-center justify-center">
        {isLoading && (
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading visualization...</p>
          </div>
        )}

        {!isLoading && !currentVegaSpec && (
          <div className="text-center text-gray-500">
            <p className="mt-4 text-lg">No visualization yet</p>
            <p className="text-sm mt-2">Ask a question to see a chart</p>
          </div>
        )}

        {!isLoading && currentVegaSpec && (
          <div className="bg-white rounded-lg shadow-lg p-1">
            <VegaChart spec={currentVegaSpec} />
          </div>
        )}
      </div>
    </div>
  );
}
