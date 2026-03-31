"use client";

import Link from "next/link";
import Image from "next/image";
import logoImage from "@/app/PLCAI-logo.webp";

export default function EnergyFooter() {
  return (
    <footer className="border-t border-white/5 bg-[#0a0a0a] px-6 py-16 sm:px-8 sm:py-20 lg:px-12">
      <div className="mx-auto max-w-6xl">
        <div className="mb-12 grid grid-cols-1 gap-12 md:grid-cols-3">
          <div className="md:col-span-2">
            <Link href="/" className="group mb-4 flex items-center gap-3">
              <Image
                src={logoImage}
                alt="PLCAI"
                className="h-10 w-auto transition-transform duration-300 group-hover:scale-105 sm:h-12"
                width={120}
                height={48}
              />
            </Link>
            <p className="max-w-sm text-sm leading-relaxed text-white/50">
              A Next.js frontend for the ENG4000 Group 27 backend. Designed to present real query results in a cleaner, more transparent interface.
            </p>
          </div>

          <div>
            <h4 className="mb-4 font-medium text-white">Product</h4>
            <ul className="space-y-3">
              <li><Link href="#features" className="text-sm text-white/50 transition-colors duration-200 hover:text-white">Features</Link></li>
              <li><Link href="#how-it-works" className="text-sm text-white/50 transition-colors duration-200 hover:text-white">How It Works</Link></li>
              <li><Link href="#solutions" className="text-sm text-white/50 transition-colors duration-200 hover:text-white">Solutions</Link></li>
              <li><Link href="#architecture" className="text-sm text-white/50 transition-colors duration-200 hover:text-white">Architecture</Link></li>
            </ul>
          </div>
        </div>

        <div className="flex flex-col items-center justify-center gap-4 border-t border-white/5 pt-8 sm:flex-row">
          <div className="text-sm text-white/30">&copy; 2026 ENG4000 Group 27 Energy Expert.</div>
        </div>
      </div>
    </footer>
  );
}
