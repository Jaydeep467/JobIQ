"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type User = {
  id: number;
  email: string;
  full_name: string;
  created_at: string;
};

export default function DashboardPage() {
  const router = useRouter();

  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCurrentUser() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        router.push("/login");
        return;
      }

      try {
        const response = await fetch("http://127.0.0.1:8000/auth/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          localStorage.removeItem("access_token");
          router.push("/login");
          return;
        }

        const data = await response.json();
        setUser(data);
      } catch (error) {
        console.error("Could not load current user:", error);
      } finally {
        setLoading(false);
      }
    }

    loadCurrentUser();
  }, [router]);

  function handleLogout() {
    localStorage.removeItem("access_token");
    router.push("/login");
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p>Loading your dashboard...</p>
      </main>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <main className="min-h-screen px-6 py-10">
      <div className="mx-auto max-w-5xl">
        <header className="flex items-center justify-between border-b border-gray-200 pb-6">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">
              JobIQ
            </p>

            <h1 className="mt-2 text-3xl font-bold">
              Welcome, {user.full_name}
            </h1>
          </div>

          <button
            onClick={handleLogout}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-semibold transition hover:bg-gray-100"
          >
            Log out
          </button>
        </header>

        <section className="mt-10 rounded-xl border border-gray-200 p-6 shadow-sm">
          <h2 className="text-xl font-semibold">Your dashboard</h2>

          <p className="mt-2 text-gray-600">
            Your JobIQ workspace is ready.
          </p>

          <div className="mt-6 rounded-lg bg-gray-50 p-4">
            <p className="text-sm text-gray-500">Signed in as</p>
            <p className="mt-1 font-medium">{user.email}</p>
          </div>
        </section>
      </div>
    </main>
  );
}