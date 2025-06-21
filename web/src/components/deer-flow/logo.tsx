// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import Image from "next/image";
import Link from "next/link";
import { cn } from "~/lib/utils";

export function LogoIcon({ className }: { className?: string }) {
  return (
    <Image
      className={cn(className)}
      src="/logo-p.png"
      alt="Logo"
      width={36}
      height={36}
      style={{ objectFit: "contain" }}
      priority
    />
  );
}

export function Logo() {
  return (
    <Link
      className="flex items-center gap-2 opacity-70 transition-opacity duration-300 hover:opacity-100"
      href="/"
    >
      <LogoIcon />
      <span className="text-lg font-bold">DeerFlow</span>
    </Link>
  );
}
