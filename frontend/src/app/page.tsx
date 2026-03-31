"use client";

import Header from "@/components/Header";
import EnergyHero from "@/components/EnergyHero";
import ProblemStatement from "@/components/ProblemStatement";
import EnergyFeatureCards from "@/components/EnergyFeatureCards";
import IntroducingSystem from "@/components/IntroducingSystem";
import HowItWorks from "@/components/HowItWorks";
import TrustIntegrity from "@/components/TrustIntegrity";
import ResultsSection from "@/components/ResultsSection";
import NewRootOfTrust from "@/components/NewRootOfTrust";
import EnergySolutions from "@/components/EnergySolutions";
import FinalCTA from "@/components/FinalCTA";
import EnergyFooter from "@/components/EnergyFooter";
import ChatInterface from "@/components/ChatInterface";
import { ChatProvider, useChat } from "@/lib/ChatContext";

function PageContent() {
  const { isChatOpen, closeChat } = useChat();

  return (
    <>
      <Header />
      <EnergyHero />
      <ProblemStatement />
      <EnergyFeatureCards />
      <IntroducingSystem />
      <HowItWorks />
      <TrustIntegrity />
      <ResultsSection />
      <NewRootOfTrust />
      <EnergySolutions />
      <FinalCTA />
      <EnergyFooter />
      <ChatInterface isOpen={isChatOpen} onClose={closeChat} />
    </>
  );
}

export default function Home() {
  return (
    <ChatProvider>
      <main className="min-h-[100dvh] bg-[#0d0d0d]">
        <PageContent />
      </main>
    </ChatProvider>
  );
}
