// Utility helpers for the frontend
// `cn` composes class names using `clsx` then merges Tailwind classes with `tailwind-merge`.
import clsx from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: any[]) {
  return twMerge(clsx(...inputs))
}

export default cn
