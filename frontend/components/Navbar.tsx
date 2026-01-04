"use client";

import Link from "next/link";
import { Upload } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";

const Navbar = () => {
  const router = useRouter();
  const pathname = usePathname();

  const handleUploadClick = () => {
    localStorage.removeItem("session_id");
    router.push("/upload");
  };

  return (
    <nav className="relative sticky top-0 z-50 h-20 bg-white/85 backdrop-blur-xl border-b border-white/50 shadow-[0_10px_40px_-30px_rgba(0,0,0,0.55)]">
      <span
        aria-hidden
        className="pointer-events-none absolute inset-x-4 bottom-0 h-[2px] rounded-full bg-linear-to-r from-orange-400/0 via-orange-500/75 to-orange-400/0 blur-[1px]"
      />
      <div className="container mx-auto relative grid h-full grid-cols-[1fr_auto_1fr] items-center px-4">
        {/* LOGO */}
        <Link
          href="/"
          className="
            col-start-2 flex items-center justify-center gap-1
            text-center font-extrabold tracking-tight
            text-2xl md:text-4xl">
          <span className="bg-linear-to-r from-red-700 to-red-400 bg-clip-text text-transparent">
            Context
          </span>
          <span className="text-gray-900">QA</span>
        </Link>
        {pathname === "/chat" && (
          <button
            onClick={handleUploadClick}
            className="cursor-pointer justify-self-end
              group relative inline-flex items-center gap-2
              rounded-xl px-5 py-3 text-sm font-semibold
              text-white
              bg-linear-to-r from-red-600 to-red-500
              shadow-lg shadow-red-500/30
              hover:from-red-500 hover:to-red-600
              hover:shadow-red-500/40
              transition-all duration-200">
            <Upload className="h-4 w-4 transition-transform group-hover:-translate-y-0.5" />
            Upload New Documents
          </button>
        )}
      </div>
    </nav>
  )
}

export default Navbar;
