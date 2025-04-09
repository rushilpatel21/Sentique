import { request } from "@/auth/allAuth";
import {getCSRFToken} from "@/lib/cerfToken.ts"; // Adjust path and extension as needed

const BASE_URL = "/api";

export const URLs: Record<string, string> = Object.freeze({
  CHAT: BASE_URL + '/chat/',
});

// Define the expected data shape
interface ChatData {
  id: string;
  messages: Array<{ role: string; content: string; parts: Array<{ type: string; text: string }> }>;
}

// Custom fetch function compatible with useChat
export async function chat(url: string, options: RequestInit = {}): Promise<Response> {
  const csrfToken = getCSRFToken(); // Assuming you have this utility

  const chatData: ChatData = options.body ? JSON.parse(options.body as string) : { id: "", messages: [] };

  const modifiedOptions: RequestInit = {
    ...options,
    method: 'POST',
    headers: {
      ...options.headers,
      'X-CSRFToken': csrfToken,
      'Content-Type': 'application/json',
    },
    credentials: 'include', // Include cookies
    body: JSON.stringify(chatData),
  };

  return await fetch(URLs.CHAT, modifiedOptions); // Use fetch directly, or adapt request
}
