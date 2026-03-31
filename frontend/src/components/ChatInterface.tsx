"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import logoImage from "@/app/PLCAI-logo.webp";
import { fetchBackendHealth, queryEnergyExpert } from "@/lib/api";
import { getRandomThinkingMessage, suggestedQuestions } from "@/lib/demoData";
import type { QueryResponse } from "@/lib/types";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sqlQuery?: string;
  rows?: Record<string, unknown>[];
}

interface ChatInterfaceProps {
  isOpen: boolean;
  onClose: () => void;
}

function summarizeRows(rows: Record<string, unknown>[]) {
  if (rows.length === 0) {
    return "No rows returned";
  }

  if (rows.length === 1) {
    return "1 row returned";
  }

  return `${rows.length} rows returned`;
}

function formatCellValue(value: unknown) {
  if (value === null || value === undefined) {
    return "null";
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

function buildAssistantMessage(response: QueryResponse): Message {
  return {
    id: `${Date.now()}-assistant`,
    role: "assistant",
    content: response.analysis,
    timestamp: new Date(),
    sqlQuery: response.sql,
    rows: response.rows,
  };
}

export default function ChatInterface({ isOpen, onClose }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [thinkingMessage, setThinkingMessage] = useState("Sending request to the backend...");
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    let isMounted = true;
    setBackendStatus("checking");

    fetchBackendHealth()
      .then(() => {
        if (isMounted) {
          setBackendStatus("online");
        }
      })
      .catch(() => {
        if (isMounted) {
          setBackendStatus("offline");
        }
      });

    return () => {
      isMounted = false;
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  useEffect(() => {
    if (!isLoading) {
      return;
    }

    const interval = setInterval(() => {
      setThinkingMessage(getRandomThinkingMessage());
    }, 900);

    return () => clearInterval(interval);
  }, [isLoading]);

  const handleSend = async (question = input.trim()) => {
    if (!question || isLoading) {
      return;
    }

    const userMessage: Message = {
      id: `${Date.now()}-user`,
      role: "user",
      content: question,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setThinkingMessage(getRandomThinkingMessage());

    try {
      const response = await queryEnergyExpert(question);
      setMessages((prev) => [...prev, buildAssistantMessage(response)]);
      setBackendStatus("online");
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "The backend request failed.";

      setMessages((prev) => [
        ...prev,
        {
          id: `${Date.now()}-error`,
          role: "assistant",
          content: `Request failed. ${message}`,
          timestamp: new Date(),
        },
      ]);
      setBackendStatus("offline");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    setInput(question);
    inputRef.current?.focus();
  };

  if (!isOpen) {
    return null;
  }

  const statusClasses =
    backendStatus === "online"
      ? "bg-[#5EEAD4]/10 border-[#5EEAD4]/30 text-[#5EEAD4]"
      : backendStatus === "offline"
        ? "bg-[#f97316]/10 border-[#f97316]/30 text-[#fdba74]"
        : "bg-white/5 border-white/10 text-white/60";

  const statusDotClass =
    backendStatus === "online"
      ? "bg-[#5EEAD4]"
      : backendStatus === "offline"
        ? "bg-[#f97316]"
        : "bg-white/50";

  const statusText =
    backendStatus === "online"
      ? "Backend online"
      : backendStatus === "offline"
        ? "Backend unavailable"
        : "Checking backend";

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center">
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />

      <div className="relative flex h-full w-full flex-col overflow-hidden border border-white/10 bg-[#0d0d0d] shadow-2xl md:h-[90%] md:max-h-[860px] md:w-[90%] md:max-w-6xl md:rounded-2xl">
        <div className="flex items-center justify-between border-b border-white/10 bg-[#0d0d0d] px-6 py-4">
          <div className="flex items-center gap-3">
            <Image src={logoImage} alt="PLCAI" className="h-8 w-auto sm:h-10" width={100} height={40} />
            <div>
              <h2 className="text-sm font-semibold text-white">ENG4000 Group 27 Query Workspace</h2>
              <p className="text-xs text-white/50">FastAPI-backed energy analytics interface</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className={`flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium ${statusClasses}`}>
              <span className={`h-2 w-2 rounded-full ${statusDotClass}`} />
              <span>{statusText}</span>
            </div>

            <button onClick={onClose} className="flex h-10 w-10 items-center justify-center rounded-lg transition-colors hover:bg-white/5" aria-label="Close query workspace">
              <svg className="h-5 w-5 text-white/60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
          {messages.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center px-4 text-center">
              <Image src={logoImage} alt="PLCAI" className="mb-6 h-16 w-auto" width={160} height={64} />
              <h3 className="mb-2 text-2xl font-light text-white">Ask the backend about your energy data</h3>
              <p className="mb-3 max-w-md text-white/50">
                This interface sends your question to the real Group 27 FastAPI backend and displays the returned analysis, SQL, and result rows.
              </p>
              <p className="mb-8 max-w-md text-sm text-white/35">
                If the backend is offline, start FastAPI on port 8000 before submitting a query.
              </p>

              <div className="grid w-full max-w-2xl grid-cols-1 gap-3 sm:grid-cols-2">
                {suggestedQuestions.map((question) => (
                  <button
                    key={question}
                    onClick={() => handleSuggestedQuestion(question)}
                    className="group rounded-xl border border-white/10 bg-white/5 p-4 text-left transition-all duration-200 hover:border-[#5EEAD4]/30 hover:bg-white/10"
                  >
                    <p className="text-sm text-white/80 transition-colors group-hover:text-white">{question}</p>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="mx-auto max-w-4xl space-y-6">
              {messages.map((message) => {
                const columns = message.rows && message.rows.length > 0 ? Object.keys(message.rows[0]) : [];

                return (
                  <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[88%] ${message.role === "user" ? "order-2" : ""}`}>
                      <div className={`flex gap-3 ${message.role === "user" ? "flex-row-reverse" : ""}`}>
                        {message.role === "user" ? (
                          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-white/10">
                            <svg className="h-4 w-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
                            </svg>
                          </div>
                        ) : (
                          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg border border-[#5EEAD4]/20 bg-[#5EEAD4]/10">
                            <svg className="h-4 w-4 text-[#5EEAD4]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 17L8.25 21m7.5-4l1.5 4m-9-13.5h7.5m-9.75 0h12a1.5 1.5 0 011.5 1.5v6a1.5 1.5 0 01-1.5 1.5h-12a1.5 1.5 0 01-1.5-1.5v-6a1.5 1.5 0 011.5-1.5z" />
                            </svg>
                          </div>
                        )}

                        <div className={`rounded-2xl px-4 py-3 ${message.role === "user" ? "bg-[#5EEAD4] text-black" : "border border-white/10 bg-[#1a1a1a]"}`}>
                          <div className={`whitespace-pre-wrap text-sm leading-relaxed ${message.role === "user" ? "text-black" : "text-white/90"}`}>
                            {message.content}
                          </div>

                          {message.role === "assistant" ? (
                            <div className="mt-3 flex items-center gap-2 border-t border-white/10 pt-3">
                              <button
                                onClick={() => navigator.clipboard.writeText(message.content)}
                                className="rounded-lg p-2 text-white/40 transition-colors hover:bg-white/10 hover:text-white/70"
                                title="Copy analysis"
                              >
                                <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                  <path strokeLinecap="round" strokeLinejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184" />
                                </svg>
                              </button>
                            </div>
                          ) : null}
                        </div>
                      </div>

                      {message.role === "assistant" && message.sqlQuery ? (
                        <div className="mt-3 space-y-3">
                          <details className="group">
                            <summary className="flex cursor-pointer items-center gap-2 text-xs text-white/40 transition-colors hover:text-white/60">
                              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" />
                              </svg>
                              View generated SQL
                            </summary>
                            <div className="mt-2 overflow-x-auto rounded-lg border border-white/5 bg-[#0a0a0a] p-3 font-mono text-xs text-[#5EEAD4]">
                              <pre>{message.sqlQuery}</pre>
                            </div>
                          </details>

                          <div className="rounded-2xl border border-white/10 bg-[#111111] p-4">
                            <div className="mb-3 flex items-center justify-between gap-3">
                              <h4 className="text-sm font-medium text-white">Returned rows</h4>
                              <span className="text-xs text-white/40">{summarizeRows(message.rows ?? [])}</span>
                            </div>

                            {message.rows && message.rows.length > 0 ? (
                              <div className="overflow-x-auto">
                                <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
                                  <thead>
                                    <tr>
                                      {columns.map((column) => (
                                        <th key={column} className="border-b border-white/10 px-3 py-2 text-xs font-medium uppercase tracking-[0.12em] text-white/40">
                                          {column}
                                        </th>
                                      ))}
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {message.rows.map((row, rowIndex) => (
                                      <tr key={`${message.id}-row-${rowIndex}`}>
                                        {columns.map((column) => (
                                          <td key={`${message.id}-${rowIndex}-${column}`} className="border-b border-white/5 px-3 py-2 align-top text-white/75">
                                            {formatCellValue(row[column])}
                                          </td>
                                        ))}
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            ) : (
                              <p className="text-sm text-white/50">
                                The backend completed the request, but no rows were returned for this question.
                              </p>
                            )}
                          </div>
                        </div>
                      ) : null}
                    </div>
                  </div>
                );
              })}

              {isLoading ? (
                <div className="flex justify-start">
                  <div className="rounded-2xl border border-white/10 bg-[#1a1a1a] px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="flex gap-1">
                        <span className="h-2 w-2 animate-bounce rounded-full bg-[#5EEAD4]" style={{ animationDelay: "0ms" }} />
                        <span className="h-2 w-2 animate-bounce rounded-full bg-[#5EEAD4]" style={{ animationDelay: "150ms" }} />
                        <span className="h-2 w-2 animate-bounce rounded-full bg-[#5EEAD4]" style={{ animationDelay: "300ms" }} />
                      </div>
                      <span className="min-w-[220px] text-sm text-white/50 transition-opacity duration-300">{thinkingMessage}</span>
                    </div>
                  </div>
                </div>
              ) : null}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div className="border-t border-white/10 bg-[#0d0d0d] p-4">
          <div className="mx-auto max-w-4xl">
            <div className="flex items-end gap-3 rounded-2xl border border-white/10 bg-[#1a1a1a] p-3 transition-colors focus-within:border-[#5EEAD4]/50">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a natural-language question for the backend..."
                rows={1}
                className="max-h-32 flex-1 resize-none bg-transparent text-sm text-white outline-none placeholder:text-white/40"
                style={{ minHeight: "24px" }}
              />
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl transition-all duration-200 ${
                  input.trim() && !isLoading
                    ? "bg-gradient-to-r from-[#5EEAD4] to-[#14b8a6] text-black"
                    : "cursor-not-allowed bg-white/10 text-white/30"
                }`}
                aria-label="Send query"
              >
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                </svg>
              </button>
            </div>
            <p className="mt-3 text-center text-xs text-white/30">
              The frontend mirrors the backend contract directly. Start the FastAPI server on port 8000 before querying.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
