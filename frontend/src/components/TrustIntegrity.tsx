"use client";

export default function TrustIntegrity() {
  return (
    <section className="px-6 py-20 sm:px-8 sm:py-24 md:py-32 lg:px-12">
      <div className="mx-auto max-w-6xl">
        <div className="grid items-center gap-4 lg:grid-cols-2 lg:gap-6">
          <div>
            <h2 className="mb-6 text-3xl font-light leading-tight sm:text-4xl md:text-5xl">
              Trust Built Into{" "}
              <span className="bg-gradient-to-r from-[#5EEAD4] to-[#14b8a6] bg-clip-text text-transparent">
                Every Query
              </span>
            </h2>

            <p className="mb-8 text-lg leading-relaxed text-white/60 sm:text-xl">
              Every question, query, and response is validated, auditable, and constrained by design, ensuring reliable insights without unintended actions.
            </p>

            <a href="#architecture" className="group inline-flex items-center gap-3 rounded-full border border-[#5EEAD4]/50 px-6 py-3 text-[#5EEAD4] transition-all duration-300 hover:bg-[#5EEAD4]/10">
              <span className="font-medium">View System Integrity</span>
              <svg className="h-5 w-5 transition-transform duration-300 group-hover:translate-x-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
              </svg>
            </a>
          </div>

          <div className="relative lg:ml-auto">
            <div className="rounded-2xl border border-white/10 bg-[#1a1a1a] p-8 sm:p-10 lg:-mr-12">
              <div className="space-y-6">
                {[
                  ["User", "Natural language query", "M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"],
                  ["Validation", "Schema and safety checks", "M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"],
                  ["Database", "Read-only execution", "M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125"],
                  ["Explanation", "Clear, auditable results", "M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"],
                ].map(([label, text, icon], index) => (
                  <div key={label}>
                    {index > 0 ? (
                      <div className="flex justify-start pb-6 pl-4">
                        <svg className="h-6 w-6 text-[#5EEAD4]/50" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 13.5L12 21m0 0l-7.5-7.5M12 21V3" />
                        </svg>
                      </div>
                    ) : null}
                    <div className="flex items-center gap-4">
                      <div className="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-xl border border-[#5EEAD4]/30 bg-[#5EEAD4]/10">
                        <svg className="h-7 w-7 text-[#5EEAD4]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                          <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
                        </svg>
                      </div>
                      <div>
                        <p className="font-medium text-white">{label}</p>
                        <p className="text-sm text-white/50">{text}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
