"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Send, Loader2, Bot, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import remarkGfm from "remark-gfm";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

const Chat = () => {
  const api_url = process.env.NEXT_PUBLIC_API_URL;
  const router = useRouter();

  const formatAssistantContent = (content: string) => {
    return content
      .replace(/\\\(/g, "$")
      .replace(/\\\)/g, "$")
      .replace(/\(([^()]*\\bmod[^()]*)\)/g, (_match, expr) => `$${expr}$`);
  };

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; content: string }[]>([]);
  const [loading, setLoading] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const sid = localStorage.getItem("session_id");
    if(!sid) {
      router.push("/");
      return;
    }
    setSessionId(sid);
  }, [router]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    if (!message.trim() || !sessionId || loading) return;

    const userMessage = message.trim();
    setMessage("");

    setMessages((prev) => [
      ...prev,
      { role: "user", content: userMessage },
    ]);

    setLoading(true);

    try {
      const res = await fetch(`${api_url}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: userMessage,
        }),
      });

      if(!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Chat failed");
      }

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            err.message ||
            "Something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
  <main className="h-[calc(100vh-5rem)] bg-white text-black overflow-hidden">
    <div className="mx-auto flex h-full max-w-4xl flex-col">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b bg-white px-6 py-4 font-semibold">
        ContextQA ChatBot
      </header>

      {/* Messages (SCROLLABLE) */}
      <div
        className="
          flex-1 overflow-y-auto px-6 py-6 space-y-6
          scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent
        "
      >
        {messages.length === 0 && (
          <div className="mt-24 text-center text-gray-400">
            Ask a question about your uploaded documents
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-end gap-3 ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {/* Assistant Icon */}
            {msg.role === "assistant" && (
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-red-100">
                <Bot className="h-4 w-4 text-red-600" />
              </div>
            )}

            {/* Bubble */}
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
                msg.role === "user"
                  ? "bg-red-600 text-white rounded-br-md"
                  : "bg-gray-100 text-black rounded-bl-md"
              }`}
            >
              {msg.role === "assistant" ? (
                <div className="markdown-content">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm, remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                    components={{
                      a: ({ node, ...props }) => (
                        <a {...props} target="_blank" rel="noreferrer" />
                      ),
                    }}
                  >
                    {formatAssistantContent(msg.content)}
                  </ReactMarkdown>
                </div>
              ) : (
                msg.content
              )}
            </div>

            {/* User Icon */}
            {msg.role === "user" && (
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-200">
                <User className="h-4 w-4 text-gray-600" />
              </div>
            )}
          </div>
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="flex items-end gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-red-100">
              <Bot className="h-4 w-4 text-red-600" />
            </div>
            <div className="rounded-2xl bg-gray-100 px-4 py-3 shadow-sm">
              <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input (STICKY) */}
      <div className="sticky bottom-0 border-t bg-white px-6 py-4">
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask a question..."
            className="
              flex-1 rounded-xl border px-4 py-3 text-sm
              focus:outline-none focus:ring-2 focus:ring-red-500
            "
          />
          <button
            onClick={sendMessage}
            disabled={loading}
            className="cursor-pointer
              flex h-11 w-11 items-center justify-center
              rounded-xl bg-red-600 text-white
              hover:bg-red-500 disabled:opacity-60
              transition">
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  </main>
);

};

export default Chat;
