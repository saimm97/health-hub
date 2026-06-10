"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getAccess } from "@/lib/auth";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    router.replace(getAccess() ? "/dashboard" : "/login");
  }, [router]);
  return null;
}
