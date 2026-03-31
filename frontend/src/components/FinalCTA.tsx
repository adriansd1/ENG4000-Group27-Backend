"use client";

import { useState } from "react";
import { useChat } from "@/lib/ChatContext";

export default function FinalCTA() {
  const [isHovered, setIsHovered] = useState(false);
  const { openChat } = useChat();

  return (
    <section className="relative overflow-hidden px-6 py-24 sm:px-8 sm:py-32 md:py-40 lg:px-12">
      <div className="absolute inset-0 bg-gradient-to-t from-[#0a1515] via-[#0d0d0d] to-[#0d0d0d]" />
      <div className="absolute bottom-0 left-1/2 h-[300px] w-[600px] -translate-x-1/2 rounded-full bg-[#5EEAD4]/10 blur-[120px]" />

      <div className="relative z-10 mx-auto max-w-3xl text-center">
        <h2 className="mb-8 text-3xl font-light leading-tight sm:text-4xl md:text-5xl lg:text-6xl">
          Build Safer, Smarter{" "}
          <span className="bg-gradient-to-r from-[#5EEAD4] to-[#14b8a6] bg-clip-text text-transparent">
            Energy Intelligence
          </span>
        </h2>

        <button
          onClick={openChat}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          className="btn-primary group px-10 py-5 text-lg sm:px-14 sm:py-6 sm:text-xl"
        >
          <span className={`h-3 w-3 rounded-full bg-black transition-all duration-300 ${isHovered ? "scale-125" : ""}`} />
          Open the Query Workspace
        </button>
      </div>
    </section>
  );
}
