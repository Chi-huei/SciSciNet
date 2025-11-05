import React from 'react';
import { VegaEmbed } from 'react-vega';

interface VegaChartProps {
  spec: any;
}

export default function VegaChart({ spec }: VegaChartProps) {
  if (!spec) {
    return null;
  }

  const options = {
    actions: false,
    width: 1200
    
  };

  return (
    <div className="w-full flex justify-center">
      <VegaEmbed spec={spec} options={options} />
    </div>
  );
}
