"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Upload } from "lucide-react";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    const sessionId = localStorage.getItem("session_id");
    if (sessionId) router.replace("/chat");
  }, []);

  return (
    <main className="min-h-screen bg-white text-black">
      {/* HERO */}
      <section className="mx-auto max-w-6xl px-6 pt-6 text-center">
        <h1 className="text-2xl md:text-5xl font-bold tracking-tight mb-4">
          Context-aware Document Q&A
          <span className="block">
            Built for Multi-turn Conversations
          </span>
        </h1>

        <p className="mx-auto max-w-2xl text-md text-gray-500 mb-8">
          ContextQA is a session-based conversational retrieval system that
          enables isolated document ingestion and accurate multi-turn querying
          using modern RAG techniques.
        </p>

        {/* UPLOAD */}
        <div className="flex justify-center">
          <button
            onClick={() => router.push("/upload")}
            className=" cursor-pointer
              group relative inline-flex items-center gap-3
              rounded-2xl px-8 py-4 text-sm font-semibold
              text-white
              bg-linear-to-r from-red-600 to-red-500
              shadow-lg shadow-red-500/30
              hover:from-red-500 hover:to-red-600
              hover:shadow-red-500/40
              transition-all duration-200">
            <Upload className="h-5 w-5 transition-transform group-hover:-translate-y-0.5" />
            Upload Documents
          </button>
        </div>
      </section>

      {/* FEATURES */}
      <section className="mx-auto max-w-6xl px-6 pb-24 pt-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            title="Session Isolation"
            description="Each session maintains its own document store and chat context, ensuring clean and independent retrieval pipelines."
          />

          <FeatureCard
            title="Contextual Question Rewriting"
            description="Follow-up questions are rewritten using conversation history to preserve intent across multi-turn interactions."
          />

          <FeatureCard
            title="MMR-based Retrieval"
            description="Maximal Marginal Relevance balances semantic relevance and diversity, reducing redundant context injection."
          />
        </div>
      </section>
    </main>
  );
}


function FeatureCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div
      className="
        rounded-2xl border border-gray-200 bg-white
        p-6 text-left
        hover:border-red-300 hover:shadow-md
        transition">
      <h3 className="text-lg font-semibold mb-2 text-black">
        {title}
      </h3>
      <p className="text-sm text-gray-600 leading-relaxed">
        {description}
      </p>
    </div>
  );
}
