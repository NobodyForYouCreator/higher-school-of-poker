import React from "react";

export type ButtonVariant = "primary" | "danger" | "ghost" | "default";
export type ButtonSize = "sm" | "md";

export default function Button({
  variant = "default",
  size = "md",
  className,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
}) {
  const classes = ["btn", `btn-${variant}`, `btn-${size}`, className].filter(Boolean).join(" ");
  return <button {...props} className={classes} />;
}

