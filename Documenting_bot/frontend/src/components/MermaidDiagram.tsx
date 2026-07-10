"use client";

import { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

mermaid.initialize({
  startOnLoad: false,
  theme: "dark",
  themeVariables: {
    primaryColor: "#1B1E27",
    primaryTextColor: "#EDEBE6",
    primaryBorderColor: "#5EEAD4",
    lineColor: "#8B92A5",
    background: "#111318",
    mainBkg: "#1B1E27",
    nodeBorder: "#5EEAD4",
  },
});

export default function MermaidDiagram({ chart }: { chart: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const idRef = useRef(`mermaid-${Math.random().toString(36).slice(2)}`);

  useEffect(() => {
    let cancelled = false;

    mermaid
      .render(idRef.current, chart)
      .then(({ svg }) => {
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Failed to render diagram.");
      });

    return () => {
      cancelled = true;
    };
  }, [chart]);

  if (error) {
    return (
      <div className="text-sm text-red-400 bg-[#111318] border border-[#2C3040] rounded-lg p-4">
        Could not render diagram: {error}
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="my-4 flex justify-center bg-[#111318] border border-[#2C3040] rounded-lg p-6 overflow-x-auto"
    />
  );
}