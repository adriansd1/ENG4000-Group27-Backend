"use client";

export default function ProblemStatement() {
  return (
    <section className="py-20 sm:py-24 md:py-32 px-6 sm:px-8 lg:px-12 relative">
      {/* Subtle top divider */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
      
      <div className="max-w-3xl mx-auto text-center">
        <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-light mb-6 sm:mb-8 leading-tight">
          Energy Data Is Complex.{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#5EEAD4] to-[#14b8a6]">
            Access Shouldn&apos;t Be.
          </span>
        </h2>
        
        <p className="text-white/60 text-lg sm:text-xl leading-relaxed">
          Energy performance data is often locked behind complex schemas, SQL expertise, and restricted cloud policies. Teams need answers fast — without relying on specialized analysts or external AI services.
        </p>
      </div>
      
      {/* Subtle bottom divider */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-32 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
    </section>
  );
}
