"use client";

import { useChat } from "@ai-sdk/react"
import { Chat } from "@/components/ui/chat";

export function ChatDemo() {
  const { messages, input, handleInputChange, handleSubmit, isLoading, stop } =
    useChat();

  return (
    <Chat
      messages={messages}
      input={input}
      handleInputChange={handleInputChange}
      handleSubmit={handleSubmit}
      isGenerating={isLoading}
      stop={stop}
    />
  );
}

// Ensure correct export
export default ChatDemo;
