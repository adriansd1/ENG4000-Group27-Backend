"use client";

import { useState } from "react";
import { useChat } from "@/lib/ChatContext";

export default function EnergyHero() {
  const [isHovered, setIsHovered] = useState(false);
  const { openChat } = useChat();

  return (
    <section className="relative flex min-h-[100dvh] items-center overflow-hidden pb-20 pt-32 sm:pb-24 sm:pt-36 md:pb-28 md:pt-40 lg:pt-44">
      <div className="absolute inset-0 bg-gradient-to-br from-[#0d0d0d] via-[#0d0d0d] to-[#0a1a1a]" />

      <div className="relative z-10 mx-auto w-full max-w-7xl px-6 sm:px-8 lg:px-12">
        <div className="grid items-center gap-12 sm:gap-16 lg:grid-cols-2 lg:gap-20">
          <div className="animate-fade-in-up">
            <h1 className="mb-6 text-4xl font-light leading-[1.1] sm:mb-8 sm:text-5xl md:mb-10 md:text-6xl lg:text-7xl xl:text-[90px]">
              Offline AI Integrity
              <br />
              <span className="bg-gradient-to-r from-[#5EEAD4] to-[#14b8a6] bg-clip-text text-transparent">
                Starts Here
              </span>
            </h1>

            <p className="mb-8 max-w-xl text-lg leading-relaxed text-white/70 sm:mb-10 sm:text-xl md:mb-12">
              A styled frontend for the Group 27 backend that turns natural-language questions into validated SQL, tabular results, and clear analysis.
            </p>

            <button
              onClick={openChat}
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
              className="btn-primary group px-8 py-4 text-base sm:px-10 sm:py-5 sm:text-lg"
            >
              <span className={`h-2.5 w-2.5 rounded-full bg-black transition-transform duration-300 ${isHovered ? "scale-125" : ""}`} />
              Ask the Backend
            </button>
          </div>

          <div className="relative mt-12 flex items-center justify-center lg:mt-0">
            <div className="relative h-[300px] w-[300px] sm:h-[400px] sm:w-[400px] md:h-[500px] md:w-[500px] lg:h-[550px] lg:w-[550px]">
              <div className="absolute inset-0 animate-float">
                <svg viewBox="0 0 400 400" className="h-full w-full" style={{ animationDuration: "20s" }}>
                  <defs>
                    <linearGradient id="meshGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#5EEAD4" stopOpacity="0.6" />
                      <stop offset="50%" stopColor="#14b8a6" stopOpacity="0.4" />
                      <stop offset="100%" stopColor="#0d9488" stopOpacity="0.2" />
                    </linearGradient>
                    <filter id="glow">
                      <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                      <feMerge>
                        <feMergeNode in="coloredBlur" />
                        <feMergeNode in="SourceGraphic" />
                      </feMerge>
                    </filter>
                  </defs>

                  <circle cx="200" cy="200" r="180" fill="none" stroke="url(#meshGradient)" strokeWidth="0.5" opacity="0.5" />
                  <circle cx="200" cy="200" r="160" fill="none" stroke="url(#meshGradient)" strokeWidth="0.5" opacity="0.4" />
                  <circle cx="200" cy="200" r="140" fill="none" stroke="url(#meshGradient)" strokeWidth="0.5" opacity="0.3" />

                  {[...Array(12)].map((_, index) => (
                    <ellipse
                      key={`h-${index}`}
                      cx="200"
                      cy="200"
                      rx="150"
                      ry={150 * Math.cos((index * Math.PI) / 12)}
                      fill="none"
                      stroke="url(#meshGradient)"
                      strokeWidth="0.8"
                      opacity={0.3 + (index % 3) * 0.1}
                      filter="url(#glow)"
                    />
                  ))}

                  {[...Array(24)].map((_, index) => (
                    <ellipse
                      key={`v-${index}`}
                      cx="200"
                      cy="200"
                      rx={150 * Math.cos((index * Math.PI) / 24)}
                      ry="150"
                      fill="none"
                      stroke="url(#meshGradient)"
                      strokeWidth="0.5"
                      opacity={0.2 + (index % 4) * 0.05}
                      transform={`rotate(${index * 7.5} 200 200)`}
                    />
                  ))}

                  <circle cx="200" cy="200" r="60" fill="url(#meshGradient)" opacity="0.1" filter="url(#glow)" />

                  {[...Array(8)].map((_, index) => (
                    <circle
                      key={`p-${index}`}
                      cx={200 + 120 * Math.cos((index * Math.PI * 2) / 8)}
                      cy={200 + 120 * Math.sin((index * Math.PI * 2) / 8)}
                      r="3"
                      fill="#5EEAD4"
                      opacity="0.6"
                      className="animate-pulse"
                    />
                  ))}
                </svg>
              </div>

              <div className="absolute inset-0 bg-gradient-radial from-[#5EEAD4]/10 via-transparent to-transparent blur-3xl" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
