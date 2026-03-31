"use client";

const solutions = [
  {
    title: "Telecom Infrastructure",
    description: "Monitor and analyze energy consumption across distributed telecom sites, cell towers, and data centers with secure, offline intelligence.",
    icon: "M8.288 15.038a5.25 5.25 0 017.424 0M5.106 11.856c3.807-3.808 9.98-3.808 13.788 0M1.924 8.674c5.565-5.565 14.587-5.565 20.152 0M12.53 18.22l-.53.53-.53-.53a.75.75 0 011.06 0z",
  },
  {
    title: "Distributed Energy Systems",
    description: "Gain insights into solar, wind, battery storage, and microgrid performance without exposing sensitive operational data to external services.",
    icon: "M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z",
  },
  {
    title: "On-Prem Analytics Environments",
    description: "Deploy AI-powered analytics in air-gapped or security-restricted environments where cloud connectivity is not permitted.",
    icon: "M5.25 14.25h13.5m-13.5 0a3 3 0 01-3-3m3 3a3 3 0 100 6h13.5a3 3 0 100-6m-16.5-3a3 3 0 013-3h13.5a3 3 0 013 3m-19.5 0a4.5 4.5 0 01.9-2.7L5.737 5.1a3.375 3.375 0 012.7-1.35h7.126c1.062 0 2.062.5 2.7 1.35l2.587 3.45a4.5 4.5 0 01.9 2.7m0 0a3 3 0 01-3 3m0 3h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008zm-3 6h.008v.008h-.008v-.008zm0-6h.008v.008h-.008v-.008z",
  },
];

export default function EnergySolutions() {
  return (
    <section id="solutions" className="px-6 py-20 sm:px-8 sm:py-24 md:py-32 lg:px-12">
      <div className="mx-auto max-w-6xl">
        <div className="mb-16 text-center sm:mb-20">
          <h2 className="mb-4 text-3xl font-light sm:text-4xl md:text-5xl">
            Solutions for{" "}
            <span className="bg-gradient-to-r from-[#5EEAD4] to-[#14b8a6] bg-clip-text text-transparent">
              Energy-Driven Organizations
            </span>
          </h2>
          <p className="mx-auto max-w-2xl text-lg text-white/50">
            Purpose-built for industries where data security and operational insight are paramount
          </p>
        </div>

        <div className="space-y-6">
          {solutions.map((solution) => (
            <div key={solution.title} className="group relative rounded-2xl border border-white/5 bg-[#1a1a1a] p-8 transition-all duration-300 hover:border-[#5EEAD4]/30 hover:shadow-[0_0_40px_rgba(94,234,212,0.08)] sm:p-10">
              <div className="flex flex-col gap-6 md:flex-row md:items-center">
                <div className="flex h-16 w-16 flex-shrink-0 items-center justify-center rounded-xl border border-[#5EEAD4]/30 bg-[#5EEAD4]/10 text-[#5EEAD4] transition-transform duration-300 group-hover:scale-110">
                  <svg className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path strokeLinecap="round" strokeLinejoin="round" d={solution.icon} />
                  </svg>
                </div>

                <div className="flex-1">
                  <h3 className="mb-2 text-xl font-medium text-white sm:text-2xl">{solution.title}</h3>
                  <p className="text-base leading-relaxed text-white/60 sm:text-lg">{solution.description}</p>
                </div>

                <div className="flex-shrink-0">
                  <a href="#architecture" className="group/btn flex items-center gap-2 text-[#5EEAD4] transition-colors duration-300 hover:text-white">
                    <span className="text-sm font-medium">Learn more</span>
                    <svg className="h-4 w-4 transition-transform duration-300 group-hover/btn:translate-x-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                    </svg>
                  </a>
                </div>
              </div>

              <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-r from-[#5EEAD4]/5 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
