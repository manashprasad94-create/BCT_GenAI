"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import MermaidDiagram from "@/components/MermaidDiagram";

export default function ResultPage() {
  const [doc, setDoc] = useState<string>("");
  const [fileCount, setFileCount] = useState<number>(0);
  const router = useRouter();

  useEffect(() => {
    const stored = sessionStorage.getItem("autodocs_result");
    if (!stored) {
      router.push("/");
      return;
    }
    const parsed = JSON.parse(stored);
    setDoc(parsed.documentation || "");
    setFileCount(parsed.file_count || 0);
  }, [router]);

  const handleDownload = () => {
    const blob = new Blob([doc], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "DOCUMENTATION.md";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <main className="min-h-screen bg-[#111318] px-4 py-10">
      <div className="max-w-3xl mx-auto bg-[#1B1E27] border border-[#2C3040] rounded-2xl shadow-xl p-8">
        <div className="flex items-center justify-between mb-6 pb-6 border-b border-[#2C3040]">
          <div>
            <h1 className="text-xl font-semibold text-[#EDEBE6]">Generated Documentation</h1>
            <p className="text-sm text-[#5EEAD4] mt-1">{fileCount} files analyzed</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleDownload}
              className="bg-[#F0B429] text-[#111318] text-sm rounded-lg px-4 py-2 font-semibold hover:bg-[#f5c04d] transition-colors"
            >
              Download .md
            </button>
            <button
              onClick={() => router.push("/")}
              className="bg-[#2C3040] text-[#EDEBE6] text-sm rounded-lg px-4 py-2 font-medium hover:bg-[#353a4d] transition-colors"
            >
              New Project
            </button>
          </div>
        </div>

        <article className="prose prose-invert prose-sm max-w-none
                             prose-headings:text-[#EDEBE6]
                             prose-p:text-[#c7c9d1]
                             prose-a:text-[#5EEAD4]
                             prose-code:text-[#F0B429]
                             prose-strong:text-[#EDEBE6]">
          <ReactMarkdown
            components={{
              code({ className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || "");
                const language = match?.[1];

                if (language === "mermaid") {
                  return <MermaidDiagram chart={String(children).trim()} />;
                }

                return (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              },
            }}
          >
            {doc}
          </ReactMarkdown>
        </article>
      </div>
    </main>
  );
}