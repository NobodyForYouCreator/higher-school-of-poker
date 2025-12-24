import React from "react";

export default function Input({
  className,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={["input", className].filter(Boolean).join(" ")} />;
}

