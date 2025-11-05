import React from 'react';
import ChatPanel from './components/ChatPanel';
import VizPanel from './components/VizPanel';

function App() {
  return (
    <div className="flex h-screen">
      <div className="w-1/4 border-r">
        <ChatPanel />
      </div>
      <div className="w-3/4">
        <VizPanel />
      </div>
    </div>
  );
}

export default App;
