export const thinkingMessages = [
  "Analyzing energy data locally...",
  "Validating query...",
  "Sending request to the backend...",
  "Checking schema and metrics...",
  "Reviewing returned rows...",
  "Processing your request...",
  "Calling the FastAPI service...",
  "Formatting the backend response...",
];

export const suggestedQuestions = [
  "What was the average power consumption last week?",
  "Show me the top 5 sites by energy usage this month",
  "List all site names and provinces",
  "Compare recent performance across major sites",
  "Are there any anomalies in yesterday's meter readings?",
  "Which sites use generators most often?",
];

export function getRandomThinkingMessage(): string {
  return thinkingMessages[Math.floor(Math.random() * thinkingMessages.length)];
}
