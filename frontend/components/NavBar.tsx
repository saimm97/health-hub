"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { logout } from "@/lib/auth";

const LINKS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/coach", label: "AI Coach" },
];

export default function NavBar() {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    logout();
    router.push("/login");
  }

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-2 font-semibold text-brand-700">
          <span className="inline-grid place-items-center w-8 h-8 rounded-lg bg-brand-600 text-white">H</span>
          HealthHub
        </Link>
        <nav className="flex items-center gap-1 text-sm font-medium">
          {LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`px-3 py-2 rounded-lg hover:bg-slate-100 ${
                pathname === l.href ? "text-brand-700 bg-brand-50" : ""
              }`}
            >
              {l.label}
            </Link>
          ))}
          <button
            onClick={handleLogout}
            className="ml-2 text-sm px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-100"
          >
            Log out
          </button>
        </nav>
      </div>
    </header>
  );
}
