"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import logoImage from "@/app/PLCAI-logo.webp";
import { useChat } from "@/lib/ChatContext";

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { openChat } = useChat();

  return (
    <header className="fixed left-0 right-0 top-0 z-50">
      <div className="border-b border-white/5 bg-[#0d0d0d]/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 sm:py-5 lg:px-8">
          <Link href="/" className="group flex items-center gap-3">
            <Image
              src={logoImage}
              alt="PLCAI"
              className="h-10 w-auto transition-transform duration-300 group-hover:scale-105 sm:h-12"
              width={120}
              height={48}
              priority
            />
          </Link>

          <nav className="hidden items-center gap-1 lg:flex">
            <a href="#features" className="rounded-lg px-4 py-2 text-sm text-white/70 transition-all duration-200 hover:bg-white/5 hover:text-white">Features</a>
            <a href="#how-it-works" className="rounded-lg px-4 py-2 text-sm text-white/70 transition-all duration-200 hover:bg-white/5 hover:text-white">How It Works</a>
            <a href="#solutions" className="rounded-lg px-4 py-2 text-sm text-white/70 transition-all duration-200 hover:bg-white/5 hover:text-white">Solutions</a>
            <a href="#architecture" className="rounded-lg px-4 py-2 text-sm text-white/70 transition-all duration-200 hover:bg-white/5 hover:text-white">Architecture</a>
          </nav>

          <div className="flex items-center gap-4">
            <button
              onClick={openChat}
              className="hidden items-center gap-2 rounded-full bg-gradient-to-r from-[#5EEAD4] to-[#14b8a6] px-5 py-2.5 text-sm font-medium text-black transition-all duration-300 hover:shadow-[0_0_20px_rgba(94,234,212,0.4)] sm:flex"
            >
              <span className="h-2 w-2 rounded-full bg-black" />
              Open Query
            </button>

            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="flex h-10 w-10 flex-col items-center justify-center gap-1.5 rounded-lg transition-colors hover:bg-white/5 lg:hidden"
              aria-label="Toggle menu"
            >
              <span className={`h-0.5 w-5 bg-white transition-all duration-300 ${isMenuOpen ? "translate-y-2 rotate-45" : ""}`} />
              <span className={`h-0.5 w-5 bg-white transition-all duration-300 ${isMenuOpen ? "opacity-0" : ""}`} />
              <span className={`h-0.5 w-5 bg-white transition-all duration-300 ${isMenuOpen ? "-translate-y-2 -rotate-45" : ""}`} />
            </button>
          </div>
        </div>
      </div>

      <div className={`overflow-hidden transition-all duration-300 lg:hidden ${isMenuOpen ? "max-h-96" : "max-h-0"}`}>
        <div className="border-b border-white/5 bg-[#0d0d0d]/95 backdrop-blur-xl">
          <nav className="flex flex-col space-y-1 px-6 py-4">
            <a href="#features" className="rounded-lg px-4 py-3 text-white/70 transition-all hover:bg-white/5 hover:text-white">Features</a>
            <a href="#how-it-works" className="rounded-lg px-4 py-3 text-white/70 transition-all hover:bg-white/5 hover:text-white">How It Works</a>
            <a href="#solutions" className="rounded-lg px-4 py-3 text-white/70 transition-all hover:bg-white/5 hover:text-white">Solutions</a>
            <a href="#architecture" className="rounded-lg px-4 py-3 text-white/70 transition-all hover:bg-white/5 hover:text-white">Architecture</a>
            <div className="pt-4">
              <button
                onClick={() => {
                  openChat();
                  setIsMenuOpen(false);
                }}
                className="flex w-full items-center justify-center gap-2 rounded-full bg-gradient-to-r from-[#5EEAD4] to-[#14b8a6] px-5 py-3 text-sm font-medium text-black"
              >
                <span className="h-2 w-2 rounded-full bg-black" />
                Open Query
              </button>
            </div>
          </nav>
        </div>
      </div>
    </header>
  );
}
