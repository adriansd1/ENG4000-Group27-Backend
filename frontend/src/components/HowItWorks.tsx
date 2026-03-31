"use client";

const steps = [
  {
    number: "01",
    title: "Ask a Question",
    description: "Users ask natural-language questions about energy performance or site behavior.",
    icon: (
      <svg className="w-10 h-10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
      </svg>
    ),
  },
  {
    number: "02",
    title: "Secure Local Analysis",
    description: "The system generates safe, schema-aware SQL and executes it locally.",
    icon: (
      <svg className="w-10 h-10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
      </svg>
    ),
  },
  {
    number: "03",
    title: "Clear Insights",
    description: "Results are returned with structured data and an expert-style explanation.",
    icon: (
      <svg className="w-10 h-10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5m.75-9l3-3 2.148 2.148A12.061 12.061 0 0116.5 7.605" />
      </svg>
    ),
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-20 sm:py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-[#0a0a0a]">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16 sm:mb-20">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-light mb-4">
            How It Works
          </h2>
          <p className="text-white/50 text-lg">
            Three simple steps to energy intelligence
          </p>
        </div>
        
        {/* Steps */}
        <div className="relative">
          {/* Connection line */}
          <div className="hidden lg:block absolute left-1/2 top-16 bottom-0 w-px bg-gradient-to-b from-[#5EEAD4]/50 via-[#5EEAD4]/20 to-transparent" />
          
          <div className="space-y-12 lg:space-y-0 lg:grid lg:grid-cols-3 lg:gap-8 lg:gap-x-16">
            {steps.map((step, index) => (
              <div key={index} className="relative flex flex-col">
                {/* Arrow for mobile/tablet */}
                {index < steps.length - 1 && (
                  <div className="lg:hidden flex justify-center py-8">
                    <svg className="w-6 h-6 text-[#5EEAD4]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 13.5L12 21m0 0l-7.5-7.5M12 21V3" />
                    </svg>
                  </div>
                )}
                
                {/* Step Card */}
                <div className="relative bg-[#1a1a1a] border border-white/5 rounded-2xl p-10 text-center group hover:border-[#5EEAD4]/30 transition-all duration-300 h-full flex flex-col">
                  {/* Step number */}
                  <div className="absolute -top-5 left-1/2 -translate-x-1/2 bg-[#5EEAD4] text-black text-sm font-bold px-4 py-1.5 rounded-full">
                    {step.number}
                  </div>
                  
                  {/* Icon */}
                  <div className="text-[#5EEAD4] flex justify-center mb-8 mt-6">
                    {step.icon}
                  </div>
                  
                  {/* Title */}
                  <h3 className="text-xl sm:text-2xl font-medium mb-4 text-white">
                    {step.title}
                  </h3>
                  
                  {/* Description */}
                  <p className="text-white/60 text-base leading-relaxed flex-grow">
                    {step.description}
                  </p>
                </div>
                
                {/* Arrow for desktop */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:flex absolute -right-12 top-1/2 -translate-y-1/2 z-10">
                    <svg className="w-8 h-8 text-[#5EEAD4]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                    </svg>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
