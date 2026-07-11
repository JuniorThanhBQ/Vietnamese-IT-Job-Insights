import { useState, useCallback } from 'react';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState(null);

  const sendMessage = useCallback(
    async (content) => {
      if (!content.trim()) return;

      setError(null);
      setStreaming(true);

      const userMsg = { role: 'user', content };
      const currentMessages = [...messages, userMsg];
      setMessages(currentMessages);

      // Map history to backend expected structure (role: "user" | "model")
      const history = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      try {
        const response = await fetch('/api/v1/jobs/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: content,
            history,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');

        // Append an empty model message placeholder
        const modelMsgPlaceholder = { role: 'model', content: '' };
        setMessages((prev) => [...prev, modelMsgPlaceholder]);

        let accumulatedContent = '';
        let buffer = '';

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');

          // Save the last incomplete line back to the buffer
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('data: ')) {
              const dataStr = trimmed.slice(6);
              try {
                const parsed = JSON.parse(dataStr);
                if (parsed.text) {
                  accumulatedContent += parsed.text;

                  // Update the last message in state
                  setMessages((prev) => {
                    const updated = [...prev];
                    if (updated.length > 0) {
                      updated[updated.length - 1] = {
                        role: 'model',
                        content: accumulatedContent,
                      };
                    }
                    return updated;
                  });
                }
              } catch {
                // Ignore partial or invalid JSON lines in the buffer
              }
            }
          }
        }
      } catch (err) {
        setError(err.message || 'Failed to communicate with the assistant.');
        // Remove the last model message placeholder if it was empty
        setMessages((prev) => {
          const updated = [...prev];
          if (updated.length > 0 && updated[updated.length - 1].content === '') {
            updated.pop();
          }
          return updated;
        });
      } finally {
        setStreaming(false);
      }
    },
    [messages]
  );

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
    setStreaming(false);
  }, []);

  return { messages, streaming, error, sendMessage, clearChat };
}
