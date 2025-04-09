// src/pages/Chatbot.tsx
import { useEffect, useRef } from 'react';
import { useChat } from '@ai-sdk/react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Send, Bot, User } from "lucide-react";
import { getCSRFToken } from "@/lib/cerfToken.ts";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';


export default function Chat() {
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const csrfToken = getCSRFToken() || '';
  const { messages, input, handleInputChange, handleSubmit, status, error } = useChat({
    api: "/api/chat/", // Use full URL for clarity
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    credentials: 'include',
    onResponse: (response) => {
      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));
      // Do NOT call response.text() here; it's already locked by useChat
    },
    onFinish: (message) => {
      console.log('Finished with message:', message);
      console.log('All messages:', messages);
    },
    onError: (err) => {
      console.error('Chat error:', err);
    },
  });

  // Scroll to bottom when new messages are added
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // Log messages and status for debugging
  useEffect(() => {
    console.log('Messages updated:', messages);
    console.log('Status:', status);
  }, [messages, status]);

  return (
    <div className="container mx-auto h-full w-full flex flex-col">
      <Card className="flex-1 flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            AI Chatbot
          </CardTitle>
        </CardHeader>
        <CardContent className=" flex flex-col gap-4 h-[65vh]">
          <ScrollArea className="h-[100%] pr-4" ref={scrollAreaRef}>

            {messages.length === 0 && status !== 'streaming' ? (
              <div className="text-center text-muted-foreground py-8">
                Start a conversation by typing a message below!
              </div>
            ) : messages.length === 0 && status === 'streaming' ? (
              <div className="text-center text-muted-foreground py-8">
                Thinking...
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 mb-4 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <Avatar>
                      <AvatarFallback>
                        <Bot className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                  )}
                  <div
                    className={`max-w-[70%] rounded-lg p-3 ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                    <div className="text-xs mt-1 opacity-70">
                      {new Date(message.createdAt || Date.now()).toLocaleTimeString()}
                    </div>
                  </div>
                  {message.role === 'user' && (
                    <Avatar>
                      <AvatarFallback>
                        <User className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                  )}
                </div>
              ))
            )}
            {error && (
              <div className="text-center text-red-500 py-4">
                Error: {error.message}
              </div>
            )}
          </ScrollArea>
          <div className={"flex flex-col w-[96%] items-center justify-center gap-2 absolute bottom-5"}>
          <form onSubmit={handleSubmit} className="flex gap-2 w-[80%]">
            <Input
              value={input}
              onChange={handleInputChange}
              placeholder="Type your message..."
              disabled={status === 'submitted'}
              className="flex-1"
            />
            <Button type="submit" disabled={status === 'submitted'}>
              <Send className="h-4 w-4" />
              <span className="sr-only">Send</span>
            </Button>
          </form>
          <p className="text-sm text-muted-foreground">Status: {status}</p>
            </div>
        </CardContent>
      </Card>
    </div>
  );
}