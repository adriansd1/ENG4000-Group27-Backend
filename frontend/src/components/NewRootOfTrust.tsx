"use client";

import { useChat } from "@/lib/ChatContext";

export default function NewRootOfTrust() {
  const { openChat } = useChat();

  return (
    <section id="architecture" className="relative overflow-hidden px-6 py-20 sm:px-8 sm:py-24 md:py-32 lg:px-12">
      <div className="absolute inset-0 bg-gradient-to-b from-[#0d0d0d] via-[#0a1515] to-[#0d0d0d]" />
      <div className="absolute left-0 top-1/2 h-96 w-96 -translate-y-1/2 rounded-full bg-[#5EEAD4]/5 blur-[100px]" />
      <div className="absolute right-0 top-1/2 h-96 w-96 -translate-y-1/2 rounded-full bg-[#14b8a6]/5 blur-[100px]" />

      <div className="relative z-10 mx-auto max-w-4xl text-center">
        <div className="mb-8 inline-flex h-20 w-20 items-center justify-center rounded-2xl border border-[#5EEAD4]/30 bg-[#5EEAD4]/10">
          <svg className="h-10 w-10 text-[#5EEAD4]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
          </svg>
        </div>

        <h2 className="mb-6 text-3xl font-light leading-tight sm:mb-8 sm:text-4xl md:text-5xl lg:text-6xl">
          A New Root of Trust for{" "}
          <span className="bg-gradient-to-r from-[#5EEAD4] to-[#14b8a6] bg-clip-text text-transparent">
            AI Analytics
          </span>
        </h2>

        <p className="mx-auto mb-10 max-w-3xl text-lg leading-relaxed text-white/60 sm:text-xl">
          By keeping data local, enforcing strict safeguards, and making reasoning visible, the system establishes a foundation for responsible AI-driven decision-making.
        </p>

        <button onClick={openChat} className="btn-primary group px-8 py-4 text-base sm:text-lg">
          <span className="h-2 w-2 rounded-full bg-black transition-transform duration-300 group-hover:scale-125" />
          Query the Backend
        </button>
      </div>
    </section>
  );
}
