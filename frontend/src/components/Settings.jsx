import { useState } from 'react';

export default function Settings() {
  const [alpha, setAlpha] = useState(0.5);

  return (
    <div className="flex items-center gap-2 text-sm">
      <label className="text-slate-300">Alpha</label>
      <input
        type="range"
        min="0"
        max="1"
        step="0.1"
        value={alpha}
        onChange={(event) => setAlpha(Number(event.target.value))}
        className="accent-emerald-500"
      />
      <span className="w-8 text-right text-slate-400">{alpha.toFixed(1)}</span>
    </div>
  );
}

