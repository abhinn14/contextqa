"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Upload, FileText, Loader2, CheckCircle, XCircle, MessageSquare } from "lucide-react";

const UploadPage = () => {
  const router = useRouter();
  const api_url = process.env.NEXT_PUBLIC_API_URL;

  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const sessionId = localStorage.getItem("session_id");
    if(sessionId) router.replace("/chat");
  }, [router]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if(!e.target.files) return;
    setFiles(Array.from(e.target.files));
    setError(null);
  };

  const handleUpload = async () => {
    if(files.length === 0) {
      setError("Please select at least one file.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      files.forEach((file) => formData.append("files", file));

      const res = await fetch(`${api_url}/api/upload`, {
        method: "POST",
        body: formData,
      });

      if(!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Upload failed");
      }

      const data = await res.json();
      localStorage.setItem("session_id", data.session_id);
      setSuccess(true);
      setTimeout(() => {router.replace("/chat")}, 800);
    } catch (err: any) {
      setError(err.message || "Something went wrong in handleUpload");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-white px-6 py-6 text-black">
      <div className="mx-auto max-w-3xl">
        {/* Header */}
        <div className="mb-10 text-center">
          <h1 className="text-3xl md:text-4xl font-bold mb-3">
            Upload Documents
          </h1>
          <p className="text-gray-500">
            Upload one or more documents to start a new conversational session.
          </p>
        </div>

        {/* Upload Card */}
        <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
          {/* File Picker */}
          <label
            htmlFor="file-upload"
            className="
              flex flex-col items-center justify-center
              rounded-xl border-2 border-dashed border-gray-300
              px-6 py-12 text-center
              cursor-pointer hover:border-red-400 transition">
            <Upload className="h-8 w-8 text-red-500 mb-4" />
            <p className="font-medium">
              Click to upload or drag & drop
            </p>
            <p className="text-sm text-gray-500 mt-1">
              PDF, DOCX, TXT supported
            </p>

            <input
              id="file-upload"
              type="file"
              multiple
              className="hidden"
              onChange={handleFileChange}
            />
          </label>

          {/* Selected Files */}
          {files.length > 0 && (
            <div className="mt-6 space-y-2">
              {files.map((file, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-3 rounded-lg border px-4 py-2 text-sm"
                >
                  <FileText className="h-4 w-4 text-gray-500" />
                  <span className="truncate">{file.name}</span>
                </div>
              ))}
            </div>
          )}

          {/* Status */}
          {error && (
            <div className="mt-4 flex items-center gap-2 text-sm text-red-600">
              <XCircle className="h-4 w-4" />
              {error}
            </div>
          )}

          {success && (
            <div className="mt-4 flex items-center gap-2 text-sm text-green-600">
              <CheckCircle className="h-4 w-4" />
              Indexing complete. Redirecting…
            </div>
          )}

          {/* Action */}
          <div className="mt-8 flex justify-end">
            <button
              onClick={handleUpload}
              disabled={loading}
              className="cursor-pointer
                inline-flex items-center gap-2
                rounded-xl px-6 py-3 text-sm font-semibold
                text-white
                bg-linear-to-r from-red-600 to-red-500
                hover:from-red-500 hover:to-red-600
                disabled:opacity-60
                transition">
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Loading...
                </>
              ) : (
                <>
                  <MessageSquare className="h-4 w-4" />
                  Start Chatting
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </main>
  );
};

export default UploadPage;
