"use client";

export default function IntroducingSystem() {
  return (
    <section className="relative px-6 py-20 sm:px-8 sm:py-24 md:py-32 lg:px-12">
      <div className="absolute left-0 right-0 top-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

      <div className="mx-auto max-w-4xl text-center">
        <h2 className="mb-6 text-3xl font-light leading-tight sm:mb-8 sm:text-4xl md:text-5xl lg:text-6xl">
          Introducing the{" "}
          <span className="bg-gradient-to-r from-[#5EEAD4] to-[#14b8a6] bg-clip-text text-transparent">
            Energy Expert System
          </span>
        </h2>

        <p className="mx-auto mb-10 max-w-3xl text-lg leading-relaxed text-white/60 sm:text-xl">
          A frontend layer for the current FastAPI backend. It keeps the presentation polished while exposing the backend&apos;s real flow: question in, validated SQL out, rows returned, and analysis written back to the user.
        </p>

        <a href="#how-it-works" className="group inline-flex items-center gap-3 text-[#5EEAD4] transition-colors duration-300 hover:text-white">
          <span className="text-lg font-medium">Learn How It Works</span>
          <svg className="h-5 w-5 transition-transform duration-300 group-hover:translate-x-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
          </svg>
        </a>
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
    </section>
  );
}
