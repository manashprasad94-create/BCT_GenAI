"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const [zipFile, setZipFile] = useState<File | null>(null);
  const [githubUrl, setGithubUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async () => {
    setError("");

    if (!zipFile && !githubUrl.trim()) {
      setError("Upload a zip file or paste a GitHub URL.");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    if (zipFile) formData.append("zip_file", zipFile);
    if (githubUrl.trim()) formData.append("github_url", githubUrl.trim());

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/generate-docs`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Something went wrong.");
      }

      const data = await res.json();
      sessionStorage.setItem("autodocs_result", JSON.stringify(data));
      router.push("/result");
    } catch (err: any) {
      setError(err.message || "Failed to generate documentation.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 bg-[#111318]">
      <div className="w-full max-w-xl bg-[#1B1E27] border border-[#2C3040] rounded-2xl shadow-xl p-8 space-y-6">
        <div>
          <div className="inline-flex items-center gap-2 mb-2">
            <span className="w-2 h-2 rounded-full bg-[#F0B429]" />
            <span className="text-xs uppercase tracking-widest text-[#8B92A5]">Documentation Generator</span>
          </div>
          <h1 className="text-2xl font-semibold text-[#EDEBE6]">AutoDocs</h1>
          <p className="text-[#8B92A5] mt-1 text-sm">
            Upload a project or paste a GitHub link. Get full documentation, generated automatically.
          </p>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-[#EDEBE6]">Upload a .zip file</label>
          <input
            type="file"
            accept=".zip"
            onChange={(e) => setZipFile(e.target.files?.[0] || null)}
            className="block w-full text-sm text-[#EDEBE6] bg-[#111318] border border-[#2C3040] rounded-lg cursor-pointer p-2
                       file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0
                       file:bg-[#2C3040] file:text-[#EDEBE6] file:text-sm"
          />
        </div>

        <div className="flex items-center gap-3 text-[#8B92A5] text-xs">
          <div className="flex-1 h-px bg-[#2C3040]" />
          OR
          <div className="flex-1 h-px bg-[#2C3040]" />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-[#EDEBE6]">GitHub repository URL</label>
          <input
            type="text"
            placeholder="https://github.com/username/repo"
            value={githubUrl}
            onChange={(e) => setGithubUrl(e.target.value)}
            className="block w-full text-sm text-[#EDEBE6] placeholder-[#8B92A5] bg-[#111318]
                       border border-[#2C3040] rounded-lg p-2.5 outline-none
                       focus:border-[#5EEAD4] transition-colors"
          />
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full bg-[#F0B429] text-[#111318] rounded-lg py-2.5 font-semibold
                     disabled:opacity-50 hover:bg-[#f5c04d] transition-colors"
        >
          {loading ? "Generating documentation..." : "Generate Documentation"}
        </button>

        {loading && (
          <p className="text-xs text-[#8B92A5] text-center">
            This can take 20–60 seconds depending on project size.
          </p>
        )}
      </div>
    </main>
  );
}