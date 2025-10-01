import React, { Suspense, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

// Lightweight, optional 3D canvas using dynamic import to avoid heavy bundle on first paint
const Canvas3D = React.lazy(() => import('../sections/Canvas3D'));

export default function Landing() {
  const navigate = useNavigate();
  const featuresRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    // Simple scroll-driven reveal using IntersectionObserver (GSAP optional later)
    const el = featuresRef.current;
    if (!el) return;
    const items = Array.from(el.querySelectorAll('[data-reveal]')) as HTMLElement[];
    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add('opacity-100', 'translate-y-0');
          }
        }
      },
      { threshold: 0.2 }
    );
    items.forEach((i) => io.observe(i));
    return () => io.disconnect();
  }, []);

  return (
    <div id="main" className="min-h-screen bg-background relative overflow-hidden">
      {/* Animated gradient background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute -inset-[20%] bg-[radial-gradient(circle_at_20%_20%,rgba(124,58,237,0.25),transparent_40%),radial-gradient(circle_at_80%_30%,rgba(16,185,129,0.15),transparent_40%),radial-gradient(circle_at_50%_80%,rgba(148,163,184,0.12),transparent_50%)] animate-[fadeIn_1s_ease]" />
      </div>

      {/* Hero Section */}
      <section id="hero" className="relative h-screen flex items-center justify-center text-center px-6">
        {/* 3D canvas in the back */}
        <div className="absolute inset-0 -z-10 opacity-80">
          <Suspense fallback={<div className="w-full h-full" />}> 
            <Canvas3D />
          </Suspense>
        </div>

        <div className="max-w-3xl mx-auto">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-text-primary"
          >
            Compare. Choose. Ride.
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
            className="mt-6 text-lg sm:text-xl text-text-secondary"
          >
            The only ride price comparison you’ll ever need.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className="mt-10"
          >
            <button
              onClick={() => navigate('/rides')}
              className="px-8 py-3 rounded-xl bg-accent text-white font-semibold shadow-card hover:shadow-card-hover transition-transform active:scale-[0.98]"
            >
              Start Comparing
            </button>
          </motion.div>

          {/* Scroll hint */}
          <div className="absolute bottom-8 left-0 right-0 flex flex-col items-center text-text-secondary">
            <svg className="h-6 w-6 animate-bounce" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
            </svg>
            <span className="text-sm mt-1">Scroll to explore</span>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative py-24 md:py-32" ref={featuresRef}>
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { title: 'Cheapest Rides', desc: 'We compare across providers to get you the best price every time.', icon: (
                <svg className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .843-3 1.882S10.343 11.764 12 11.764s3 .843 3 1.882S13.657 15.529 12 15.529m0-11.764v1.176m0 10.588V17"/></svg>
              )},
              { title: 'Fastest ETA', desc: 'Know which ride will reach you the fastest with real-time data.', icon: (
                <svg className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              )},
              { title: 'Eco Insights', desc: 'See your ride’s CO₂ impact and pick greener options.', icon: (
                <svg className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/></svg>
              )},
            ].map((f, i) => (
              <div
                key={f.title}
                data-reveal
                className="opacity-0 translate-y-4 transition-all duration-700 bg-surface border border-border rounded-2xl p-6"
                style={{ transitionDelay: `${i * 100}ms` }}
              >
                <div className="text-accent">{f.icon}</div>
                <h3 className="mt-4 text-xl font-semibold text-text-primary">{f.title}</h3>
                <p className="mt-2 text-text-secondary">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section id="cta-section" className="py-24 md:py-32 text-center">
        <h2 className="text-4xl md:text-5xl font-extrabold text-text-primary">Your Ride, Your Choice</h2>
        <button
          onClick={() => navigate('/rides')}
          className="mt-8 px-8 py-3 rounded-xl bg-accent text-white font-semibold shadow-card hover:shadow-card-hover animate-pulse"
        >
          Compare Now
        </button>
      </section>
    </div>
  );
}
