import React, { useMemo } from 'react';

// Lightweight CSS-based fallback animation resembling moving particles/routes
export default function Canvas3D() {
  const particles = useMemo(() => Array.from({ length: 50 }), []);
  return (
    <div className="w-full h-full relative overflow-hidden">
      {/* Floating car-like shapes */}
      <div className="absolute inset-0">
        {particles.map((_, i) => (
          <span
            key={i}
            className="absolute block w-2 h-2 rounded-full bg-accent/60 animate-[float_6s_ease-in-out_infinite]"
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 6}s`,
              filter: 'blur(0.5px)'
            }}
          />
        ))}
      </div>
      {/* Subtle route lines */}
      <svg className="absolute inset-0 w-full h-full opacity-30" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="rgba(124,58,237,0.2)" />
            <stop offset="100%" stopColor="rgba(16,185,129,0.2)" />
          </linearGradient>
        </defs>
        {[...Array(6)].map((_, i) => (
          <path
            key={i}
            d={`M ${-100 + i * 60} ${50 + i * 40} C ${200 + i * 20} ${10 + i * 30}, ${400 - i * 30} ${90 + i * 20}, 1200 ${20 + i * 35}`}
            stroke="url(#g)"
            strokeWidth="2"
            fill="none"
          />
        ))}
      </svg>
      <style>{`
        @keyframes float { 0%, 100% { transform: translateY(0) } 50% { transform: translateY(-12px) } }
      `}</style>
    </div>
  );
}
