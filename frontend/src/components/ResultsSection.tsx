"use client";

export default function ResultsSection() {
  return (
    <section className="bg-[#0a0a0a] px-6 py-20 sm:px-8 sm:py-24 md:py-32 lg:px-12">
      <div className="mx-auto max-w-6xl">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          <div className="order-2 lg:order-1">
            <div className="relative">
              <div className="pointer-events-none absolute inset-0 z-10 bg-gradient-to-t from-[#0a0a0a] via-transparent to-transparent" />

              <div className="overflow-hidden rounded-2xl border border-white/10 bg-[#1a1a1a] p-6 font-mono text-sm sm:p-8">
                <div className="mb-6 flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-red-500/60" />
                  <div className="h-3 w-3 rounded-full bg-yellow-500/60" />
                  <div className="h-3 w-3 rounded-full bg-green-500/60" />
                  <span className="ml-4 text-xs text-white/40">response.json</span>
                </div>

                <pre className="overflow-x-auto text-white/70">
{`{
  "question": "List all site names",
  "sql": "SELECT sitename, province
FROM site_metadata
LIMIT 1000",
  "rows": [
    { "sitename": "Toronto-1", "province": "ON" },
    { "sitename": "Vancouver-1", "province": "BC" }
  ],
  "analysis": "The backend returned the
first matching rows and summarized the
result in plain language."
}`}
                </pre>
              </div>
            </div>
          </div>

          <div className="order-1 lg:order-2">
            <h2 className="mb-6 text-3xl font-light leading-tight sm:text-4xl md:text-5xl">
              The Result:{" "}
              <span className="bg-gradient-to-r from-[#5EEAD4] to-[#14b8a6] bg-clip-text text-transparent">
                Verifiable Intelligence
              </span>
            </h2>

            <p className="mb-8 text-lg leading-relaxed text-white/60 sm:text-xl">
              Each response mirrors the backend contract directly: the user question, generated SQL, returned rows, and the analysis text produced by the backend.
            </p>

            <div className="flex flex-wrap gap-4">
              {["Backend-aligned output", "Query visibility", "Row-level evidence"].map((label) => (
                <div key={label} className="flex items-center gap-2 rounded-full border border-white/10 bg-[#1a1a1a] px-4 py-2">
                  <svg className="h-5 w-5 text-[#5EEAD4]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                  <span className="text-sm text-white/70">{label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
